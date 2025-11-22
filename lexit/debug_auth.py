#!/usr/bin/env python
"""Debug script to test user authentication"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lexit.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.template import Context, Template
from django.contrib.auth.context_processors import auth

User = get_user_model()

def test_auth_context():
    """Test authentication context rendering"""
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test unauthenticated request
    print("\n=== Testing Unauthenticated Request ===")
    request = factory.get('/')
    request.user = None
    context = auth(request)
    print(f"user: {context.get('user')}")
    print(f"user.is_authenticated: {getattr(context.get('user'), 'is_authenticated', False)}")
    
    # Test authenticated request
    print("\n=== Testing Authenticated Request ===")
    request = factory.get('/')
    request.user = user
    context = auth(request)
    print(f"user: {context.get('user')}")
    print(f"user.is_authenticated: {getattr(context.get('user'), 'is_authenticated', False)}")
    
    # Test template rendering
    print("\n=== Testing Template Rendering ===")
    template_str = '''
    {% if user.is_authenticated %}
        <p>User is authenticated: {{ user.username }}</p>
        <form method="post" action="/logout/">
            <button type="submit">Logout</button>
        </form>
    {% else %}
        <p>User is not authenticated</p>
        <a href="/login/">Login</a>
    {% endif %}
    '''
    
    template = Template(template_str)
    context_data = Context({'user': user})
    rendered = template.render(context_data)
    print("Rendered template:")
    print(rendered)

if __name__ == '__main__':
    test_auth_context()