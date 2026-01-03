from django.contrib import admin
from django.contrib import admin
from .models import MqttLog


@admin.register(MqttLog)
class MqttLogAdmin(admin.ModelAdmin):
    list_display = ("topic", "timestamp")
    list_filter = ("topic",)
    search_fields = ("topic",)
    ordering = ("-timestamp",)