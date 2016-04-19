from django.conf.urls import include, url
from django.contrib import admin

from . import auth

urlpatterns = [
    url(r'^(.*)', auth.authenticate)
]
