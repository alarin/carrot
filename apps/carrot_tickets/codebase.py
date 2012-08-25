"""
Codebase (codebasehq.com) API wrapper
"""
import json
from urllib import urlencode
import urllib2

from django.conf import settings


base_url = 'http://api3.codebasehq.com/'

def codebase_query(url):
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(
        realm='Application',
        uri=base_url,
        user=settings.CARROT_CODEBASE_USERNAME,
        passwd=settings.CARROT_CODEBASE_KEY)
    opener = urllib2.build_opener(auth_handler)
    opener.addheaders = [('Content-type', 'application/json'), ('Accept', 'application/json')]
    response = opener.open(base_url + url).read()
    parsed = json.loads(response)
    return parsed


def tickets(project, milestone=None, query=None):
    url = '/%s/tickets' % project
    params = {}
    if query:
        params['query'] = query

# MILESTONE filtering not working :(
#    elif milestone:
#        url += '?query=milestone:%s' % milestone
    tickets = []
    try:
        page = 1
        while True:
            params['page'] = page
            tickets += codebase_query(url + '?' + urlencode(params))
            page += 1
    except urllib2.HTTPError:
        pass

    if milestone:
        tickets = [ticket for ticket in tickets if unicode(ticket['ticket']['milestone_id']) == milestone]
    return tickets


def ticket_notes(project, ticket_id):
    return codebase_query('/%s/tickets/%s/notes' % (project, ticket_id))


def milestones(project):
    return codebase_query('/%s/milestones' % project)
