# Django Collaborative

![Google News Initiative](https://raw.githubusercontent.com/propublica/django-collaborative/master/docs/images/Google-News-Initiative.png)

![ProPublica](https://raw.githubusercontent.com/propublica/django-collaborative/master/docs/images/ProPublica.png)


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

# Deploy it
 [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/propublica/django-collaborative/tree/master)

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
    # start the local application
    python manage.py runserver

You can then access the application `http://localhost:8000` and log
in with the credentials you selected in the `createsuperuser` step
(above). Logging in will bring you to a configuration wizard where
you will import your first Google Sheet and import its contents.
