from django.urls import path, include
from .views import *

urlpatterns = [
    path("", dashboard_view, name="dashboard")
]