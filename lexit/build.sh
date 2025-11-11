#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "=== STATIC FILES DEBUGGING ==="
echo "Checking source static directory..."
ls -la static/ 2>/dev/null || echo "No static directory found"
echo ""
echo "Checking static/dist directory..."
ls -la static/dist/ 2>/dev/null || echo "No static/dist directory found"
echo ""
echo "Checking static/src directory..."
ls -la static/src/ 2>/dev/null || echo "No static/src directory found"
echo ""
echo "Checking static/images directory..."
ls -la static/images/ 2>/dev/null || echo "No static/images directory found"
echo ""

echo "Removing old staticfiles directory..."
rm -rf staticfiles/

echo "Collecting static files with verbose output..."
python manage.py collectstatic --noinput --clear --verbosity=2

echo ""
echo "=== AFTER COLLECTION ==="
echo "Checking staticfiles directory..."
ls -la staticfiles/ 2>/dev/null || echo "No staticfiles directory found"
echo ""
echo "Checking staticfiles/dist..."
ls -la staticfiles/dist/ 2>/dev/null || echo "No dist in staticfiles"
echo ""
echo "Checking staticfiles/src..."  
ls -la staticfiles/src/ 2>/dev/null || echo "No src in staticfiles"
echo ""
echo "Checking staticfiles/images..."
ls -la staticfiles/images/ 2>/dev/null || echo "No images in staticfiles"
echo ""

echo "Running migrations..."
python manage.py migrate

echo "Build completed successfully!"