from django.core.management.base import BaseCommand
from user_home.models import Testimonial


class Command(BaseCommand):
    help = 'Create sample testimonials for testing'

    def handle(self, *args, **options):
        # Create sample testimonials
        testimonials_data = [
            {
                'quote': 'This is the first analyser I have seen which is simple to use and provides such a clear analysis.',
                'description': 'I work with BtL investors from all over the world and I am constantly asked questions about how to improve tenant experiences. This is the first analyser I have seen which is simple to use and provides such a clear analysis.',
                'author_name': 'Rebecca Harris',
                'author_role': 'Real Estate Expert',
                'social_media_link': 'https://linkedin.com/in/rebeccaharris',
                'is_active': True,
                'display_order': 1,
            },
            {
                'quote': 'LEXIT helped me understand my property portfolio in a way no other tool has managed.',
                'description': 'As an international landlord with properties across the UK, I needed something that could give me clear insights into my investments. LEXIT provided exactly that - comprehensive analysis with actionable recommendations.',
                'author_name': 'James Chen',
                'author_role': 'International Property Investor',
                'social_media_link': 'https://linkedin.com/in/jameschen',
                'is_active': True,
                'display_order': 2,
            },
            {
                'quote': 'Finally, a tool that makes sense of the complex buy-to-let market!',
                'description': 'The regulatory changes were overwhelming until I found LEXIT. Now I have clear guidance on compliance and can make informed decisions about my property investments with confidence.',
                'author_name': 'Sarah Mitchell',
                'author_role': 'Property Portfolio Manager',
                'social_media_link': 'https://twitter.com/sarahmitchell',
                'is_active': True,
                'display_order': 3,
            }
        ]

        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                author_name=testimonial_data['author_name'],
                defaults=testimonial_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created testimonial for {testimonial.author_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Testimonial for {testimonial.author_name} already exists')
                )

        self.stdout.write(self.style.SUCCESS('Sample testimonials creation completed!'))