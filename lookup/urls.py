from django.conf.urls import url
# from views import goToGoogleTop

from . import views

urlpatterns = [
    url(r'^(?P<quote>.+)/results/$', views.results, name='results')
]
