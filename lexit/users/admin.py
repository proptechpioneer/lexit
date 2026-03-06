from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import UserProfile, HoneypotAttempt, SecurityEvent
from .activecampaign import build_referral_code_tag_name


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'country',
        'referral_code',
        'referral_code_used',
        'ac_referral_tag',
        'referred_by',
        'referred_contacts_count',
        'created_at',
        'updated_at',
    )
    list_filter = ('country', 'created_at', 'use_avatar', 'referred_by')
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'referral_code',
        'referral_code_used',
        'referred_by__username',
        'referred_by__email',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'ac_referral_tag',
        'referred_contacts_count',
        'referred_contacts_report',
    )

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Referral Tracking', {
            'fields': (
                'referral_code',
                'referral_code_used',
                'ac_referral_tag',
                'referred_by',
                'referred_at',
                'referred_contacts_count',
                'referred_contacts_report',
            )
        }),
        ('Profile Details', {
            'fields': (
                'profile_image', 'avatar_choice', 'use_avatar',
                'country', 'city', 'retirement_objective', 'income_objective',
                'capital_gain_objective', 'accidental_landlord', 'future_ownership',
                'facebook_url', 'linkedin_url', 'twitter_url', 'whatsapp_number',
                'bio', 'website_url', 'show_email', 'show_social_media',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'referred_by')

    def referred_contacts_count(self, obj):
        return obj.user.referred_users.count()
    referred_contacts_count.short_description = 'Referred Contacts'

    def ac_referral_tag(self, obj):
        source_code = obj.referral_code_used
        if not source_code and obj.referred_by and hasattr(obj.referred_by, 'profile'):
            source_code = obj.referred_by.profile.referral_code

        tag_name = build_referral_code_tag_name(source_code)
        return tag_name or 'N/A'
    ac_referral_tag.short_description = 'AC Referral Tag'

    def referred_contacts_report(self, obj):
        referred_profiles = UserProfile.objects.select_related('user').filter(
            referred_by=obj.user
        ).order_by('-referred_at', '-created_at')[:50]

        if not referred_profiles:
            return 'No referred contacts yet.'

        rows = []
        for profile in referred_profiles:
            display_name = profile.user.get_full_name().strip() or profile.user.username
            referred_at = profile.referred_at or profile.created_at
            used_code = profile.referral_code_used or obj.referral_code
            ac_tag = build_referral_code_tag_name(used_code)
            rows.append(
                (
                    f"{display_name} ({profile.user.email}) — {referred_at:%Y-%m-%d %H:%M}"
                    f" — code={used_code or 'N/A'}"
                    f" — ac_tag={ac_tag or 'N/A'}"
                )
            )

        return format_html('<br>'.join(rows))
    referred_contacts_report.short_description = 'Referred Contacts Report (latest 50)'


@admin.register(HoneypotAttempt)
class HoneypotAttemptAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'ip_address', 'attempt_type', 'path', 'is_recent_indicator', 'blocked')
    list_filter = ('attempt_type', 'blocked', 'timestamp', 'honeypot_field')
    search_fields = ('ip_address', 'user_agent', 'honeypot_value', 'path')
    readonly_fields = ('timestamp',)
    ordering = ['-timestamp']
    
    def is_recent_indicator(self, obj):
        if obj.is_recent:
            return format_html('<span style="color: red; font-weight: bold;">Recent (24h)</span>')
        return 'No'
    is_recent_indicator.short_description = 'Recent'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('timestamp', 'ip_address', 'attempt_type', 'blocked')
        }),
        ('Request Details', {
            'fields': ('path', 'user_agent', 'referer'),
            'classes': ('collapse',)
        }),
        ('Honeypot Data', {
            'fields': ('honeypot_field', 'honeypot_value', 'form_data'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

    # Add action to mark attempts as reviewed
    actions = ['mark_as_reviewed']
    
    def mark_as_reviewed(self, request, queryset):
        # You could add a 'reviewed' field to the model if needed
        self.message_user(request, f"Marked {queryset.count()} attempts as reviewed.")
    mark_as_reviewed.short_description = "Mark selected attempts as reviewed"


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'event_type', 'severity', 'ip_address', 'user', 'severity_color')
    list_filter = ('event_type', 'severity', 'timestamp')
    search_fields = ('ip_address', 'user__username', 'details')
    readonly_fields = ('timestamp',)
    ordering = ['-timestamp']
    
    def severity_color(self, obj):
        colors = {
            'low': 'green',
            'medium': 'orange', 
            'high': 'red',
            'critical': 'darkred'
        }
        color = colors.get(obj.severity, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_color.short_description = 'Severity'
    
    fieldsets = (
        ('Event Information', {
            'fields': ('timestamp', 'event_type', 'severity')
        }),
        ('Source Information', {
            'fields': ('ip_address', 'user')
        }),
        ('Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
    )
