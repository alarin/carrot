import json
from carrot_tickets.models import TicketComment, Ticket, CommentKind
from django.contrib.auth.models import User
from carrot_github.models import ProjectGitHub
from django.db.models.query_utils import Q
from django.http import HttpResponse
import re

RE_TICKET_NUMBER = re.compile("#([\d+])")

COMMENT_TEXT = r"%(url)s\n\n%(message)s"

def github(request):
    """
    Process github service hook.
    https://help.github.com/articles/post-receive-hooks

    Mostly create ticket comments
    """
    if request.method == 'GET':
        return HttpResponse('Carrot GitHub hook url. See more at <a href="https://help.github.com/articles/post-receive-hooks">https://help.github.com/articles/post-receive-hooks</a>')

    if request.method == 'POST':
        payload = json.loads(request.read())

        project = ProjectGitHub.objects.filter(repo_url=payload['repository']['url'])
        if not project:
            return HttpResponse('Project with url %s not found' % payload['repository']['url'])
        else:
            project = project[0].project

        for commit in payload['commits']:
            #I want receive User.DoesNotFound exceptions on my mail to fix it
            author = User.objects.get(email=commit['author']['email'])
            ticket_ids = [match.group(1) for match in RE_TICKET_NUMBER.finditer(commit['message'])]
            for ticket in Ticket.objects.filter(Q(project=project)|Q(project__parent=project))\
                .filter(pk__in=ticket_ids):
                TicketComment.objects.create(ticket=ticket, author=author, kind=CommentKind.COMMIT,
                    content = COMMENT_TEXT % commit)

        return HttpResponse('ok')


