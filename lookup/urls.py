from django.conf.urls import url

from . import views

urlpatterns = [
	# url(r'^$', views.index, name='index'),
    url(r'^(?P<quote>[a-z]+)/results/$', views.results) #, name='results')
]
