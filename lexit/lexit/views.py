from django.shortcuts import render
from user_home.models import Testimonial
from news.models import NewsArticle

def landing_page(request):
    # Get active testimonials ordered by display_order
    testimonials = Testimonial.objects.filter(is_active=True).order_by('display_order', '-created_at')
    
    # Get featured articles first, then recent articles as fallback
    featured_articles = NewsArticle.objects.filter(is_featured=True).order_by('-published_date')[:4]
    
    # If we don't have enough featured articles, fill with recent articles
    if featured_articles.count() < 4:
        recent_articles = NewsArticle.objects.exclude(
            id__in=featured_articles.values_list('id', flat=True)
        ).order_by('-published_date')[:4-featured_articles.count()]
        recent_articles = list(featured_articles) + list(recent_articles)
    else:
        recent_articles = featured_articles
    
    context = {
        'testimonials': testimonials,
        'recent_articles': recent_articles[:4],  # Ensure we only show 4
    }
    return render(request, "landing_page.html", context)

def rrb_home(request):
    return render(request, "rrb_home.html")

def test_css(request):
    return render(request, "test_css.html")

def debug_static(request):
    return render(request, "debug_static.html")
