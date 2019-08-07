#!/bin/bash
echo "Running migrations..."
python manage.py migrate
echo "Collecting staticfiles..."
python manage.py collectstatic --no-input
