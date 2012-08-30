import carrot_tickets
from carrot_tickets.models import Ticket
from carrot_timetrack.models import TicketEstimate, TimeLog
from django.contrib import admin


class EstimateInline(admin.TabularInline):
    model = TicketEstimate

class TimeLogInline(admin.TabularInline):
    model = TimeLog


class TicketAdmin(carrot_tickets.admin.TicketAdmin):
    def __init__(self, *args, **kwargs):
        self.inlines += [EstimateInline, TimeLogInline]
        self.list_display = list(self.list_display) + ['estimate']
        super(TicketAdmin, self).__init__(*args, **kwargs)

    def estimate(self, obj):
        tes = obj.estimates.all()
        if len(tes):
            return tes[0].hours
        return ''



admin.site.unregister(Ticket)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(TimeLog)