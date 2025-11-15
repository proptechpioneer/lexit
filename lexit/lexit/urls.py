"""
URL configuration for lexit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import RedirectView
from . import views
from .media_views import serve_media
from .email_test_views import test_email
from .sendgrid_direct_test import direct_sendgrid_test

def favicon_view(request):
    # Return a redirect to the static favicon
    return RedirectView.as_view(url=settings.STATIC_URL + 'images/lexit_favicon.png', permanent=True)(request)

def debug_media_view(request):
    """Debug view to check media configuration - Updated"""
    import os
    response_data = {
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
        'DEBUG': settings.DEBUG,
        'ENVIRONMENT': getattr(settings, 'ENVIRONMENT', 'unknown'),
        'media_files': [],
        'testimonials': [],
        'cloudinary_config': {}
    }
    
    # Check Cloudinary configuration
    import os
    response_data['environment_vars'] = {
        'CLOUDINARY_CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'NOT_SET'),
        'CLOUDINARY_API_KEY_SET': bool(os.environ.get('CLOUDINARY_API_KEY')),
        'CLOUDINARY_API_SECRET_SET': bool(os.environ.get('CLOUDINARY_API_SECRET')),
    }
    
    if hasattr(settings, 'CLOUDINARY_STORAGE'):
        response_data['cloudinary_config'] = {
            'cloud_name_set': bool(settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')),
            'api_key_set': bool(settings.CLOUDINARY_STORAGE.get('API_KEY')),
            'api_secret_set': bool(settings.CLOUDINARY_STORAGE.get('API_SECRET')),
            'cloud_name': settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', '')[:10] + '...' if settings.CLOUDINARY_STORAGE.get('CLOUD_NAME') else ''
        }
    
    # Check storage backend
    try:
        from django.core.files.storage import default_storage
        response_data['storage_backend'] = str(type(default_storage).__name__)
    except Exception as e:
        response_data['storage_backend'] = f"Error: {str(e)}"
    
    # List files in media directory
    if os.path.exists(settings.MEDIA_ROOT):
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                response_data['media_files'].append({
                    'name': relative_path,
                    'size': os.path.getsize(file_path),
                    'url': settings.MEDIA_URL + relative_path.replace('\\', '/')
                })
    
    # Check testimonial data
    from user_home.models import Testimonial
    for testimonial in Testimonial.objects.all():
        testimonial_data = {
            'author_name': testimonial.author_name,
            'is_active': testimonial.is_active,
            'has_image': bool(testimonial.author_image),
            'image_name': testimonial.author_image.name if testimonial.author_image else None,
            'get_author_image_url': testimonial.get_author_image_url,
        }
        
        if testimonial.author_image:
            try:
                testimonial_data['image_url_raw'] = testimonial.author_image.url
            except Exception as e:
                testimonial_data['image_url_error'] = str(e)
        
        response_data['testimonials'].append(testimonial_data)
    
    from django.http import JsonResponse
    return JsonResponse(response_data)

urlpatterns = [
    path('centralmanagementserver/', admin.site.urls),  # Real admin interface
    path('favicon.ico', favicon_view, name='favicon'),
    path('debug-media/', debug_media_view, name='debug_media'),  # Debug endpoint
    path('test-email/', test_email, name='test_email'),  # Email test endpoint
    path('test-sendgrid-direct/', direct_sendgrid_test, name='test_sendgrid_direct'),  # Direct SendGrid API test
    path('', views.landing_page, name='landing_page'),
    path('rrb/', views.rrb_home, name='rrb_home'),
    path('rra-guide/', include('rra_guide.urls', namespace='rra_guide')),
    path('test-css/', views.test_css, name='test_css'),
    path('debug-static/', views.debug_static, name='debug_static'),
    path('news/', include('news.urls', namespace='news')),
    path('users/', include('users.urls', namespace='users')),
    path('dashboard/', include('user_home.urls', namespace='user_home')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

# Serve media files in all environments
# Use Django's static file serving for media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Also add explicit static file serving for completeness
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
