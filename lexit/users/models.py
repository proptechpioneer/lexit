from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    AVATAR_CHOICES = [
        ('default', 'Default Avatar'),
        ('avatar_1', 'Professional'),
        ('avatar_2', 'Casual'),
        ('avatar_3', 'Modern'),
        ('avatar_4', 'Elegant'),
        ('avatar_5', 'Creative'),
    ]
    
    COUNTRY_CHOICES = [
        ('GB', 'United Kingdom'),
        ('AU', 'Australia'),
        ('BH', 'Bahrain'),
        ('BE', 'Belgium'),
        ('CA', 'Canada'),
        ('CN', 'China'),
        ('DE', 'Germany'),
        ('ES', 'Spain'),
        ('FJ', 'Fiji'),
        ('FR', 'France'),
        ('GH', 'Ghana'),
        ('HK', 'Hong Kong'),
        ('ID', 'Indonesia'),
        ('IE', 'Ireland'),
        ('IL', 'Israel'),
        ('IN', 'India'),
        ('IT', 'Italy'),
        ('JO', 'Jordan'),
        ('JP', 'Japan'),
        ('KE', 'Kenya'),
        ('KR', 'South Korea'),
        ('KW', 'Kuwait'),
        ('LB', 'Lebanon'),
        ('MY', 'Malaysia'),
        ('NG', 'Nigeria'),
        ('NL', 'Netherlands'),
        ('NZ', 'New Zealand'),
        ('OM', 'Oman'),
        ('PH', 'Philippines'),
        ('PT', 'Portugal'),
        ('QA', 'Qatar'),
        ('RU', 'Russia'),
        ('SA', 'Saudi Arabia'),
        ('SG', 'Singapore'),
        ('CH', 'Switzerland'),
        ('TH', 'Thailand'),
        ('TR', 'Turkey'),
        ('AE', 'United Arab Emirates'),
        ('US', 'United States'),
        ('VN', 'Vietnam'),
        ('ZA', 'South Africa'),
        ('OTHER', 'Other'),
    ]
    
    FUTURE_OWNERSHIP_CHOICES = [
        ('thinking_selling', 'I am thinking of selling'),
        ('long_haul', 'I am in it for the long haul'),
        ('right_price', 'I would sell at the right price'),
        ('get_me_out', 'Just get me out!'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile Image and Avatar
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        blank=True, 
        null=True,
        help_text='Upload your profile picture'
    )
    avatar_choice = models.CharField(
        max_length=20, 
        choices=AVATAR_CHOICES, 
        default='default',
        help_text='Choose an avatar if you prefer not to upload a photo'
    )
    use_avatar = models.BooleanField(
        default=True,
        help_text='Use avatar instead of uploaded image'
    )
    
    # Location Information
    country = models.CharField(
        max_length=5, 
        choices=COUNTRY_CHOICES, 
        default='GB',
        help_text='Your country of residence'
    )
    city = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text='Your city (optional)'
    )
    
    # Investor Objectives
    retirement_objective = models.BooleanField(
        default=False,
        help_text='Investment for retirement planning'
    )
    income_objective = models.BooleanField(
        default=False,
        help_text='Investment for regular income generation'
    )
    capital_gain_objective = models.BooleanField(
        default=False,
        help_text='Investment for capital appreciation/growth'
    )
    accidental_landlord = models.BooleanField(
        default=False,
        help_text='Became a landlord by circumstance (e.g., inherited property, unable to sell)'
    )
    
    # Future Ownership Plans
    future_ownership = models.CharField(
        max_length=20,
        choices=FUTURE_OWNERSHIP_CHOICES,
        blank=True,
        null=True,
        help_text='Your future plans regarding property ownership'
    )
    
    # Social Media Information
    facebook_url = models.URLField(
        blank=True, 
        null=True,
        help_text='Your Facebook profile URL (optional)'
    )
    linkedin_url = models.URLField(
        blank=True, 
        null=True,
        help_text='Your LinkedIn profile URL (optional)'
    )
    twitter_url = models.URLField(
        blank=True, 
        null=True,
        help_text='Your Twitter profile URL (optional)'
    )
    whatsapp_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text='Your WhatsApp number with country code (e.g., +44 123 456 7890)'
    )
    
    # Additional Information
    bio = models.TextField(
        blank=True, 
        null=True,
        max_length=500,
        help_text='Tell us a bit about yourself (optional, max 500 characters)'
    )
    website_url = models.URLField(
        blank=True, 
        null=True,
        help_text='Your personal or business website (optional)'
    )
    
    # Privacy Settings
    show_email = models.BooleanField(
        default=False,
        help_text='Make your email visible to other users'
    )
    show_social_media = models.BooleanField(
        default=True,
        help_text='Make your social media links visible to other users'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_display_image_url(self):
        """Return the URL for the user's display image (either uploaded image or avatar)"""
        if not self.use_avatar and self.profile_image:
            return self.profile_image.url
        else:
            # Return avatar based on choice
            avatar_mapping = {
                'default': '/static/images/lexit_image.png',
                'avatar_1': '/static/images/avatar_1.png',
                'avatar_2': '/static/images/avatar_2.png', 
                'avatar_3': '/static/images/avatar_3.png',
                'avatar_4': '/static/images/avatar_4.png',
                'avatar_5': '/static/images/avatar_5.png',
            }
            return avatar_mapping.get(self.avatar_choice, '/static/images/lexit_image.png')
    
    def get_country_display_name(self):
        """Return the full country name"""
        return dict(self.COUNTRY_CHOICES).get(self.country, 'Unknown')
    
    def get_investor_objectives(self):
        """Return a list of the user's investor objectives"""
        objectives = []
        if self.retirement_objective:
            objectives.append('Retirement')
        if self.income_objective:
            objectives.append('Income')
        if self.capital_gain_objective:
            objectives.append('Capital Gain')
        if self.accidental_landlord:
            objectives.append('Accidental Landlord')
        return objectives
    
    def get_future_ownership_display(self):
        """Return the display name for future ownership choice"""
        return dict(self.FUTURE_OWNERSHIP_CHOICES).get(self.future_ownership, '')
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)


