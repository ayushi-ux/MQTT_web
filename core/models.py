# Create your models here.
from django.db import models

class MqttLog(models.Model):
    topic = models.CharField(max_length=255)
    payload = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)  # ✅ REAL SERVER TIME

    def __str__(self):
        return f"{self.topic} @ {self.timestamp}"


