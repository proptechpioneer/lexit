from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.db import transaction
from honeypot.decorators import check_honeypot
from .security_utils import check_honeypot_with_logging
from .forms import SimpleUserCreationForm, UserProfileForm, ExtendedUserProfileForm
from .models import UserProfile
from .activecampaign import sync_contact, notify_referrer_of_signup, build_referred_user_identifier
import datetime
import logging


logger = logging.getLogger(__name__)

# Create your views here.


def _normalize_ref_token(value):
    return ''.join(ch for ch in (value or '').upper() if ch.isalnum())


def _find_referrer_profile(referral_code):
    normalized_ref = _normalize_ref_token(referral_code)
    if not normalized_ref:
        return None

    # Attribute referrals only by the explicit referral code to avoid false matches.
    return UserProfile.objects.select_related('user').filter(
        referral_code__iexact=normalized_ref,
        can_refer=True,
    ).first()


def _notify_referrer_by_email(referrer_user, referred_user, referral_code=None):
    """Notify the referrer without exposing referred-user contact details."""
    if not getattr(referrer_user, 'email', ''):
        return {'success': False, 'reason': 'missing_referrer_email'}

    referred_identifier = build_referred_user_identifier(referred_user)
    context = {
        'referrer_user': referrer_user,
        'referred_identifier': referred_identifier,
        'referral_code': referral_code or '',
        'current_year': datetime.datetime.now().year,
    }

    try:
        html_message = render_to_string('users/referrer_notification_email.html', context)
        plain_message = render_to_string('users/referrer_notification_email.txt', context)

        send_mail(
            subject='LEXIT referral update: a new member joined via your link',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[referrer_user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return {'success': True, 'referred_identifier': referred_identifier}
    except Exception as exc:
        logger.warning(
            "Referrer notification email failed: referrer=%s reason=%s",
            referrer_user.email,
            str(exc),
        )
        return {'success': False, 'reason': str(exc)}

@login_required
def profile_view(request):
    """View and edit user profile"""
    # Ensure user has a profile
    if not hasattr(request.user, 'profile'):
        UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ExtendedUserProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ExtendedUserProfileForm(instance=request.user.profile)
    
    can_refer = bool(getattr(request.user.profile, 'can_refer', False))
    referral_signup_url = None
    referral_landing_url = None

    if can_refer and request.user.profile.referral_code:
        referral_signup_url = request.build_absolute_uri(
            f"{reverse('users:register')}?ref={request.user.profile.referral_code}"
        )
        referral_landing_url = request.build_absolute_uri(
            f"{reverse('landing_page')}?ref={request.user.profile.referral_code}"
        )

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'referral_signup_url': referral_signup_url,
        'referral_landing_url': referral_landing_url,
        'can_refer': can_refer,
        'referral_count': request.user.referred_users.count(),
    })


