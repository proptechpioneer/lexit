from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from datetime import date

class Property(models.Model):
    PROPERTY_TYPES = [
        ('detached', 'Detached House'),
        ('apartment', 'Apartment'),
        ('semi', 'Semi-Detached House'),
        ('terrace', 'Terraced House'),
        ('end', 'End of Terrace'),
        ('bungalow', 'Bungalow'),
        ('cottage', 'Cottage'),
    ]
    
    EPC_RATINGS = [
        ('A', 'A (Most Efficient)'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G (Least Efficient)'),
    ]
    
    OWNERSHIP_CHOICES = [
        ('company', 'Property is owned in company'),
        ('individual', 'Property is owned in own name'),
    ]

    MORTGAGE_CHOICES = [
        ('principal_and_interest', 'Principal & Interest'),
        ('interest_only', 'Interest Only'),
    ]

    # Property Image
    property_image = models.ImageField(upload_to='property_images/', blank=True, null=True)

    # Address Information
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    unit_number = models.CharField(max_length=200, blank=True)
    street_number = models.CharField(max_length=200, blank=True)
    street_name = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=8, blank=False)

    # Basic Property Information
    date_of_purchase = models.DateField(blank=False, default=date(2022, 1, 1))
    ownership_status = models.CharField(max_length=20, choices=OWNERSHIP_CHOICES, default='individual')
    property_name = models.CharField(max_length=100, blank=False, help_text="Give your property a name for easy identification")
    property_type = models.CharField(max_length=20, blank=False, choices=PROPERTY_TYPES, default='semi')
    number_bedrooms = models.PositiveIntegerField(blank=False, default=3)
    number_bathrooms = models.PositiveIntegerField(blank=False, default=1)
    car_parking_spaces = models.PositiveIntegerField(blank=True, default=1)
    epc_rating = models.CharField(max_length=1, choices=EPC_RATINGS, blank=False, null=True)

    # Financial Information
    purchase_price = models.DecimalField(blank=False, max_digits=8, decimal_places=0, default=100000, help_text="Original purchase price")
    deposit_paid = models.DecimalField(blank=False, max_digits=8, decimal_places=0, default=0, help_text="Initial deposit paid")
    estimated_market_value = models.DecimalField(blank=False, max_digits=8, decimal_places=0, default=0, null=True, help_text="Estimated current market value")
    weekly_rent = models.DecimalField(blank=False, max_digits=5, decimal_places=0, default=0, help_text="Current weekly rental income")
                                           
    # Mortgage Information
    has_mortgage = models.BooleanField(blank=False, default=False)
    mortgage_type = models.CharField(max_length=30, choices=MORTGAGE_CHOICES, blank=True, null=True)
    outstanding_mortgage_balance = models.DecimalField(max_digits=8, decimal_places=0, default=0, help_text="Remaining mortgage balance")
    mortgage_interest_rate = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Mortgage interest rate")
    mortgage_years_remaining = models.PositiveIntegerField(blank=True, null=True, help_text="Years remaining on mortgage")

    # Expenses
    property_management_fees = models.DecimalField(blank=False, max_digits=4, decimal_places=2, default=0, help_text="Property management fees as percentage of rental income")
    service_charge = models.DecimalField(blank=False, max_digits=5, decimal_places=0, default=0, help_text="Annual service charge")
    ground_rent = models.DecimalField(blank=False, max_digits=5, decimal_places=0, default=0, help_text="Annual ground rent")
    other_annual_costs = models.DecimalField(blank=False, max_digits=8, decimal_places=0, default=0, help_text="Other annual costs (e.g., insurance, maintenance)")

    # Income Information
    annual_income = models.DecimalField(blank=False, max_digits=8, decimal_places=0, default=0, help_text="Total annual income from property")
    uk_resident = models.BooleanField(default=True, help_text="Is the property owner a UK resident?")
    uk_taxfree_allowance = models.BooleanField(default=True, help_text="Is the property owner eligible for UK tax-free allowance?")

    # Management
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.property_name}-{self.city}")
            slug = base_slug
            counter = 1
            while Property.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.property_name} - {self.city}"
    
    def get_absolute_url(self):
        return reverse('user_home:property_detail', kwargs={'pk': self.pk})
    
    @property
    def full_address(self):
        address_parts = []
        if self.unit_number:
            address_parts.append(self.unit_number)
        if self.street_number:
            address_parts.append(self.street_number)
        address_parts.extend([self.street_name, self.city, self.postcode])
        return ", ".join(filter(None, address_parts))
    
    @property
    def annual_rent(self):
        return self.weekly_rent * 52
    
    @property
    def gross_yield(self):
        if self.estimated_market_value and self.estimated_market_value > 0:
            return (self.annual_rent / self.estimated_market_value) * 100
        return 0
    
    @property
    def buyer_type_for_sdlt(self):
        """Determine the buyer type for SDLT calculations based on ownership status and UK residence"""
        if self.ownership_status == 'company':
            return 'uk_company'
        elif self.ownership_status == 'individual':
            # Check if UK resident for individuals
            if self.uk_resident:
                return 'uk_individual'
            else:
                return 'non_uk_individual'
        else:
            # Default fallback
            return 'uk_individual'
    
    @property
    def get_property_image_url(self):
        """Return the property image URL or default image if none uploaded"""
        if self.property_image and hasattr(self.property_image, 'url'):
            return self.property_image.url
        else:
            # Return default image from static folder
            from django.conf import settings
            return f"{settings.STATIC_URL}images/lexit_image.png"
    
    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-created_at']


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    is_main_image = models.BooleanField(default=False, help_text="Is this the main property image?")
    date_uploaded = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_main_image', 'date_uploaded']
    
    def __str__(self):
        return f"Image for {self.property.property_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one main image per property
        if self.is_main_image:
            PropertyImage.objects.filter(property=self.property, is_main_image=True).update(is_main_image=False)
        super().save(*args, **kwargs)


