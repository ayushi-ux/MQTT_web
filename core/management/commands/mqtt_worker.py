from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
import json
import os
from core.models import MqttLog


class Command(BaseCommand):
    help = "MQTT background worker"

    def handle(self, *args, **kwargs):

        def on_connect(client, userdata, flags, rc):
            print("✅ Connected to MQTT Broker")
            client.subscribe("factory/esp32/#")

        def on_message(client, userdata, msg):
            try:
                payload = msg.payload.decode()
                data = json.loads(payload)
            except Exception:
                data = {"raw": msg.payload.decode()}

            MqttLog.objects.create(
                topic=msg.topic,
                payload=data
            )

            print(f"📩 Data saved from {msg.topic}")

        client = mqtt.Client()
        client.username_pw_set(
            os.environ.get("MQTT_USER"),
            os.environ.get("MQTT_PASS")
        )

        client.connect(
            os.environ.get("MQTT_BROKER"),
            int(os.environ.get("MQTT_PORT"))
        )

        client.on_connect = on_connect
        client.on_message = on_message

        client.loop_forever()
