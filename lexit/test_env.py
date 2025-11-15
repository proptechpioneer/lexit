#!/usr/bin/env python3
"""Test script to check environment variables in Railway"""

import os
import sys

print("=== Environment Variable Test ===")
print(f"Python version: {sys.version}")

# Check all CLOUDINARY environment variables
cloudinary_vars = {key: value for key, value in os.environ.items() if 'CLOUDINARY' in key}
print(f"All CLOUDINARY vars: {cloudinary_vars}")

# Check specific variables
print(f"CLOUDINARY_CLOUD_NAME: {os.environ.get('CLOUDINARY_CLOUD_NAME', 'NOT_SET')}")
print(f"CLOUDINARY_API_KEY: {os.environ.get('CLOUDINARY_API_KEY', 'NOT_SET')}")
print(f"CLOUDINARY_API_SECRET: {os.environ.get('CLOUDINARY_API_SECRET', 'NOT_SET')}")

# Check total environment variables count
print(f"Total environment variables: {len(os.environ)}")

# Print first few environment variables for debugging
print("First 10 environment variables:")
for i, (key, value) in enumerate(os.environ.items()):
    if i >= 10:
        break
    print(f"  {key}: {value[:10]}...")