class PropertyDocument(models.Model):
    DOCUMENT_TYPES = [
        ('deed', 'Property Deed'),
        ('survey', 'Survey Report'),
        ('epc', 'Energy Performance Certificate'),
        ('insurance', 'Insurance Document'),
        ('lease', 'Lease Agreement'),
        ('mortgage', 'Mortgage Document'),
        ('other', 'Other Document'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='property_documents/%Y/%m/')
    description = models.TextField(max_length=500, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['document_type', 'title']
    
    def __str__(self):
        return f"{self.title} - {self.property.property_name}"


class Testimonial(models.Model):
    """Model for storing customer testimonials"""
    quote = models.CharField(max_length=500, help_text="The main testimonial quote")
    description = models.TextField(max_length=1000, help_text="Detailed testimonial description")
    author_name = models.CharField(max_length=100, help_text="Name of the person giving the testimonial")
    author_role = models.CharField(max_length=100, help_text="Job title or role of the testimonial author")
    author_image = models.ImageField(upload_to='testimonials/', blank=True, null=True, help_text="Photo of the testimonial author")
    social_media_link = models.URLField(blank=True, null=True, help_text="LinkedIn, Twitter, or other social media profile")
    is_active = models.BooleanField(default=True, help_text="Whether this testimonial should be displayed")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which testimonials should be displayed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
    
    def __str__(self):
        return f"{self.author_name} - {self.quote[:50]}..."
    
    @property
    def get_author_image_url(self):
        """Return the author image URL or default image if none uploaded"""
        if self.author_image and hasattr(self.author_image, 'url'):
            # For production, ensure full domain is included
            from django.conf import settings
            image_url = self.author_image.url
            
            # If URL is relative, make it absolute for production
            if not image_url.startswith('http') and hasattr(settings, 'ALLOWED_HOSTS'):
                if settings.ENVIRONMENT == 'production':
                    # Use the production domain
                    return f"https://www.lexit.tech{image_url}"
            
            return image_url
        else:
            # Return default testimonial image from static folder
            from django.conf import settings
            return f"{settings.STATIC_URL}images/tesitimonial_girl.png"
