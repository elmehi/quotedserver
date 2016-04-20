from django.conf.urls import url
# from views import goToGoogleTop

from . import views

urlpatterns = [
    url(r'^(?P<quote>.+)/results/$', views.results, name='results'),
    url(r'^auth/$', views.authenticate, name='authenticate'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^toggledomain/(?P<domain>.+)/$', views.toggleDomain, name='domain_toggle')
]
