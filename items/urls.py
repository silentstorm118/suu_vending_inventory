from django.urls import path, include
from .views import *

app_name = "items"

urlpatterns = [
    path("", item_list, name="item_list"),
    path("update/<int:item_id>", update_backroom, name="update_backroom"),
    path("create/", create_product, name="create_product")
]