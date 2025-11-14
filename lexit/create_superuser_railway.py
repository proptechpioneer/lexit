#!/usr/bin/env python
"""
Simple superuser creation script for Railway deployment
Add this as a build/deploy script or run it manually
"""
import os
import subprocess
import sys

def run_command():
    """Run the Django management command via Railway"""
    try:
        # Change to the correct directory
        os.chdir('/app')  # Railway uses /app as the project directory
        
        # Run the Django management command
        result = subprocess.run([
            'python', 'manage.py', 'create_new_superuser'
        ], capture_output=True, text=True)
        
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("Return code:", result.returncode)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    run_command()