# Security Models for tracking honeypot and other security events

class HoneypotAttempt(models.Model):
    """Model to track honeypot violations and suspicious activity"""
    
    ip_address = models.GenericIPAddressField(help_text="IP address of the attempt")
    user_agent = models.TextField(blank=True, help_text="User agent string from the request")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When the attempt occurred")
    honeypot_field = models.CharField(max_length=100, help_text="Name of the honeypot field that was filled")
    honeypot_value = models.TextField(blank=True, help_text="Value entered in the honeypot field")
    form_data = models.JSONField(default=dict, blank=True, help_text="Other form data submitted")
    path = models.CharField(max_length=500, help_text="URL path where attempt occurred")
    referer = models.URLField(blank=True, null=True, help_text="HTTP referer header")
    attempt_type = models.CharField(
        max_length=50,
        choices=[
            ('honeypot', 'Honeypot Violation'),
            ('suspicious', 'Suspicious Activity'),
            ('bot', 'Bot Detection'),
        ],
        default='honeypot',
        help_text="Type of security violation"
    )
    blocked = models.BooleanField(default=True, help_text="Whether the attempt was blocked")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Security Attempt"
        verbose_name_plural = "Security Attempts"
    
    def __str__(self):
        return f"{self.get_attempt_type_display()} from {self.ip_address} at {self.timestamp}"
    
    @property
    def is_recent(self):
        """Check if attempt was in the last 24 hours"""
        from django.utils import timezone
        from datetime import timedelta
        return self.timestamp > timezone.now() - timedelta(days=1)


class SecurityEvent(models.Model):
    """Model for broader security events"""
    
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('failed_login', 'Failed Login'),
            ('suspicious_user_agent', 'Suspicious User Agent'),
            ('rate_limit', 'Rate Limit Exceeded'),
            ('invalid_session', 'Invalid Session'),
        ],
        help_text="Type of security event"
    )
    ip_address = models.GenericIPAddressField(help_text="IP address involved")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="User account if known")
    details = models.JSONField(default=dict, help_text="Event details")
    timestamp = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium'
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Security Event"
        verbose_name_plural = "Security Events"
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.get_severity_display()} ({self.timestamp})"
