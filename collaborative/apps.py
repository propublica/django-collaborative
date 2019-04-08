from django.apps import AppConfig

class CollabConfig(AppConfig):
    name = "collaborative"
    verbose_name = "Collaborative Tip-Gathering System"

    def ready(self):
        import collaborative.signals
