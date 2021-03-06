from __future__ import unicode_literals
from annoying.fields import AutoOneToOneField
from carrot_tickets.models import Project, Ticket

from django.db import models
from django.contrib.auth.models import Group, User
from django.db.models.query_utils import Q


class Roles:
    developer = Group.objects.get_or_create(name='developer')[0]
    pm = Group.objects.get_or_create(name='pm')[0]
    qa = Group.objects.get_or_create(name='qa')[0]
    designer = Group.objects.get_or_create(name='designer')[0]

    @staticmethod
    def has_role(user, role):
        return role.pk in user.groups.all().values_list('pk', flat=True)


class CarrotProfile(models.Model):
    user = AutoOneToOneField(User)
    projects = models.ManyToManyField(Project)
    emails = models.CharField(max_length=250, default="", blank=True)

    def role(self):
        if Roles.has_role(self.user, Roles.pm):
            return 'pm'

    def visible_tickets(self):
        selfprojects = self.projects.values_list('id', flat=True)
        return Ticket.objects.filter(Q(project__in=selfprojects) | Q(project__parent__in=selfprojects))



from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^annoying\.fields\.AutoOneToOneField"])
