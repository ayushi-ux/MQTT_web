# from django.core.management.base import BaseCommand
# import paho.mqtt.client as mqtt
# import json
# import os
# from core.models import MqttLog


# class Command(BaseCommand):
#     help = "MQTT background worker"

#     def handle(self, *args, **kwargs):

#         def on_connect(client, userdata, flags, rc):
#             print("✅ Connected to MQTT Broker")
#             client.subscribe("factory/esp32/#")

#         def on_message(client, userdata, msg):
#             try:
#                 payload = msg.payload.decode()
#                 data = json.loads(payload)
#             except Exception:
#                 data = {"raw": msg.payload.decode()}

#             MqttLog.objects.create(
#                 topic=msg.topic,
#                 payload=data
#             )

#             print(f"📩 Data saved from {msg.topic}")

#         client = mqtt.Client()
#         client.username_pw_set(
#             os.environ.get("MQTT_USER"),
#             os.environ.get("MQTT_PASS")
#         )

#         client.connect(
#             os.environ.get("MQTT_BROKER"),
#             int(os.environ.get("MQTT_PORT"))
#         )

#         client.on_connect = on_connect
#         client.on_message = on_message

#         client.loop_forever()




import json
import time
import os
import paho.mqtt.client as mqtt

from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import MqttLog   # confirm model name

class Command(BaseCommand):
    help = "MQTT background worker"

    def handle(self, *args, **options):
        MQTT_BROKER = os.getenv("MQTT_BROKER")
        MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
        MQTT_USERNAME = os.getenv("MQTT_USERNAME")
        MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
        MQTT_TOPIC = os.getenv("MQTT_TOPIC", "factory/esp32/#")

        def on_connect(client, userdata, flags, rc):
            self.stdout.write(self.style.SUCCESS("Connected to MQTT Broker"))
            client.subscribe(MQTT_TOPIC)

        def on_message(client, userdata, msg):
            try:
                data = json.loads(msg.payload.decode())

                MqttLog.objects.create(
                    topic=msg.topic,
                    payload=data
                )

            except Exception as e:
                self.stderr.write(str(e))

        client = mqtt.Client()
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.on_connect = on_connect
        client.on_message = on_message

        while True:
            try:
                client.connect(MQTT_BROKER, MQTT_PORT, 60)
                client.loop_forever()
            except Exception as e:
                self.stderr.write(f"MQTT Error: {e}")
                time.sleep(5)
