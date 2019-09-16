FROM python:3

## pre-setup
#rm -f /tmp/collaborative.zip
#zip --exclude db.sqlite3 collaborative/settings_dev.py \*.pyc \
#  __pycache__ media/\* .git/\* \
#  -r /tmp/collaborative.zip ./
#scp /tmp/collaborative.zip ${DEPLOY_SERVER}:/tmp/
#cat deploy/remote_deploy.sh | ssh ${DEPLOY_SERVER}

# System dependencies
RUN apt-get update -qqy \
      && apt-get install -qqy --no-install-recommends tzdata \
      && apt-get install -y git nginx libpq-dev gunicorn \
      && apt-get clean \
      && rm -rf /var/lib/apt/lists/*

# # Get deploy files
# sudo mkdir -p /opt/collaborative/app \
#     || die "Failure making proc dir"
# # clear out any old templates
# sudo find /opt/collaborative/app -iname '*.html' -delete
# sudo unzip -o /tmp/collaborative.zip -d /opt/collaborative/app/ \
#     || die "Failure unzipping code"
# sudo mkdir -p /opt/collaborative/app/media/csv_uploads \
#     || die "Can't create CSV uploads directory"

# # Setup Letsencrypt
# if ! sudo ls /etc/letsencrypt/live/collaborative-test.bxroberts.org; then
#     sudo certbot -n --apache --agree-tos --email brandon@bxroberts.org \
#         -d collaborative-test.bxroberts.org \
#         || die "Failure running certbot"
# fi
# if ! sudo ls /usr/bin/certbot-posthook; then
#     sudo mv -f /opt/collaborative/app/deploy/letsencrypt/certbot-posthook \
#         /usr/bin/ \
#         || die "Failure installing certbot posthook"
# fi
# if ! sudo grep -q certbot /etc/crontab; then
#     sudo sh -c \
#         "echo '# Auto-added by collaborative deploy script' >> /etc/crontab" \
#         || die "Failure instantiating certbot cron entry"
#     sudo sh -c \
#         "cat /opt/collaborative/app/deploy/letsencrypt/crontab >> /etc/crontab" \
#         || die "Failure adding certbot cron entry"
# fi

# # Setup for our Apache app
# sudo rm -rf /etc/apache2/sites-enabled/*
# sudo mv -f /opt/collaborative/app/deploy/apache/collaborative.conf \
#     /etc/apache2/sites-available/ \
#         || die "Failure adding apache site"

# if ! [ -L /etc/apache2/sites-enabled/collaborative.conf ]; then
#     sudo ln -s /etc/apache2/sites-available/collaborative.conf \
#         /etc/apache2/sites-enabled/ \
#         || die "Failure linking apache site"
# fi

# # Python dependencies/environment
# sudo rm -rf /opt/collaborative/app/venv
# sudo find /opt/collaborative/app -iname '*.py[c|o]' -delete
# sudo find /opt/collaborative/app -iname '__pycache__' -delete

# sudo virtualenv -p $(which python3) /opt/collaborative/app/venv \
#     || die "Failure setting up Python virtualenv"
# sudo /opt/collaborative/app/venv/bin/pip install \
#     -r /opt/collaborative/app/requirements.txt \
#     || die "Failure installing Python deps"
# sudo /opt/collaborative/app/venv/bin/pip install \
#     -r /opt/collaborative/app/requirements-deploy.txt \
#     || die "Failure installing deplotment Python deps"

# # Run migrations
# sudo /opt/collaborative/app/venv/bin/python \
#     /opt/collaborative/app/manage.py migrate \
#     || die "Failure to migrate"
# sudo /opt/collaborative/app/venv/bin/python \
#     /opt/collaborative/app/manage.py collectstatic --noinput \
#     || die "Failure to gather static files"

# # Set Apache perms on everything
# sudo chown -R www-data:www-data /opt/collaborative \
#     || die "Failure setting process dir permissions"

# # Setup Apache in general
# sudo a2enmod wsgi \
#     && sudo a2enmod ssl \
#     && sudo a2enmod headers \
#     && sudo a2enmod rewrite \
#     || die "Failure installing apache mods"

# # Set UTF-8 Apache encoding, else all Django requests will explode
# sudo mv -f /opt/collaborative/app/deploy/apache/envvars \
#     /etc/apache2/envvars

# # Letsencrypt updater (using system cron)
# if ! sudo grep -q certbot /etc/crontab; then
#     sudo sh -c \
#         "echo '# Auto-added by collaborative deploy script' >> /etc/crontab" \
#         || die "Failure instantiating certbot cron entry"
#     sudo sh -c \
#         "cat /opt/collaborative/app/deploy/letsencrypt/crontab >> /etc/crontab" \
#         || die "Failure adding certbot cron entry"
# fi

# # Application crons
# sudo mv -f /opt/collaborative/app/deploy/cron/refresh_data_sources \
#     /etc/cron.d/refresh_data_sources \
#     || die "Failure to copy data refreshing cron script"
# sudo chown root:root /etc/cron.d/refresh_data_sources \
#     || die "Failure to set ownership of data refreshing cron script"
# sudo chmod 644 /etc/cron.d/refresh_data_sources \
#     || die "Failure to set perms on data refreshing cron script"

# # Logging
# sudo mv -f /opt/collaborative/app/deploy/logrotate/refresh_data_sources \
#     /etc/logrotate.d/refresh_data_sources \
#     || die "Failure to copy data refreshing logrotate config"
# sudo touch /var/log/refresh_data_sources.log \
#     || die "Unable to ensure data refresh log is available"
# sudo chown www-data /var/log/refresh_data_sources.log \
#     || die "Unable to set permissiong on data refresh log"

# # Apply everything
# sudo systemctl restart apache2

# Set env path variables used in this Dockerfile
ENV COLLABORATE_SRC=app
ENV COLLABORATE_SRVHOME=/srv
ENV COLLABORATE_SRVPROJ=$COLLABORATE_SRVHOME/$COLLABORATE_SRC
ENV PORT=8080

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
RUN git clone -b cloud-run \
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

# # Port to expose (nginx handles port 8080->8000->gunicorn)
EXPOSE 8080

ENV DJANGO_SETTINGS_MODULE "collaborative.settings"

# intend gunicorn-start to be the entrypoint command for this image
#CMD ["/gunicorn-start.sh"]
CMD exec python manage.py migrate --noinput \
    && python manage.py collectstatic --noinput\
    && gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 collaborative.wsgi
