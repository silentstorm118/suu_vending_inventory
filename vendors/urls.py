from django.urls import path

from . import views

app_name = "vendors"

urlpatterns = [
    path("", views.vendor_list, name="vendor_list"),
    path(
        "<int:vendor_id>/", views.vendor_detail, name="vendor_detail"
    ),  # New Detail Link
    path("add/", views.vendor_add, name="vendor_add"),
    path("<int:vendor_id>/edit/", views.vendor_edit, name="vendor_edit"),
    path("item/add/", views.vendor_item_add, name="vendor_item_add"),
]
