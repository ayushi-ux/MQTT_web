# # #///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# from django.shortcuts import render
# from django.http import JsonResponse
# from .mqtt_client import latest_data
# from .models import MqttLog   # 👈 ADD THIS IMPORT

# def mqtt_data(request):
#     log = MqttLog.objects.order_by("-id").first()

#     if not log:
#         return JsonResponse({})

#     local_ts = timezone.localtime(log.timestamp)  # ✅ convert to IST

#     return JsonResponse({
#         "esp32_0": {
#             **log.payload,
#             "timestamp": local_ts.strftime("%Y-%m-%d %H:%M:%S")
#         }
#     })



# # ===== EXISTING PAGE VIEW (UNCHANGED) =====
# def index(request):
#     return render(request, "index.html")


# from django.http import JsonResponse
# from django.utils import timezone
# from collections import defaultdict
# from .models import MqttLog

# def graph_data(request):
#     logs = MqttLog.objects.order_by("timestamp")

#     buckets = defaultdict(lambda: {
#         "temp": [],
#         "hum": [],
#         "light": []
#     })

#     for log in logs:
#         t = timezone.localtime(log.timestamp).strftime("%H:%M")

#         payload = log.payload or {}
#         buckets[t]["temp"].append(payload.get("Temperature"))
#         buckets[t]["hum"].append(payload.get("Humidity"))
#         buckets[t]["light"].append(payload.get("Light Sensor"))

#     labels, temperature, humidity, light = [], [], [], []

#     for t, values in buckets.items():
#         labels.append(t)

#         valid_temp = [v for v in values["temp"] if v is not None]
#         valid_hum = [v for v in values["hum"] if v is not None]
#         valid_light = [v for v in values["light"] if v is not None]

#         temperature.append(sum(valid_temp) / len(valid_temp) if valid_temp else None)
#         humidity.append(sum(valid_hum) / len(valid_hum) if valid_hum else None)
#         light.append(sum(valid_light) / len(valid_light) if valid_light else None)

#     return JsonResponse({
#         "labels": labels,
#         "temperature": temperature,
#         "humidity": humidity,
#         "light": light,
#     })


# from django.shortcuts import render
# from django.utils import timezone
# from .models import MqttLog

# def continuous_data(request):
#     logs = MqttLog.objects.order_by("-timestamp")[:100]

#     rows = []
#     for log in logs:
#         payload = log.payload or {}

#         rows.append({
#             "timestamp": timezone.localtime(log.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
#             "temperature": payload.get("Temperature"),
#             "humidity": payload.get("Humidity"),
#             "light": payload.get("Light Sensor"),
#         })

#     return render(request, "continuous_data.html", {"rows": rows})



# from django.http import JsonResponse
# from django.utils import timezone
# from .models import MqttLog

# def live_sensor_data(request):
#     logs = MqttLog.objects.order_by("-timestamp")[:100]

#     data = []
#     for log in logs:
#         payload = log.payload or {}

#         data.append({
#             "timestamp": timezone.localtime(log.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
#             "temperature": payload.get("Temperature"),
#             "humidity": payload.get("Humidity"),
#             "light": payload.get("Light Sensor"),
#         })

#     return JsonResponse({"data": data})


from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from collections import defaultdict
from .models import MqttLog

# ======================================================
# 1. LATEST SENSOR DATA (FOR DASHBOARD CARDS)
# ======================================================
# from django.http import JsonResponse
# from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.db import connection   # 👈 REQUIRED
# from .models import MqttLog

@never_cache
def mqtt_data(request):
    # 🔥 Force Django to reopen DB connection
    connection.close()

    log = MqttLog.objects.order_by("-id").first()

    if not log:
        return JsonResponse({})

    payload = log.payload or {}

    return JsonResponse({
        "esp32_0": {
            "Temperature": payload.get("Temperature"),
            "Humidity": payload.get("Humidity"),
            "Light": payload.get("Light"),
            "timestamp": timezone.localtime(log.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        }
    })


# ======================================================
# 2. DASHBOARD PAGE
# ======================================================
def index(request):
    return render(request, "index.html")


# ======================================================
# 3. GRAPH DATA (LIMITED + SAFE)
# ======================================================

@never_cache
def graph_data(request):
    # 🔥 FORCE fresh DB connection
    connection.close()

    logs = list(
        MqttLog.objects.order_by("-id")[:300]
    )[::-1]   # reverse for correct time order

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
        buckets[t]["light"].append(payload.get("Light"))

    labels, temperature, humidity, light = [], [], [], []

    for t in buckets:
        labels.append(t)

        temp_vals = [v for v in buckets[t]["temp"] if v is not None]
        hum_vals = [v for v in buckets[t]["hum"] if v is not None]
        light_vals = [v for v in buckets[t]["light"] if v is not None]

        temperature.append(sum(temp_vals) / len(temp_vals) if temp_vals else None)
        humidity.append(sum(hum_vals) / len(hum_vals) if hum_vals else None)
        light.append(sum(light_vals) / len(light_vals) if light_vals else None)

    return JsonResponse({
        "labels": labels,
        "temperature": temperature,
        "humidity": humidity,
        "light": light,
    })


# ======================================================
# 4. TABLE VIEW (LAST 100 ROWS)
# ======================================================
def continuous_data(request):
    logs = MqttLog.objects.order_by("-id")[:100]

    rows = []
    for log in logs:
        payload = log.payload or {}
        rows.append({
            "timestamp": timezone.localtime(log.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": payload.get("Temperature"),
            "humidity": payload.get("Humidity"),
            "light": payload.get("Light"),
        })

    return render(request, "continuous_data.html", {"rows": rows})


# ======================================================
# 5. API FOR LIVE AUTO-REFRESH (OPTIONAL)
# ======================================================
def live_sensor_data(request):
    logs = MqttLog.objects.order_by("-id")[:100]

    data = []
    for log in logs:
        payload = log.payload or {}
        data.append({
            "timestamp": timezone.localtime(log.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": payload.get("Temperature"),
            "humidity": payload.get("Humidity"),
            "light": payload.get("Light"),
        })

    return JsonResponse({"data": data})
