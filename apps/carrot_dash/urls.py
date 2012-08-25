from django.conf.urls import patterns, include, url

urlpatterns = patterns('carrot_dash.views',
    url(r'^/$', 'home', name='carrot_home'),
    url(r'^/dash/developer$', 'dash_developer', name='dash_developer'),
    url(r'^/dash/pm$', 'dash_pm', name='dash_pm'),
    url(r'^/dash/qa$', 'dash_qa', name='dash_qa'),
    url(r'^/dash/designer$', 'dash_designer', name='dash_designer'),
)
