from django.urls import path
from . import views

app_name = 'user_home'

urlpatterns = [
    # Dashboard
    path('', views.user_home, name='user_home'),
    path('stats-mockup/', views.dashboard_stats_mockup, name='dashboard_stats_mockup'),
    path('property-cards-mockup/', views.property_cards_mockup, name='property_cards_mockup'),
    path('property-page-mockup/', views.property_page_mockup, name='property_page_mockup'),
    
    # Property management
    path('properties/', views.property_list, name='property_list'),
    path('properties/add/', views.upload_property, name='upload_property'),
    path('properties/add/', views.upload_property, name='add_property'),  # Alias for template compatibility
    path('properties/<slug:slug>/', views.property_detail, name='property_detail'),
    path('properties/<slug:slug>/edit/', views.edit_property, name='edit_property'),
    # path('properties/<int:pk>/delete/', views.PropertyDeleteView.as_view(), name='delete_property'),
    
    # Deal analysis
    path('analyse-deal/', views.analyse_deal, name='analyse_deal'),
    path('email-deal-analysis-pdf/', views.email_deal_analysis_pdf, name='email_deal_analysis_pdf'),
]