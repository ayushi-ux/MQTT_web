from django.shortcuts import render
from django.http import JsonResponse
from .mqtt_client import latest_data
from .models import MqttLog   # 👈 ADD THIS IMPORT


def mqtt_data(request):
    log = MqttLog.objects.order_by("-id").first()

    if not log:
        return JsonResponse({})

    local_ts = timezone.localtime(log.timestamp)  # ✅ convert to IST

    return JsonResponse({
        "esp32_0": {
            **log.payload,
            "timestamp": local_ts.strftime("%Y-%m-%d %H:%M:%S")
        }
    })



# ===== EXISTING PAGE VIEW (UNCHANGED) =====
def index(request):
    return render(request, "index.html")


from django.http import JsonResponse
from django.utils import timezone
from collections import defaultdict
from .models import MqttLog

def graph_data(request):
    logs = MqttLog.objects.order_by("timestamp")

    buckets = defaultdict(lambda: {
        "temp": [],
        "hum": [],
        "light": []
    })

    for log in logs:
        t = timezone.localtime(log.timestamp).strftime("%H:%M")

        payload = log.payload or {}
        buckets[t]["temp"].append(payload.get("Temperature"))
        buckets[t]["hum"].append(payload.get("Humidity"))
        buckets[t]["light"].append(payload.get("Light Sensor"))

    labels, temperature, humidity, light = [], [], [], []

    for t, values in buckets.items():
        labels.append(t)

        valid_temp = [v for v in values["temp"] if v is not None]
        valid_hum = [v for v in values["hum"] if v is not None]
        valid_light = [v for v in values["light"] if v is not None]

        temperature.append(sum(valid_temp) / len(valid_temp) if valid_temp else None)
        humidity.append(sum(valid_hum) / len(valid_hum) if valid_hum else None)
        light.append(sum(valid_light) / len(valid_light) if valid_light else None)

    return JsonResponse({
        "labels": labels,
        "temperature": temperature,
        "humidity": humidity,
        "light": light,
    })


from django.shortcuts import render
from django.utils import timezone
from .models import MqttLog

def continuous_data(request):
    logs = MqttLog.objects.order_by("-timestamp")[:100]

    rows = []
    for log in logs:
        payload = log.payload or {}

        rows.append({
            "timestamp": timezone.localtime(log.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": payload.get("Temperature"),
            "humidity": payload.get("Humidity"),
            "light": payload.get("Light Sensor"),
        })

    return render(request, "continuous_data.html", {"rows": rows})



from django.http import JsonResponse
from django.utils import timezone
from .models import MqttLog

def live_sensor_data(request):
    logs = MqttLog.objects.order_by("-timestamp")[:100]

    data = []
    for log in logs:
        payload = log.payload or {}

        data.append({
            "timestamp": timezone.localtime(log.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": payload.get("Temperature"),
            "humidity": payload.get("Humidity"),
            "light": payload.get("Light Sensor"),
        })

    return JsonResponse({"data": data})