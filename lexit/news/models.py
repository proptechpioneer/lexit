from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.
class NewsArticle(models.Model):
    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('article', 'Article'),
        ('renters_rights', "Renters' Rights Act"),
        ('market', 'Market'),
        ('tech_news', 'Tech News'),
        ('rent_reviews', 'Rent Reviews'),
        ('taxes', 'Taxes'),
    ]
    
    title = models.CharField(max_length=90)
    summary = models.CharField(max_length=200)
    body = CKEditor5Field('Body', config_name='extends')
    published_date = models.DateField(auto_now_add=True)
    slug = models.SlugField()
    banner = models.ImageField(default='default_banner.jpg', blank=True)
    alt_text = models.CharField(max_length=100, default='News Article Image')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='news')
    is_featured = models.BooleanField(default=False, help_text="Show this article on the landing page")

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_category_display_class(self):
        """Return CSS class for category badge"""
        category_colors = {
            'news': 'bg-yellow',                    # Yellow for general news
            'article': 'bg-light-blue',             # Light blue for articles
            'renters_rights': 'bg-red-400',         # Red for important legislation
            'market': 'bg-green-400',               # Green for market news
            'tech_news': 'bg-purple-400',           # Purple for tech
            'rent_reviews': 'bg-blue-400',          # Blue for rent reviews
            'taxes': 'bg-orange-400',               # Orange for tax-related content
        }
        return category_colors.get(self.category, 'bg-yellow')
