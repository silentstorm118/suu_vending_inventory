from django.urls import path, include
from .views import *

app_name: str = "dashboard"

urlpatterns = [
    path("", dashboard_view, name="dashboard")
]