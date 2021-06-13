from django.apps import AppConfig


class HoldersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'holders'

    class Meta:
        app_label = 'holders'

    def ready(self):
        from .signals import save_in_read_only_db  # noqa
