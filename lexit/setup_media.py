#!/usr/bin/env python
"""
Railway deployment script to ensure media directories exist
"""
import os
from django.conf import settings

def create_media_directories():
    """Create media directories if they don't exist"""
    media_dirs = [
        'testimonials',
        'property_images',
        'property_documents'
    ]
    
    # Ensure main media directory exists
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    
    # Create subdirectories
    for dir_name in media_dirs:
        dir_path = os.path.join(settings.MEDIA_ROOT, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created media directory: {dir_path}")

if __name__ == '__main__':
    # Set up Django
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lexit.settings')
    django.setup()
    
    create_media_directories()
    print("Media directories setup complete!")