@check_honeypot_with_logging
def register_view(request):
    """Simple user registration view with minimal fields"""
    referral_code = (
        request.GET.get('ref')
        or request.POST.get('referral_code')
        or request.session.get('referral_code')
        or ''
    ).strip().upper()

    if referral_code:
        request.session['referral_code'] = referral_code

    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()  # This will create both User and basic UserProfile
            referrer_user = None
            journey_type = 'with_referrer' if referral_code else 'without_referrer'
            logger.info(
                "Signup journey=%s new_user=%s query_ref=%s session_ref=%s post_ref=%s",
                journey_type,
                user.email,
                (request.GET.get('ref') or '').strip(),
                (request.session.get('referral_code') or '').strip(),
                (request.POST.get('referral_code') or '').strip(),
            )

            if referral_code:
                referrer_profile = _find_referrer_profile(referral_code)
                if referrer_profile and referrer_profile.user_id != user.id:
                    referrer_user = referrer_profile.user
                    profile = user.profile
                    profile.referred_by = referrer_user
                    profile.referred_at = timezone.now()
                    profile.referral_code_used = referral_code
                    profile.save(update_fields=['referred_by', 'referred_at', 'referral_code_used'])
                    logger.info(
                        "Referral tracked: new_user=%s referred_by=%s code=%s",
                        user.email,
                        referrer_profile.user.email,
                        referral_code,
                    )

                    # Additional referred journey step: notify referrer without sharing contact details.
                    referrer_email_result = _notify_referrer_by_email(
                        referrer_user=referrer_user,
                        referred_user=user,
                        referral_code=referral_code,
                    )
                    if referrer_email_result.get('success'):
                        logger.info(
                            "Referrer email notification sent: referrer=%s referred_identifier=%s",
                            referrer_user.email,
                            referrer_email_result.get('referred_identifier'),
                        )

                    ac_referrer_notification_result = notify_referrer_of_signup(
                        referrer_user=referrer_user,
                        referred_user=user,
                        referral_code=referral_code,
                    )
                    if ac_referrer_notification_result.get('success'):
                        logger.info(
                            "ActiveCampaign referrer notification recorded: referrer=%s contact_id=%s referred_identifier=%s",
                            referrer_user.email,
                            ac_referrer_notification_result.get('contact_id'),
                            ac_referrer_notification_result.get('referred_identifier'),
                        )
                    else:
                        logger.warning(
                            "ActiveCampaign referrer notification failed: referrer=%s reason=%s",
                            referrer_user.email,
                            ac_referrer_notification_result.get('reason'),
                        )
                else:
                    profile = user.profile
                    profile.referral_code_used = referral_code
                    profile.save(update_fields=['referral_code_used'])
                    logger.warning(
                        "Referral code not matched during signup: code=%s new_user=%s",
                        referral_code,
                        user.email,
                    )
            else:
                logger.warning(
                    "No referral code available during signup: new_user=%s",
                    user.email,
                )

            # Sync new signup to ActiveCampaign (non-blocking)
            ac_result = sync_contact(
                user,
                referral_code=referral_code,
                referred_by=referrer_user,
            )
            if ac_result.get('success'):
                logger.info(
                    "ActiveCampaign sync success for %s (contact_id=%s, tags=%s)",
                    user.email,
                    ac_result.get('contact_id'),
                    ac_result.get('applied_tags') or [],
                )
            else:
                logger.warning(
                    "ActiveCampaign sync result for %s: %s",
                    user.email,
                    ac_result.get('reason'),
                )
            
            # Send welcome email
            try:
                context = {
                    'user': user,
                    'current_year': datetime.datetime.now().year,
                }
                
                # Render HTML email
                html_message = render_to_string('users/welcome_email.html', context)
                # Render plain text version
                plain_message = render_to_string('users/welcome_email.txt', context)
                
                send_mail(
                    subject='Welcome to LEXIT | Buy-to-Let Investment Analyzer!',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                # Log successful email send (optional)
                print(f"Welcome email sent successfully to {user.email}")
                
            except Exception as e:
                # Log the error but don't prevent registration
                print(f"Failed to send welcome email to {user.email}: {str(e)}")
                messages.warning(request, 'Account created successfully! However, there was an issue sending the welcome email.')
            
            login(request, user)  # Automatically log in the new user
            messages.success(request, 'Welcome to LEXIT! Your account has been created successfully.')
            if 'referral_code' in request.session:
                del request.session['referral_code']
            return redirect('user_home:user_home')  # Redirect to user dashboard
    else:
        form = SimpleUserCreationForm()
    
    return render(request, 'users/register.html', {
        'form': form,
        'referral_code': referral_code,
    })


@check_honeypot_with_logging
def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('user_home:user_home')  # Redirect to user dashboard
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('landing_page')  # Redirect to homepage after logout


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with our template"""
    template_name = 'users/forgot_password.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')
    form_class = PasswordResetForm
    
    def form_valid(self, form):
        messages.success(self.request, 'If an account with that email exists, you will receive password reset instructions.')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view with our template"""
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')
    form_class = SetPasswordForm
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been reset successfully! You can now log in with your new password.')
        return super().form_valid(form)


def password_reset_done_view(request):
    """Password reset email sent confirmation"""
    return render(request, 'users/password_reset_done.html')


def password_reset_complete_view(request):
    """Password reset completed successfully"""
    return render(request, 'users/password_reset_complete.html')