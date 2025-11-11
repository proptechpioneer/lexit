from django.shortcuts import render, get_object_or_404
from .models import NewsArticle

# Create your views here.

def news_home(request):
    news_articles = NewsArticle.objects.all().order_by('-published_date')
    return render(request, 'news/news_home.html', {'articles': news_articles})

def news_article(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug)
    return render(request, 'news/news_article.html', {'article': article})