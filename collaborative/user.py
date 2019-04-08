from django.conf import settings
from social_core.exceptions import AuthForbidden


def set_staff_status(user, *args, **kwargs):
    """
    Users need to be staff in order to use the Django Admin. Hence,
    all users who log into the system ought to be staff. We use this
    in the social login pipeline to give users this privilege.
    """
    user.is_staff = True
    user.save()


def enforce_slack_team(user, response, backend, details, *args, **kwargs):
    """
    If using slack sign in, make sure users are logging in using
    the specified slack team.
    """
    # TODO: make this a generic check for all the supported social
    # sign in methods
    if backend.name == "slack":
        slack_team = response.get('team', {})
        slack_team_id = slack_team.get('id')
        if not slack_team or not slack_team_id:
            return
        if slack_team_id != settings.SOCIAL_AUTH_SLACK_TEAM:
            raise AuthForbidden(backend)

