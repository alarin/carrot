import datetime
from django.contrib.auth.models import User
from carrot_tickets.models import Ticket
from django.db import models


class TicketEstimate(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='estimates')
    hours = models.PositiveIntegerField(null=True)
    is_expert = models.BooleanField(default=False)


class TimeLog(models.Model):
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(User)
    start = models.DateTimeField(default=datetime.datetime.now)
    end = models.DateTimeField(blank=True, null=True)

    def hours(self):
        end = self.end or datetime.datetime.now()
        return int((end-self.start).total_seconds()/60/60)

    def __unicode__(self):
        return '#%s %s %s-%s' % (self.ticket.number, self.user.get_full_name(), self.start, self.end)