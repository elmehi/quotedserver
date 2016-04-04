from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^(?P<quote>[A-Z]+)/results/$', views.results, name='results')
]
