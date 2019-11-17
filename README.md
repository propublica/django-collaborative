# Collaborate

![ProPublica](https://raw.githubusercontent.com/propublica/django-collaborative/master/docs/images/ProPublica.png) ![Google News Initiative](https://raw.githubusercontent.com/propublica/django-collaborative/master/docs/images/Google-News-Initiative.png)

This is a web application for managing and building stories based on
tips solicited from the public. This project is meant to be easy to
setup for non-programmer, intuitive to use and highly extendable.

Here are a few use cases:
- Collection of data from various sources (Google Form via Google Sheets, Screendoor, Private Google Spreadsheets)
- An easy to setup data entry system
- Organizing data from multiple sources and allowing many users to view and annotate it

The project is broken up into several components:
- A system for transforming CSV files into managed database records
- A default and automatic Django admin panel built for rapid and easy editing,
  managing and browsing of data
- Customizable fields for tagging, querying, annotating and tracking tips

This is a project of [ProPublica](https://www.propublica.org/),
supported by the [Google News Initiative](https://newsinitiative.withgoogle.com/).

# Documentation

We have a GitBook with a full user guide that covers running Collaborate, importing and refining data, and setting up Google services. [You can read the documentation here.](https://propublica.gitbook.io/collaborative/)

# Deploy it

Collaborate has builtin support for one-click installs in both Google Cloud and
Heroku. During the setup process for both deployments, *make sure to
fill in the email, username and password fields so you can log in.*

## Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/propublica/django-collaborative/tree/master)

The Heroku deploy button will create a small, "free-tier" Collaborate
system. This consists of a small web server, a database which
supports between 10k-10M records (depending on data size) and
automatically configures scheduled data re-importing.

## Google Cloud

[![Run on Google Cloud](https://storage.googleapis.com/cloudrun/button.svg)](https://console.cloud.google.com/cloudshell/editor?shellonly=true&cloudshell_image=gcr.io/cloudrun/button&cloudshell_git_repo=https://github.com/propublica/django-collaborative.git&cloudshell_git_branch=cloud-run&cloudshell_working_dir=deploy/google-cloud)

The Google Cloud Run button launches Collaborate into the Google Cloud
environment. This deploy requires you to [setup a Google Project][gc-proj],
enable [Google Cloud billing][gc-bill] and enable the [Cloud Run API](gc-run).
[Full set up instructions are here][gc-docs].

This deploy does not automatically configure scheduled re-importing, but
you can add it via Cloud Scheduler by [following these instructions][gc-sched].

Once you've deployed your Cloud Run instance, you can manage your running
instance from the [Google Developer's Console][run-dashboard].

## Getting Started (Local Testing/Development)

Getting the system set up and running locally begins with cloning this
repository and installing the Python dependencies. Python 3.6 or 3.7 and Django 2.2 are assumed here.

    # virtual environment is recommended
    mkvirtualenv -p /path/to/python3.7 collaborative
    # install python dependencies
    pip install -r requirements.txt

Assuming everything worked, let's bootstrap and then start the local server:

    # get the database ready
    python manage.py migrate

    # create a default admin account
    python manage.py createsuperuser

    # gather up django and collaborate assets
    python manage.py collectstatic --noinput

    # start the local application
    python manage.py runserver

You can then access the application `http://localhost:8000` and log
in with the credentials you selected in the `createsuperuser` step
(above). Logging in will bring you to a configuration wizard where
you will import your first Google Sheet and import its contents.

## Production Deploy (Nginx/Docker)

If you want to deploy this to a production environment, we've included
configuration templates and scripts for [Docker][docker] and [Nginx][nginx].

A Collaborate `Dockerfile` (the same one used by the Google Cloud Run
deploy) can be found here:

    deploy/google-cloud/Dockerfile

This creates a basic production environment with nginx and gunicorn. By
default, it uses SQLite3, but you can configure the database by adding a
`DATABASE_URL` environment variable. You can read more about the format
for this variable [here][dj-database-url].

We also included a configuration script for plain Nginx deploys here:

    deploy/google-cloud/django_nginx.conf

This can be copied to your main Nginx sites configuration directory (e.g.,
`/etc/nginx/sites-available/`).

In order to get auto-updating data sources, make sure to add a cron job
that runs the following `manage.py` command:

    manage.py refresh_data_sources

There's an example cron file that, when added to your `/etc/crontab`, will
update data every 15 minutes:

    ./deploy/cron/refresh_data_sources

Note that if you use the above example, you probably want to add logrotate
for the logfile the above cron config adds. You can find the logrotate
script here (add it to `/etc/logrotate.d/refresh_data_sources`):

    ./deploy/logrotate/refresh_data_sources


[gc-proj]: https://console.cloud.google.com/projectselector2/home/dashboard
    "Google Cloud Project Selector"

[gc-bill]: https://cloud.google.com/billing/docs/how-to/modify-project
    "Google Cloud Billing set up"

[gc-run]: https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com,run.googleapis.com&redirect=https://console.cloud.google.com
    "Enable Google Cloud Run API"

[gc-docs]: https://cloud.google.com/run/docs/quickstarts/build-and-deploy
    "Google Cloud Run quickstart"

[gc-sched]: https://cloud.google.com/run/docs/events/using-scheduler
    "Google Cloud Scheduler"

[run-dashboard]: https://console.cloud.google.com/run
    "Google Cloud Run console"

[docker]: https://www.docker.com/get-started
    "Docker website"

[nginx]: https://nginx.org/
    "Nginx website"

[dj-database-url]: https://github.com/jacobian/dj-database-url
    "Django database environment variable instructions"
