#!/usr/bin/env bash
# exit on error
set -o errexit

cd visor_siniestros

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply migrations
python manage.py migrate
