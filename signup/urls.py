from django.conf.urls import include, url
from django.contrib import admin

from . import signup

urlpatterns = [
    url(r'^(.*)', signup.sign_up_user)
]
