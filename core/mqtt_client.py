
import json
from datetime import datetime
import paho.mqtt.client as mqtt
from .models import MqttLog

latest_data = {}

# Topics
SENSOR_TOPIC = "factory/esp32/esp32_0/Tx_model"
WATER_TOPIC  = "factory/esp32/esp32_0/water_management_system"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe([(SENSOR_TOPIC, 0), (WATER_TOPIC, 0)])
    else:
        print("Connection failed:", rc)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        topic = msg.topic
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print("MQTT RECEIVED:", topic, payload)

        # ================= SENSOR DATA =================
        if topic == SENSOR_TOPIC:
            latest_data["esp32_0"] = {
                **payload,
                "timestamp": timestamp
            }

        # ================= WATER MANAGEMENT DATA =================
        elif topic == WATER_TOPIC:
            # Extract inputs safely
            total_height = payload.get("Total_height")
            total_volume = payload.get("Total_Volume")
            distance = payload.get("Distance")

            calculated = {}

            # Perform calculation ONLY if values exist
            if total_height and total_volume and distance is not None:
                filled_height = max(total_height - distance, 0)
                percentage = round((filled_height / total_height) * 100, 2)
                filled_volume = round((percentage / 100) * total_volume, 2)

                calculated = {
                    "Filled_height": round(filled_height, 3),
                    "Percentage": percentage,
                    "Filled_water_in_volume": filled_volume
                }

            # Merge original + calculated
            final_payload = {
                **payload,
                **calculated,
                "timestamp": timestamp
            }

            latest_data["water_management"] = final_payload

            # Save calculated payload
            MqttLog.objects.create(
                topic=topic,
                payload=final_payload
            )

            print("CALCULATED DATA:", final_payload)
            return  # ⛔ already saved

        # ================= SAVE SENSOR DATA =================
        MqttLog.objects.create(
            topic=topic,
            payload={
                **payload,
                "timestamp": timestamp
            }
        )

        print("SAVED TO DB")

    except Exception as e:
        print("MQTT ERROR:", e)



def start_mqtt():
    client = mqtt.Client(client_id="django-subscriber")

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("broker.emqx.io", 1883, 60)
    client.loop_start()
