
from django.db import models
from django.apps import AppConfig

class Config(AppConfig):
    default_auto_field = 'django.db.models.AutoField'  # Opsiyonel
    name = 'mlops_services'

class LiveActivity(models.Model):
    event_title = models.CharField(max_length=255)
    upper_category = models.CharField(max_length=255)
    lower_category = models.CharField(max_length=255)
    date = models.DateTimeField()
    start_time = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    class Meta:
        app_label = "mlops_services"
        db_table = 'live_activity'
        managed = False