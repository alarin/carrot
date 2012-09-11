import datetime
import user
from django.contrib.auth.models import User
from carrot_tickets.models import Ticket
from django.db import models


class TicketEstimate(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='estimates')
    hours = models.PositiveIntegerField(null=True)
    is_expert = models.BooleanField(default=False)


class TimeLogManager(models.Manager):
    def start(self, user, ticket):
        timelog, created = TimeLog.objects.get_or_create(ticket=ticket, user=user, end=None)
        TimeLog.objects.exclude(ticket=ticket).filter(user=user, end=None).update(end=datetime.datetime.now())

    def pause(self, user, ticket):
        timelog = TimeLog.objects.get(ticket=ticket, user=user, end=None)
        timelog.end = datetime.datetime.now()
        timelog.save()

    def stop(self, user, ticket):
        #now don't need other logic
        return self.pause(user, ticket)



class TimeLog(models.Model):
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(User)
    start = models.DateTimeField(default=datetime.datetime.now)
    end = models.DateTimeField(blank=True, null=True)

    objects = TimeLogManager()

    def hours(self):
        end = self.end or datetime.datetime.now()
        td = end - self.start
        return int((td.seconds + td.days * 24 * 3600)/60/60)

    def __unicode__(self):
        return '#%s %s %s-%s' % (self.ticket.number, self.user.get_full_name(), self.start, self.end)