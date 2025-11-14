from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from .models import UserProfile


class SimpleUserCreationForm(UserCreationForm):
    """Simple user registration form with minimal fields"""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Your last name (optional)'
        })
    )
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'your.email@example.com'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Tailwind classes to inherited fields
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Choose your username'
        })
        
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Choose a strong password'
        })
        
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Confirm your password'
        })

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        
        # Check against blacklist
        if username in [name.lower() for name in getattr(settings, 'USERNAME_BLACKLIST', [])]:
            raise forms.ValidationError(
                f"The username '{username}' is not allowed. Please choose a different username."
            )
        
        return self.cleaned_data['username']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # UserProfile will be created automatically by the post_save signal
        return user


class CustomUserCreationForm(UserCreationForm):
    """Extended user registration form with additional fields"""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Your last name (optional)'
        })
    )
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'your.email@example.com'
        })
    )
    
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
        }),
        label='I agree to the Terms of Service and Privacy Policy'
    )
    
    agree_gdpr = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
        }),
        label='I consent to the processing of my personal data in accordance with GDPR'
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Tailwind classes to inherited fields
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Choose your username'
        })
        
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Choose a strong password'
        })
        
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Confirm your password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for basic user information"""
    
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Your last name (optional)'
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'Your first name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'your.email@example.com'
            }),
        }


class ExtendedUserProfileForm(forms.ModelForm):
    """Form for extended user profile information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'profile_image', 'avatar_choice', 'use_avatar',
            'country', 'city',
            'retirement_objective', 'income_objective', 'capital_gain_objective', 'accidental_landlord',
            'future_ownership',
            'facebook_url', 'linkedin_url', 'twitter_url', 'whatsapp_number',
            'bio', 'website_url',
            'show_email', 'show_social_media'
        ]
        
        widgets = {
            'profile_image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'accept': 'image/*'
            }),
            
            'avatar_choice': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors'
            }),
            
            'use_avatar': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
            }),
            
            'country': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors'
            }),
            
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'Your city (optional)'
            }),
            
            'retirement_objective': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
            }),
            
            'income_objective': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
            }),
            
            'capital_gain_objective': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
            }),
            
            'accidental_landlord': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
            }),
            
            'future_ownership': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors'
            }),
            
            'facebook_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'https://facebook.com/yourprofile'
            }),
            
            'linkedin_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            
            'twitter_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'https://twitter.com/yourhandle'
            }),
            
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': '+44 123 456 7890'
            }),
            
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors resize-none',
                'rows': 4,
                'maxlength': 500,
                'placeholder': 'Tell us a bit about yourself (max 500 characters)'
            }),
            
            'website_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'https://yourwebsite.com'
            }),
            
            'show_email': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
            }),
            
            'show_social_media': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
            }),
        }


class UserRegistrationForm(forms.ModelForm):
    """Combined form for user registration with profile data"""
    
    # User fields
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Choose a strong password'
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Confirm your password'
        })
    )
    
    # Profile fields
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'accept': 'image/*'
        })
    )
    
    avatar_choice = forms.ChoiceField(
        choices=UserProfile.AVATAR_CHOICES,
        initial='default',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors'
        })
    )
    
    use_avatar = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
        })
    )
    
    country = forms.ChoiceField(
        choices=UserProfile.COUNTRY_CHOICES,
        initial='GB',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors'
        })
    )
    
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'Your city (optional)'
        })
    )
    
    retirement_objective = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
        })
    )
    
    income_objective = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
        })
    )
    
    capital_gain_objective = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
        })
    )
    
    accidental_landlord = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
        })
    )
    
    future_ownership = forms.ChoiceField(
        choices=[('', 'Select your future plans...')] + UserProfile.FUTURE_OWNERSHIP_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors'
        })
    )
    
    facebook_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'https://facebook.com/yourprofile'
        })
    )
    
    linkedin_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'https://linkedin.com/in/yourprofile'
        })
    )
    
    twitter_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'https://twitter.com/yourhandle'
        })
    )
    
    whatsapp_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': '+44 123 456 7890'
        })
    )
    
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors resize-none',
            'rows': 4,
            'maxlength': 500,
            'placeholder': 'Tell us a bit about yourself (max 500 characters)'
        })
    )
    
    website_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
            'placeholder': 'https://yourwebsite.com'
        })
    )
    
    show_email = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
        })
    )
    
    show_social_media = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500 focus:ring-2'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'Choose your username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'Your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'Your last name (optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-colors',
                'placeholder': 'your.email@example.com'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        
        # Check against blacklist
        if username in [name.lower() for name in getattr(settings, 'USERNAME_BLACKLIST', [])]:
            raise forms.ValidationError(
                f"The username '{username}' is not allowed. Please choose a different username."
            )
        
        return self.cleaned_data['username']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            # Get or create UserProfile (signal may have already created it)
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'profile_image': self.cleaned_data.get('profile_image'),
                    'avatar_choice': self.cleaned_data.get('avatar_choice', 'default'),
                    'use_avatar': self.cleaned_data.get('use_avatar', True),
                    'country': self.cleaned_data.get('country', 'GB'),
                    'city': self.cleaned_data.get('city', ''),
                    'retirement_objective': self.cleaned_data.get('retirement_objective', False),
                    'income_objective': self.cleaned_data.get('income_objective', False),
                    'capital_gain_objective': self.cleaned_data.get('capital_gain_objective', False),
                    'accidental_landlord': self.cleaned_data.get('accidental_landlord', False),
                    'future_ownership': self.cleaned_data.get('future_ownership', ''),
                    'facebook_url': self.cleaned_data.get('facebook_url', ''),
                    'linkedin_url': self.cleaned_data.get('linkedin_url', ''),
                    'twitter_url': self.cleaned_data.get('twitter_url', ''),
                    'whatsapp_number': self.cleaned_data.get('whatsapp_number', ''),
                    'bio': self.cleaned_data.get('bio', ''),
                    'website_url': self.cleaned_data.get('website_url', ''),
                    'show_email': self.cleaned_data.get('show_email', False),
                    'show_social_media': self.cleaned_data.get('show_social_media', True),
                }
            )
            # If profile already existed, update it with the form data
            if not created:
                for field, value in {
                    'profile_image': self.cleaned_data.get('profile_image'),
                    'avatar_choice': self.cleaned_data.get('avatar_choice', 'default'),
                    'use_avatar': self.cleaned_data.get('use_avatar', True),
                    'country': self.cleaned_data.get('country', 'GB'),
                    'city': self.cleaned_data.get('city', ''),
                    'retirement_objective': self.cleaned_data.get('retirement_objective', False),
                    'income_objective': self.cleaned_data.get('income_objective', False),
                    'capital_gain_objective': self.cleaned_data.get('capital_gain_objective', False),
                    'accidental_landlord': self.cleaned_data.get('accidental_landlord', False),
                    'future_ownership': self.cleaned_data.get('future_ownership', ''),
                    'facebook_url': self.cleaned_data.get('facebook_url', ''),
                    'linkedin_url': self.cleaned_data.get('linkedin_url', ''),
                    'twitter_url': self.cleaned_data.get('twitter_url', ''),
                    'whatsapp_number': self.cleaned_data.get('whatsapp_number', ''),
                    'bio': self.cleaned_data.get('bio', ''),
                    'website_url': self.cleaned_data.get('website_url', ''),
                    'show_email': self.cleaned_data.get('show_email', False),
                    'show_social_media': self.cleaned_data.get('show_social_media', True),
                }.items():
                    setattr(profile, field, value)
                profile.save()
        return user