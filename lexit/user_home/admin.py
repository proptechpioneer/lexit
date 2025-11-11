from django.contrib import admin
from .models import Property, PropertyImage, PropertyDocument, Testimonial

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['property_name', 'owner', 'property_type', 'city', 'number_bedrooms', 'number_bathrooms', 
                   'purchase_price', 'weekly_rent', 'created_at']
    list_filter = ['property_type', 'ownership_status', 'epc_rating', 'has_mortgage', 'uk_resident', 'city', 'created_at']
    search_fields = ['property_name', 'city', 'postcode', 'owner__username', 'owner__email', 'street_name']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('property_name', 'city')}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'property_name', 'property_type', 'ownership_status', 'property_image')
        }),
        ('Address', {
            'fields': ('unit_number', 'street_number', 'street_name', 'city', 'postcode')
        }),
        ('Property Details', {
            'fields': ('number_bedrooms', 'number_bathrooms', 'car_parking_spaces', 'epc_rating')
        }),
        ('Financial Information', {
            'fields': ('purchase_price', 'deposit_paid', 'estimated_market_value', 'weekly_rent', 'date_of_purchase')
        }),
        ('Mortgage Information', {
            'fields': ('has_mortgage', 'mortgage_type', 'outstanding_mortgage_balance', 'mortgage_interest_rate', 'mortgage_years_remaining'),
            'classes': ('collapse',)
        }),
        ('Expenses', {
            'fields': ('property_management_fees', 'service_charge', 'ground_rent', 'other_annual_costs'),
            'classes': ('collapse',)
        }),
        ('Income & Tax', {
            'fields': ('annual_income', 'uk_resident', 'uk_taxfree_allowance'),
            'classes': ('collapse',)
        }),
        ('Management', {
            'fields': ('slug', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'caption', 'is_main_image', 'date_uploaded']
    list_filter = ['is_main_image', 'date_uploaded']
    search_fields = ['property__property_name', 'caption']

@admin.register(PropertyDocument)
class PropertyDocumentAdmin(admin.ModelAdmin):
    list_display = ['property', 'document_type', 'title', 'date_uploaded']
    list_filter = ['document_type', 'date_uploaded']
    search_fields = ['property__property_name', 'title', 'description']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_role', 'quote_preview', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['author_name', 'author_role', 'quote', 'description']
    list_editable = ['is_active', 'display_order']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Testimonial Content', {
            'fields': ('quote', 'description')
        }),
        ('Author Information', {
            'fields': ('author_name', 'author_role', 'author_image', 'social_media_link')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def quote_preview(self, obj):
        return obj.quote[:50] + "..." if len(obj.quote) > 50 else obj.quote
    quote_preview.short_description = 'Quote Preview'
