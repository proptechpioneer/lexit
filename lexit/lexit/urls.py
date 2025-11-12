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

def favicon_view(request):
    # Return a redirect to the static favicon
    return RedirectView.as_view(url=settings.STATIC_URL + 'images/lexit_favicon.png', permanent=True)(request)

urlpatterns = [
    path('centralmanagementserver/', admin.site.urls),  # Real admin interface
    path('favicon.ico', favicon_view, name='favicon'),
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

# Serve media files in development and production
# Render.com can handle Django's static file serving
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
