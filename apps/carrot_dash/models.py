from __future__ import unicode_literals
from annoying.fields import AutoOneToOneField
from carrot_tickets.models import Project

from django.db import models
from django.contrib.auth.models import Group, User


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



from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^annoying\.fields\.AutoOneToOneField"])
