release: python manage.py migrate --noinput && python manage.py collectstatic --no-input
web: python manage.py migrate --noinput && python manage.py collectstatic --no-input &&  gunicorn collaborative.wsgi --log-file -
clock: python clock.py
