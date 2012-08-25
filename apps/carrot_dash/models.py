from __future__ import unicode_literals
from annoying.fields import AutoOneToOneField
from carrot_tickets.models import Project

from django.db import models
from django.contrib.auth.models import Group, User


class Roles:
    developer = Group.objects.get_or_create(name='developer')
    pm = Group.objects.get_or_create(name='pm')
    qa = Group.objects.get_or_create(name='qa')
    designer = Group.objects.get_or_create(name='designer')


class CarrotProfile(models.Model):
    user = AutoOneToOneField(User)

    projects = models.ManyToManyField(Project)



from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^annoying\.fields\.AutoOneToOneField"])
