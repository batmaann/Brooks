from django.apps import AppConfig


class ForgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forge'

    def ready(self):
        from forge import signals  # noqa: F401
