from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import UserProfile, HoneypotAttempt, SecurityEvent


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'created_at', 'updated_at')
    list_filter = ('country', 'created_at', 'use_avatar')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')


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
