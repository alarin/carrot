from __future__ import unicode_literals

from autoslug.fields import AutoSlugField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    parent = models.ForeignKey('Project', null=True, blank=True)
    slug = models.SlugField()
    name = models.CharField(max_length=255)

    def __unicode__(self):
        if self.parent:
            return '%s -- %s' % (self.parent, self.name)
        else:
            return self.name


class Version(models.Model):
    project = models.ForeignKey(Project)

    slug = AutoSlugField(unique_with='project__slug', populate_from='name', always_update=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()

    def __unicode__(self):
        return self.name


class TicketKind(object):
    BUG = 'bug'
    TASK = 'task'

ticket_kind_choices = (
    (TicketKind.BUG, 'bug'),
    (TicketKind.TASK, 'task')
)

class Ticket(models.Model):
    project = models.ForeignKey(Project)
    fix_version = models.ForeignKey(Version)

    kind = models.CharField(max_length=10, choices=ticket_kind_choices, default=ticket_kind_choices[0][1])
    summary = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    assignee = models.ForeignKey(User, blank=True, null=True, related_name='assignees')
    reporter = models.ForeignKey(User, related_name='reporters')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Attachment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    file = models.FileField(upload_to='ticket_files')
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name
