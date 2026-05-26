from django.apps import AppConfig


class SecretariaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.secretaria'
    verbose_name = 'Secretaría'

    def ready(self):
        try:
            from apps.secretaria.scheduler import start
            start()
        except Exception:
            pass
