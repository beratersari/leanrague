from django.apps import AppConfig


class ModelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.models'
    verbose_name = 'Models'
    
    def ready(self):
        pass  # Models are auto-discovered
