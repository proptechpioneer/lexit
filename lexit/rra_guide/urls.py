from django.urls import path
from . import views

app_name = 'rra_guide'

urlpatterns = [
    path('', views.rra_guide_home, name='home'),
    path('section/<str:section_id>/', views.rra_section_detail, name='section_detail'),
    path('faqs/', views.rra_faqs, name='faqs'),
]