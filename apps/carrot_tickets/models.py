from __future__ import unicode_literals
import mimetypes
from django.db.models.aggregates import Sum

from autoslug.fields import AutoSlugField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.db import models

class Project(models.Model):
    parent = models.ForeignKey('Project', null=True, blank=True)
    slug = models.SlugField()
    name = models.CharField(max_length=255)

    def full_name(self):
        if self.parent:
            return '%s/%s' % (self.parent, self.name)
        else:
            return self.name

    def __unicode__(self):
        return self.full_name()

    class Meta:
        ordering = 'slug',


class Version(models.Model):
    project = models.ForeignKey(Project)

    slug = AutoSlugField(unique_with='project__slug', populate_from='name', always_update=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()

    real_startdate = models.DateField(null=True, blank=True)
    real_enddate = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return self.name


class TicketKind(object):
    BUG = 'bug'
    TASK = 'task'

ticket_kind_choices = (
    (TicketKind.BUG, 'bug'),
    (TicketKind.TASK, 'task')
)

class TicketStatus(object):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    FIXED = 'fixed'
    DESIGN_OK = 'design_ok'
    REOPENED = 'reopened'
    CLOSED = 'closed'
    REJECTED = 'rejected'

status_choices = (
    (TicketStatus.OPEN, 'open'),
    (TicketStatus.IN_PROGRESS, 'in progress'),
    (TicketStatus.FIXED, 'fixed'),
    (TicketStatus.DESIGN_OK, 'design ok'),
    (TicketStatus.REOPENED, 'reopened'),
    (TicketStatus.CLOSED, 'closed'),
)

class Ticket(models.Model):
    project = models.ForeignKey(Project)
    fix_version = models.ForeignKey(Version)

    number = models.CharField(max_length=20, editable=False, blank=True, default=0)
    kind = models.CharField(max_length=10, choices=ticket_kind_choices, default=ticket_kind_choices[1][0])
    summary = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=30, choices=status_choices, default=status_choices[0][0])

    assignee = models.ForeignKey(User, blank=True, null=True, related_name='assignees')
    reporter = models.ForeignKey(User, related_name='reporters')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.summary

    def save(self, force_insert=False, force_update=False, using=None):
        if self.pk:
            if not self.number:
                self.number = self.pk
        super(Ticket, self).save(force_insert, force_update, using)
        if not self.number:
            self.number = self.pk
            self.save()

    def time_spent(self):
        #FIXME brokes separate carrot_timetrack project, may be unite them
        from carrot_timetrack.models import TimeLog
        return TimeLog.objects.filter(ticket__pk=self.pk).aggregate(Sum('hours'))['hours__sum'] or 0

    def is_active(self):
        """
        Is ticket timetracked now
        """
        #FIXME brokes separate carrot_timetrack project, may be unite them
        from carrot_timetrack.models import TimeLog
        return len(TimeLog.objects.filter(ticket__pk=self.pk, end=None)) != 0


class BaseAttachment(models.Model):
    kind = models.CharField(max_length=20, editable=False)
    file = models.FileField(upload_to='ticket_files')
    name = models.CharField(max_length=255, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.kind and self.file:
            mt = mimetypes.guess_type(self.file.path)[0]
            if mt and mt.split('/')[0] == 'image':
                self.kind = 'image'
            else:
                self.kind = 'file'
        if not self.name and self.file:
            self.name = self.file.name
        super(BaseAttachment, self).save(force_insert, force_update, using)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


class TicketAttachment(BaseAttachment):
    ticket = models.ForeignKey(Ticket, related_name='attachments')


class CommentKind(object):
    COMMENT = 'comment'
    COMMIT = 'commit'
    CHANGES = 'changes'

comment_kind_choices = (
    (CommentKind.COMMENT, 'comment'),
    (CommentKind.COMMIT, 'commit'),
    (CommentKind.CHANGES, 'changes'),
)

class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket)
    author = models.ForeignKey(User)

    kind = models.CharField(max_length=10, choices=comment_kind_choices, default=CommentKind.COMMENT)
    content = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created',)

    def __unicode__(self):
        return self.content[:100]