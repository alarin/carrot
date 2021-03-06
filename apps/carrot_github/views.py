import json
import urllib
from carrot_tickets.models import TicketComment, Ticket, CommentKind
from django.contrib.auth.models import User
from carrot_github.models import ProjectGitHub
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re

RE_TICKET_NUMBER = re.compile("#(\d+)")

COMMENT_TEXT = "%(url)s\n\n%(message)s"

@csrf_exempt
def github(request):
    """
    Process github service hook.
    https://help.github.com/articles/post-receive-hooks

    Mostly create ticket comments
    """
    if request.method == 'GET':
        return HttpResponse('Carrot GitHub hook url. See more at <a href="https://help.github.com/articles/post-receive-hooks">https://help.github.com/articles/post-receive-hooks</a>')

    if request.method == 'POST':
        jsonpayload = urllib.unquote(request.read().split('=')[1])
        payload = json.loads(jsonpayload)
        project = ProjectGitHub.objects.filter(repo_url=payload['repository']['url'])
        if not project:
            raise Exception('Project with url %s not found' % payload['repository']['url'])
            #return HttpResponse('Project with url %s not found' % payload['repository']['url'])
        else:
            project = project[0].project

        for commit in payload['commits']:
            #I want receive User.DoesNotFound exceptions on my mail to fix it
            email = commit['author']['email']
            author = User.objects.get(Q(email=email) | Q(carrotprofile__emails__icontains=email))
            ticket_ids = [match.group(1) for match in RE_TICKET_NUMBER.finditer(commit['message'])]

            found_tickets = Ticket.objects.filter(Q(project=project)|Q(project__parent=project))\
                .filter(number__in=ticket_ids)
            for ticket in found_tickets:
                TicketComment.objects.create(ticket=ticket, author=author, kind=CommentKind.COMMIT,
                    content = COMMENT_TEXT % commit)

            if not len(found_tickets):
                raise Exception('No tickets %s, %s, %s' % (author, project, ticket_ids))

        return HttpResponse('ok')

    raise Exception('Unsupported request method %s' % request.method)


