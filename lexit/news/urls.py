from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('news/', views.news_home, name='news_home'),
    path('article/<slug:slug>/', views.news_article, name='news_article'),
]