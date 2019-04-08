from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from collaborative.user import set_staff_status


@receiver(post_save, sender=User)
def ensure_staff(sender, **kwargs):
    """
    Give users staff status (so they can see the Admin) if
    they are able to log in.
    """
    user = kwargs.get("instance")
    if user and not user.is_staff:
        set_staff_status(user)
