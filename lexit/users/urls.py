from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    # Password reset URLs
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='forgot_password'),
    path('password_reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete_view, name='password_reset_complete'),
]