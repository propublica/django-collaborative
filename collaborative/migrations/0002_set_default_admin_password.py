import logging
import os

from django.db import migrations
from django.contrib.auth.hashers import make_password


logger = logging.getLogger(__name__)


def forwards(apps, schema_editor):
    username = os.getenv("COLLAB_DEFAULT_USERNAME", "admin")
    email = os.getenv("COLLAB_DEFAULT_EMAIL")
    password = os.getenv("COLLAB_DEFAULT_PASSWORD")
    User = apps.get_model("auth", "User")
    # Don't create a new admin account if users exist (this means
    # the user has already gone through the user config or that
    # they have ran createsuperuser)
    if User.objects.count() > 0:
        logger.info("Users exist! Not creating default admin")
        return
    # Don't create blank passwords!
    if not password:
        logger.info("Password not set in environment. Bailing.")
        return
    logger.info("Creating default user=%s email=%s pass=%s" % (
        username, email, "*****" if password else "(Blank pass)"
    ))
    user = User(
        username=username,
        email=email,
        password=make_password(password),
        is_staff=True,
    )
    user.save()


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('collaborative', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
