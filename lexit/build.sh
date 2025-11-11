#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Checking static directory before collection..."
ls -la static/ || echo "No static directory found"

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Listing static files to verify collection..."
ls -la staticfiles/ || echo "No staticfiles directory found"
ls -la staticfiles/dist/ || echo "No dist directory in staticfiles"
ls -la staticfiles/src/ || echo "No src directory in staticfiles"

echo "Running migrations..."
python manage.py migrate

echo "Build completed successfully!"