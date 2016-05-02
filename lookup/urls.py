from django.conf.urls import url
# from views import goToGoogleTop

from . import views

urlpatterns = [
    url(r'^(?P<quote>.+)/results/$', views.results, name='results'),
    url(r'^(?P<quote>.+)/earliest/$', views.googleEarliest, name='earliest'),

    url(r'^auth/$', views.authenticate, name='authenticate'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^toggledomain/(?P<d>.+)/$', views.toggleDomain, name='domain_toggle'),
    url(r'^getvaliddomains/$', views.getValidDomains, name='domain_lookup'),
    url(r'^gethistory/$', views.getHistory, name='get_history'),
    
    url(r'^gethighlightedstate/$', views.getHighlightingState, name='get_highlighting_state'),
    url(r'^sethighlightedstate/(?P<state>.+)/$', views.setHighlightingState, name='set_highlighting_state'),
    
    url(r'^addtrustedsource/(?P<trusted>.+)/$', views.addTrustedSource, name='add_trusted_source'),
    url(r'^toggletrustedsource/(?P<trusted>.+)/$', views.toggleTrustedSource, name='toggle_trusted_source'),
    url(r'^removetrustedsource/(?P<trusted>.+)/$', views.removeTrustedSource, name='remove_trusted_source'),
    
    url(r'^adduntrustedsource/(?P<untrusted>.+)/$', views.addUntrustedSource, name='add_untrusted_source'),
    url(r'^toggleuntrustedsource/(?P<untrusted>.+)/$', views.toggleUntrustedSource, name='toggle_untrusted_source'),
    url(r'^removeuntrustedsource/(?P<untrusted>.+)/$', views.removeUntrustedSource, name='remove_untrusted_source'),
    
    url(r'^gettrustedsources/$', views.getTrustedSources, name='get_trusted_sources'),
    url(r'^getuntrustedsources/$', views.getUntrustedSources, name='get_untrusted_sources')
]
