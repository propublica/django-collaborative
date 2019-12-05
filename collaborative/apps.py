import logging
from django.apps import AppConfig
from django.db.utils import OperationalError


logger = logging.getLogger(__name__)


class CollabConfig(AppConfig):
    name = "collaborative"
    verbose_name = "Collaborative Tip-Gathering System"

    def ready(self):
        """
        This runs when our app has all of its models registered, including
        django ones. So now we can run our signals, which depend on the
        models being registered.
        """
        import collaborative.signals
        try:
            collaborative.signals.setup_dynmodel_signals()
        except OperationalError as e:
            logger.debug("[!] Skipping operational error: %s" % (e))
        except Exception as e:
            logger.error("[!] Error loading signals: %s" % (e))
