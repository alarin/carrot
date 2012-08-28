import django
from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout

urlpatterns = patterns('carrot_dash.views',
    url(r'^$', 'home', name='carrot_home'),
    url(r'^/dash/developer$', 'dash_developer', name='dash_developer'),
    url(r'^/dash/pm$', 'dash_pm', name='dash_pm'),
    url(r'^/dash/qa$', 'dash_qa', name='dash_qa'),
    url(r'^/dash/designer$', 'dash_designer', name='dash_designer'),

    url(r'^logout/$', 'logout_view', name='carrot_logout'),
    url(r'^login/$', 'login_view', name='carrol_login')
)
