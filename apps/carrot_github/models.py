from carrot_tickets.models import Project
from django.db import models


class ProjectGitHub(models.Model):
    project = models.ForeignKey(Project)
    repo_url = models.URLField()