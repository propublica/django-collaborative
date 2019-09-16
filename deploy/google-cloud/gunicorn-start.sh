#!/bin/bash

# django housekeeping & setup
python manage.py migrate --noinput  # collect static files
python manage.py collectstatic --noinput  # collect static files

# Prepare log files and start outputting logs to stdout
touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
tail -n 0 -f /srv/logs/*.log &

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn collaborative.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 1 \
    --log-level=info \
    --log-file=/srv/logs/gunicorn.log \
    --access-logfile=/srv/logs/access.log &

# Start nginx
echo "Starting nginx..."
exec service nginx start
