from django.conf.urls import patterns, include, url

urlpatterns = patterns('carrot_github.views',
    url(r'^github/$', 'github'),
)
