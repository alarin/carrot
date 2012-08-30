from django.conf.urls import patterns, include, url

urlpatterns = patterns('carrot_tickets.views',
    url(r'^(?P<project_slug>[\w\d_-]+)/(?P<ticket_number>\d+)/$', 'ticket', name='carrot_ticket'),
    url(r'^(?P<project_slug>[\w\d_-]+)/(?P<ticket_number>\d+)/edit/$', 'ticket_edit', name='carrot_ticket_edit'),
    url(r'^new_ticket/$', 'ticket_new', name='carrot_ticket_new'),
)
