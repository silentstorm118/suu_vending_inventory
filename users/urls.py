from django.urls import path, include
from .views import *

app_name = "users"

urlpatterns = [
    path("", user_list, name="user_list"),
    path("<int:pk>/edit/", user_edit, name="user_edit"),
    path("<int:pk>/delete/", user_delete, name="user_delete"),
]