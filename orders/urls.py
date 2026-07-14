from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("add/", views.order_add, name="order_add"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("receive/<int:order_id>/", views.receive_order, name="receive_order"),
]
