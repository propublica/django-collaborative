# Collaborative Tip Gathering

This is a web application for managing and building stories based on
tips solicited from the public. This project is meant to be easy to
setup, intuitive to use and highly extendable for non-programmers and
experts alike.

The project is broken up into several components:
- A system for transforming CSV files (Google Sheets links) into
  managed database records.
- Customizable fields for tagging, querying, annotating and tracking tips.
- A "one-click", turnkey deployment option for Google Application Engine.

![Google News Initiative](https://raw.githubusercontent.com/propublica/django-collaborative/master/docs/images/Google-News-Initiative.png)

![ProPublica](https://raw.githubusercontent.com/propublica/django-collaborative/master/docs/images/ProPublica.png)

This is a project of [ProPublica](https://www.propublica.org/),
supported by the [Google News Initiative](https://newsinitiative.withgoogle.com/).

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
