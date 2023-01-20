
from django.contrib import admin
from django.urls import path, include
from .views import MonoUser

urlpatterns = [
    path("user", MonoUser.as_view())
]