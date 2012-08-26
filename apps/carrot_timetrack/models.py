from carrot_tickets.models import Ticket
from django.db import models


class TicketEstimate(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='estimates')
    hours = models.PositiveIntegerField(null=True)
    is_expert = models.BooleanField(default=False)


class TimeLog(models.Model):
    ticket = models.ForeignKey(Ticket)
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)