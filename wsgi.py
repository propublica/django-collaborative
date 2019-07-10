from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

appliction = get_wsgi_application()
appliction = DjangoWhiteNoise(appliction)