from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from registration.forms import RegistrationFormUniqueEmail
# Uncomment the next two lines to enable the admin: 
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'freemex.views.home', name='home'),
    # url(r'^freemex/', include('freemex.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
	url(r'^test/','login.views.main'),
	url(r'^mailtest/$','login.views.mailtest'),
#	url(r'^checklogin/$','login.views.logincheck'),
	url(r'^bid/$','transaction.views.bidcheck'),
	url(r'^sell/$','transaction.views.offercheck'),
	url(r'^portfolio/$','login.views.portfolio'),
	url(r'^marketwatch/$','login.views.marketwatch'),
	url(r'^history/$','login.views.history'),
	url(r'^leaderboard/$','login.views.leader'),
	url(r'^offermodify/$','transaction.views.offermodify'),
	url(r'^bidmodify/$','transaction.views.bidmodify'),
	url(r'^deletebid/$','transaction.views.deletebid'),
	url(r'^deleteoffer/$','transaction.views.deleteoffer'),
	url(r'^analysis/$','login.views.analysis'),
#	url(r'^logout/$','login.views.logout'),
	url(r'^$','login.views.main'),
	url(r'^marquee/$','login.views.marqueecontent'),
	url(r'^notification/$','login.views.notify'),
	url(r'^faq/$','login.views.faq'),
	url(r'^accounts/register/$', 'registration.views.register',{'form_class': RegistrationFormUniqueEmail,
     'backend': 'registration.backends.default.DefaultBackend'}, name='registration_register'),
	url(r'^accounts/', include('registration.backends.default.urls')),
	url(r'^eod/$','login.views.eod'),
	url(r'^eodpage/$','login.views.eodpage'),
#	url(r'^','login.views.main'),
	
)



urlpatterns += staticfiles_urlpatterns()
