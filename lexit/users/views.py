from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from honeypot.decorators import check_honeypot
from .security_utils import check_honeypot_with_logging
from .forms import SimpleUserCreationForm, UserProfileForm, ExtendedUserProfileForm
from .models import UserProfile

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
    
    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@check_honeypot_with_logging
def register_view(request):
    """Simple user registration view with minimal fields"""
    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # This will create both User and basic UserProfile
            login(request, user)  # Automatically log in the new user
            messages.success(request, 'Welcome to LEXIT! Your account has been created successfully.')
            return redirect('user_home:user_home')  # Redirect to user dashboard
    else:
        form = SimpleUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


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