release: python manage.py migrate && python manage.py collectstatic --no-input
web: gunicorn wsgi:application --log-file -