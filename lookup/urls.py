from django.conf.urls import url
# from views import goToGoogleTop

from . import views

urlpatterns = [
    url(r'^(?P<quote>.+)/results/$', views.results, name='results'),
    url(r'^auth/$', views.authenticate, name='authenticate'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^toggledomain/(?P<d>.+)/$', views.toggleDomain, name='domain_toggle'),
    url(r'^getvaliddomains/$', views.getValidDomains, name='domain_lookup'),
    url(r'^gethistory/$', views.getHistory, name='get_history'),
    url(r'^gethighlightingstate/$', views.getHighlightingState, name='get_highlighting_state')
]
