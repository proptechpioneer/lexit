#!/usr/bin/env python
import os
import sys
import django
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lexit.settings')

# Add the project directory to Python path
project_dir = r'C:\Users\AshleyOsborne\Desktop\LEXIT BACKUPS\lexit3.0\11.11.2025\lexit'
sys.path.insert(0, project_dir)

# Set Railway environment variables
os.environ['DATABASE_URL'] = 'postgresql://postgres:VEFPrVImsjOHLuQlHdLViQBPgXpZEDSC@postgres.railway.internal:5432/railway'
os.environ['SECRET_KEY'] = 'Du$jzlBJ-#ijoK4&Cm3LL@kbVvjlUuR6R(a2N)EBk#YWxTfW-t'
os.environ['ENVIRONMENT'] = 'production'

# Initialize Django
django.setup()

def create_superuser():
    User = get_user_model()
    
    username = 'admin'
    email = 'ashley.osborne@prs-im.co.uk' 
    password = 'LexitAdmin2024!'
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists!")
        return
    
    # Create the superuser
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Superuser '{username}' created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
    except Exception as e:
        print(f"Error creating superuser: {e}")

if __name__ == '__main__':
    create_superuser()