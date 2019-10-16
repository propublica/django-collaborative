from social_core.backends.google import GoogleOAuth2

from django_models_from_csv.models import CredentialStore


class WhitelistedGoogleOAuth2(GoogleOAuth2):
    def setting(self, name, default=None):
        """
        Get a list of whitelisted domains from our credential store,
        if it's been saved. Otherwise ignore for all other setting types.
        """
        if name != "WHITELISTED_DOMAINS":
            return super().setting(name, default=default)
        # domains = ["domain2", ...]
        try:
            setting = CredentialStore.objects.get(name="google_oauth_credentials")
        except CredentialStore.DoesNotExist as e:
            return super().setting(name, default=default)
        creds = setting.credentials_json
        domains = creds.get("google_oauth_whitelist", default)
        if not domains:
            return domains
        return domains

    def get_key_and_secret(self):
        try:
            setting = CredentialStore.objects.get(name="google_oauth_credentials")
            creds = setting.credentials_json
            key = creds.get("google_oauth_key")
            secret = creds.get("google_oauth_secret")
            return key, secret
        except (AttributeError, CredentialStore.DoesNotExist) as e:
            pass
        return None, None
