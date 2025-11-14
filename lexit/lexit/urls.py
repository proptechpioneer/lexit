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

def create_superuser_view(request):
    """Temporary view to create superuser - REMOVE AFTER USE"""
    from django.contrib.auth import get_user_model
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    import json
    
    User = get_user_model()
    
    # Create multiple superusers
    superusers = [
        {
            'username': 'admin',
            'email': 'ashley.osborne@prs-im.co.uk',
            'password': 'LexitAdmin2024!'
        },
        {
            'username': 'ash_admin',
            'email': 'ashley.osborne@prs-im.co.uk',
            'password': 'DuV@lGlobal123'
        }
    ]
    
    results = []
    
    for user_data in superusers:
        username = user_data['username']
        email = user_data['email']
        password = user_data['password']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            results.append({
                'username': username,
                'status': 'exists',
                'message': f'Superuser "{username}" already exists!'
            })
            continue
        
        try:
            # Create the superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            results.append({
                'username': username,
                'status': 'success',
                'message': f'Superuser "{username}" created successfully!',
                'email': email,
                'password': password
            })
        
        except Exception as e:
            results.append({
                'username': username,
                'status': 'error',
                'message': f'Error creating superuser "{username}": {str(e)}'
            })
    
    return JsonResponse({
        'results': results,
        'admin_url': '/centralmanagementserver/'
    })

def favicon_view(request):
    # Return a redirect to the static favicon
    return RedirectView.as_view(url=settings.STATIC_URL + 'images/lexit_favicon.png', permanent=True)(request)

def debug_media_view(request):
    """Debug view to check media configuration"""
    import os
    response_data = {
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
        'DEBUG': settings.DEBUG,
        'media_files': []
    }
    
    # List files in media directory
    if os.path.exists(settings.MEDIA_ROOT):
        for file in os.listdir(settings.MEDIA_ROOT):
            file_path = os.path.join(settings.MEDIA_ROOT, file)
            if os.path.isfile(file_path):
                response_data['media_files'].append({
                    'name': file,
                    'size': os.path.getsize(file_path),
                    'url': settings.MEDIA_URL + file
                })
    
    from django.http import JsonResponse
    return JsonResponse(response_data)

urlpatterns = [
    path('centralmanagementserver/', admin.site.urls),  # Real admin interface
    path('create-superuser-temp/', create_superuser_view, name='create_superuser_temp'),  # Temporary superuser creation
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
