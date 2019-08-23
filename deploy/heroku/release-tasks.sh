#!/bin/bash
echo "Running migrations..."
python manage.py migrate -v 3
echo "Collecting staticfiles..."
python manage.py collectstatic --no-input
