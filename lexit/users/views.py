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
from honeypot.decorators import check_honeypot
from .security_utils import check_honeypot_with_logging
from .forms import SimpleUserCreationForm, UserProfileForm, ExtendedUserProfileForm
from .models import UserProfile
from .activecampaign import sync_contact
import datetime
import logging


logger = logging.getLogger(__name__)

# Create your views here.

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
        'referral_count': request.user.referred_users.count(),
    })


@check_honeypot_with_logging
def register_view(request):
    """Simple user registration view with minimal fields"""
    referral_code = (request.GET.get('ref') or request.POST.get('referral_code') or '').strip().upper()

    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # This will create both User and basic UserProfile

            if referral_code:
                referrer_profile = UserProfile.objects.select_related('user').filter(
                    referral_code__iexact=referral_code
                ).first()
                if referrer_profile and referrer_profile.user_id != user.id:
                    profile = user.profile
                    profile.referred_by = referrer_profile.user
                    profile.referred_at = timezone.now()
                    profile.save(update_fields=['referred_by', 'referred_at'])
                    logger.info(
                        "Referral tracked: new_user=%s referred_by=%s code=%s",
                        user.email,
                        referrer_profile.user.email,
                        referral_code,
                    )
                else:
                    logger.warning(
                        "Referral code not matched during signup: code=%s new_user=%s",
                        referral_code,
                        user.email,
                    )

            # Sync new signup to ActiveCampaign (non-blocking)
            ac_result = sync_contact(user)
            if ac_result.get('success'):
                logger.info(
                    "ActiveCampaign sync success for %s (contact_id=%s)",
                    user.email,
                    ac_result.get('contact_id'),
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