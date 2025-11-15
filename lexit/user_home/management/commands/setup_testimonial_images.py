from django.core.management.base import BaseCommand
from user_home.models import Testimonial
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Setup default testimonial images using static files'

    def handle(self, *args, **options):
        # Update testimonials to use static images instead of uploaded media
        testimonials_with_static_images = [
            {
                'author_name': 'Rebecca Harris',
                'static_image': 'testimonial_1.png'
            },
            {
                'author_name': 'James Chen', 
                'static_image': 'testimonial_2.png'
            },
            {
                'author_name': 'Sarah Mitchell',
                'static_image': 'testimonial_3.png'
            }
        ]
        
        for testimonial_data in testimonials_with_static_images:
            try:
                testimonial = Testimonial.objects.get(author_name=testimonial_data['author_name'])
                # Clear the uploaded image since it won't persist anyway
                if testimonial.author_image:
                    testimonial.author_image = None
                    testimonial.save()
                    self.stdout.write(f"Updated {testimonial.author_name} to use static image")
            except Testimonial.DoesNotExist:
                self.stdout.write(f"Testimonial for {testimonial_data['author_name']} not found")
        
        self.stdout.write(self.style.SUCCESS('Testimonial image setup completed!'))