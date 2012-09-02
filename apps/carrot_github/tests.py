import datetime
from StringIO import StringIO
from django.contrib.auth.models import User
from carrot_github.models import ProjectGitHub
from carrot_github.views import github
from carrot_tickets.models import Project, Ticket, Version, TicketComment
from django.http import HttpRequest
from django.test.testcases import TestCase

test_payload = """{
  "before": "5aef35982fb2d34e9d9d4502f6ede1072793222d",
  "repository": {
    "url": "http://github.com/defunkt/github",
    "name": "github",
    "description": "You're lookin' at it.",
    "watchers": 5,
    "forks": 2,
    "private": 1,
    "owner": {
      "email": "chris@ozmm.org",
      "name": "defunkt"
    }
  },
  "commits": [
    {
      "id": "41a212ee83ca127e3c8cf465891ab7216a705f59",
      "url": "http://github.com/defunkt/github/commit/41a212ee83ca127e3c8cf465891ab7216a705f59",
      "author": {
        "email": "test1@touchin.ru",
        "name": "Chris Wanstrath"
      },
      "message": "okay i give in #1",
      "timestamp": "2008-02-15T14:57:17-08:00",
      "added": ["filepath.rb"]
    },
    {
      "id": "de8251ff97ee194a289832576287d6f8ad74e3d0",
      "url": "http://github.com/defunkt/github/commit/de8251ff97ee194a289832576287d6f8ad74e3d0",
      "author": {
        "email": "test2@touchin.ru",
        "name": "Chris Wanstrath"
      },
      "message": "update #2 pricing a tad #1",
      "timestamp": "2008-02-15T14:36:34-08:00"
    }
  ],
  "after": "de8251ff97ee194a289832576287d6f8ad74e3d0",
  "ref": "refs/heads/master"
}"""


class GitHubHookTestCase(TestCase):
    def test(self):
        project = Project.objects.create(slug='test', name='test')
        version = Version.objects.create(project=project, slug='1', name='1',
            start_date=datetime.datetime.now(), end_date=datetime.datetime.now())
        ProjectGitHub.objects.create(project=project, repo_url="http://github.com/defunkt/github")
        user1 = User.objects.create(username="test1", email="test1@touchin.ru")
        user2 = User.objects.create(username="test2", email="test2@touchin.ru")
        ticket1 = Ticket.objects.create(project=project, fix_version=version,
            number=1, summary="Ticket 1", reporter=user1)
        ticket2 = Ticket.objects.create(project=project, fix_version=version,
            number=2, summary="Ticket 2", reporter=user2)

        request = HttpRequest()
        request.method = 'POST'
        request._stream = StringIO(test_payload)
        github(request)

        self.assertEqual(TicketComment.objects.filter(ticket=ticket1).count(), 2)
        self.assertEqual(TicketComment.objects.filter(ticket=ticket2).count(), 1)
        self.assertEqual(TicketComment.objects.get(ticket=ticket2).author.pk, user2.pk)