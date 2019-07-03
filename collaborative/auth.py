from social_core.backends.google import GoogleOAuth2

from collaborative.models import AppSetting


class GoogleOAuth2(GoogleOAuth2):
    def get_key_and_secret(self):
        try:
            setting = AppSetting.objects.get(name="google_oauth_credentials")
            key = setting.data.get("google_oauth_key")
            secret = setting.data.get("google_oauth_secret")
            return key, secret
        except (AttributeError, AppSetting.DoesNotExist) as e:
            pass
        return None, None
