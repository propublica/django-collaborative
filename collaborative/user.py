import logging

from django.conf import settings
from django.contrib.auth.models import User
from social_core.exceptions import AuthForbidden, AuthException
from social_core.pipeline.partial import partial

from django_models_from_csv.models import CredentialStore


logger = logging.getLogger(__name__)


def set_staff_status(user, *args, **kwargs):
    """
    Users need to be staff in order to use the Django Admin. Hence,
    all users who log into the system ought to be staff. We use this
    in the social login pipeline to give users this privilege.
    """
    if user and not user.is_staff:
        user.is_staff = True
        user.save()


def user_email_in_whitelist(email, domains):
    """
    Check to see if a user's email address is within one of
    the whitelisted domains. Only returns True if an explicit
    match has been found. This matching is case-insensitive.

    NOTE: This routine is a critical security function.
    """
    allowed = False
    lower_domains = [d.strip().lower() for d in domains if d.strip()]
    if email and lower_domains:
        domain = email.split('@', 1)[1]
        allowed = domain.lower() in lower_domains
    return allowed


def create_user_in_domain_whitelist(user, response, backend,
                                    details, *args, **kwargs):
    oauth_creds_model = CredentialStore.objects.filter(
        name="google_oauth_credentials"
    ).first()

    # don't do anything if we don't have credentials
    if not oauth_creds_model:
        return

    # decode our credentials
    try:
        credentials = oauth_creds_model.credentials_json
    except Exception as e:
        logger.error("Exception decoding credentials JSON: %s" % (e))
        return

    # don't do anything if we don't have a whitelist or a email
    whitelist = credentials.get("google_oauth_whitelist", [])
    email = details.get("email")
    if not whitelist or not email:
        return

    # do everything off a lower-cased email
    l_email = email.lower()

    # check the domain (this is the same routing that social core uses,
    # but we've removed the ability for non-whitelisted users to make
    # it past here)
    if not user_email_in_whitelist(l_email, whitelist):
        logger.debug("Rejecting email=%s not in domain whitelist=%s" % (
            l_email, whitelist
        ))
        return

    # check to see if the user exists, if so don't mess with it
    user, created = User.objects.get_or_create(username=l_email)
    if not created:
        return

    # create a new user with the email as username, with unusable password
    # and the requested email field. staff status/etc will get handed with
    # the post-save hook.
    user.email = l_email
    user.set_unusable_password()
    user.save()


@partial
def associate_by_email_or_pause(strategy, details, user=None, backend=None,
                                is_new=False, *args, **kwargs):
    """
    Associate current auth with a user with the same email address in the DB.

    This pipeline entry is not 100% secure unless you know that the providers
    enabled enforce email verification on their side, otherwise a user can
    attempt to take over another user account by using the same (not validated)
    email address on some provider.  This pipeline entry is disabled by
    default.

    We redirect the user to a access denied page where they can resume the
    login in the case an admin grants them access.
    """
    if user:
        return None

    email = details.get('email')
    if email:
        # Try to associate accounts registered with the same email address,
        # only if it's a single object. AuthException is raised if multiple
        # objects are returned.
        users = list(strategy.storage.user.get_users_by_email(email))
        if len(users) == 0:
            # Redirect to an error page notifying user their email hasn't
            # been added by the admins. This page can be re-visited once the
            # user account has been added to the system.
            current_partial = kwargs.get('current_partial')
            return strategy.redirect(
                '/request-access?partial_token={0}&backend={1}'.format(
                    current_partial.token, backend.name
                ))
        elif len(users) > 1:
            raise AuthException(
                backend,
                'The given email address is associated with another account'
            )
        else:
            return {'user': users[0],
                    'is_new': False}


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
