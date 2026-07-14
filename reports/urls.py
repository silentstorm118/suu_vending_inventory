from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("generate/", views.generate_low_stock_report, name="generate_report"),
]
