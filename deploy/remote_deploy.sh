#!/bin/bash
die () {
    echo ${*}
    exit 1
}

# Stop running process
sudo systemctl stop apache2

# System dependencies
sudo apt update
sudo apt -y install apache2 libapache2-mod-wsgi-py3 libapache2-mod-nss \
    letsencrypt python3-certbot-apache unzip \
    python3 python3-virtualenv virtualenv || die "Failure installing system deps"

# Get deploy files
sudo mkdir -p /opt/collaborative/app \
    || die "Failure making proc dir"
sudo unzip -o /tmp/collaborative.zip -d /opt/collaborative/app/ \
    || die "Failure unzipping code"

# Setup Letsencrypt
if ! sudo ls /etc/letsencrypt/live/collaborative-test.bxroberts.org; then
    sudo certbot -n --apache --agree-tos --email brandon@bxroberts.org \
        -d collaborative-test.bxroberts.org \
        || die "Failure running certbot"
fi
if ! sudo ls /usr/bin/certbot-posthook; then
    sudo mv -f /opt/collaborative/app/deploy/letsencrypt/certbot-posthook \
        /usr/bin/ \
        || die "Failure installing certbot posthook"
fi
if ! sudo grep -q certbot /etc/crontab; then
    sudo sh -c \
        "echo '# Auto-added by collaborative deploy script' >> /etc/crontab" \
        || die "Failure instantiating certbot cron entry"
    sudo sh -c \
        "cat /opt/collaborative/app/deploy/letsencrypt/crontab >> /etc/crontab" \
        || die "Failure adding certbot cron entry"
fi

# Setup for our Apache app
sudo rm -rf /etc/apache2/sites-enabled/*
sudo mv -f /opt/collaborative/app/deploy/apache/collaborative.conf \
    /etc/apache2/sites-available/ \
        || die "Failure adding apache site"

if ! [ -L /etc/apache2/sites-enabled/collaborative.conf ]; then
    sudo ln -s /etc/apache2/sites-available/collaborative.conf \
        /etc/apache2/sites-enabled/ \
        || die "Failure linking apache site"
fi

# Python dependencies/environment
sudo virtualenv -p $(which python3) /opt/collaborative/app/venv \
    || die "Failure setting up Python virtualenv"
sudo /opt/collaborative/app/venv/bin/pip install \
    -r /opt/collaborative/app/requirements.txt \
    || die "Failure installing Python deps"
sudo /opt/collaborative/app/venv/bin/pip install \
    -r /opt/collaborative/app/requirements-deploy.txt \
    || die "Failure installing deplotment Python deps"

# Run migrations
sudo /opt/collaborative/app/venv/bin/python \
    /opt/collaborative/app/manage.py migrate \
    || die "Failure to migrate"
sudo /opt/collaborative/app/venv/bin/python \
    /opt/collaborative/app/manage.py collectstatic --noinput \
    || die "Failure to gather static files"

# Set Apache perms on everything
sudo chown -R www-data:www-data /opt/collaborative \
    || die "Failure setting process dir permissions"

# Setup Apache in general
sudo a2enmod wsgi \
    && sudo a2enmod ssl \
    && sudo a2enmod headers \
    || die "Failure installing apache mods"

# Good to go!
sudo systemctl restart apache2
