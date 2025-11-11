from django.contrib import admin
from .models import NewsArticle

# Register your models here.
@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'published_date', 'slug')
    list_filter = ('category', 'is_featured', 'published_date')
    search_fields = ('title', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('category', 'is_featured')
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'summary', 'body', 'category')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'slug', 'banner', 'alt_text')
        }),
    )