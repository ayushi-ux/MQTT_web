from django.urls import path
from .views import mqtt_data, index, graph_data,continuous_data

urlpatterns = [
    path("", index),            # Web dashboard
    path("api/data/", mqtt_data),  # API endpoint
    path("api/graph-data/", graph_data),
    path("continuous-data/", continuous_data, name="continuous_data"),
    
]
