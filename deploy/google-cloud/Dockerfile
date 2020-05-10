FROM python:3.7

# System dependencies
RUN apt-get update -qqy \
      && apt-get install -qqy --no-install-recommends tzdata \
      && apt-get install -y git nginx libpq-dev gunicorn \
      && apt-get clean \
      && rm -rf /var/lib/apt/lists/*

# Set env path variables used in this Dockerfile
ENV COLLABORATE_SRC=app
ENV COLLABORATE_SRVHOME=/srv
ENV COLLABORATE_SRVPROJ=$COLLABORATE_SRVHOME/$COLLABORATE_SRC

# Create base application subdirectories for dynamic data
WORKDIR $COLLABORATE_SRVHOME
RUN mkdir -p media logs www/assets
VOLUME ["$COLLABORATE_SRVHOME/media/", "$COLLABORATE_SRVHOME/logs/"]

# Get the Collaborate repository. We would normally grab the
# local code, but since we have to run this in a sub-directory
# (Google Run collides with Heroku files) and Docker won't let you pull
# things from an upper level directory, we pull from the repo.
# Eventually we'll want to either add a specific commit or find a
# way to reconcile between Google app.json and Heroku app.json.
RUN rm -rf $COLLABORATE_SRVPROJ && git clone -b master \
      https://github.com/propublica/django-collaborative \
      $COLLABORATE_SRVPROJ

# Build our web application
WORKDIR $COLLABORATE_SRVPROJ

# Python dependencies
RUN pip install -r requirements.txt && rm requirements.txt

# Daemon configs
RUN pwd
RUN ls -alh
COPY gunicorn-start.sh /
COPY django_nginx.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

ENV DJANGO_SETTINGS_MODULE "collaborative.settings"

# intend gunicorn-start to be the entrypoint command for this image
CMD  python manage.py migrate --noinput \
    && python manage.py collectstatic --noinput\
    && exec gunicorn --bind 0.0.0.0:$PORT \
        --workers 1 --threads 8 collaborative.wsgi
