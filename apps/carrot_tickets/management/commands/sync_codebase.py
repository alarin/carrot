from __future__ import unicode_literals
from carrot_timetrack.models import TicketEstimate
from django.contrib.auth.models import User
from carrot_tickets.codebase import tickets
from carrot_tickets.models import Version, Ticket
from carrot_tickets import codebase

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = '<codebase project> <codebase version> <carrot project> <carrot version>'

    def handle(self, *args, **options):
        print [(m['ticketing_milestone']['id'],m['ticketing_milestone']['name'])
            for m in codebase.milestones(args[0])]

        if len(args) != 4:
            return self.usage('') + '\n'

        carrot_version = Version.objects.get(slug=args[3], project__slug=args[2])
        cb_tickets = tickets(args[0], args[1])

        common_options = {
            'fix_version': carrot_version,
            'project': carrot_version.project,
            'reporter': User.objects.all()[0],
        }
        for cbt in cb_tickets:
            cbt = cbt['ticket']
            notes = codebase.ticket_notes(args[0], cbt['ticket_id'])
            options = {
                'summary': cbt['summary'],
                'kind': cbt['ticket_type'].lower(),
                'number': cbt['ticket_id']
            }
            if notes:
                options['description'] = notes[0]['ticket_note']['content']


            options.update(common_options)
            ticket = Ticket.objects.filter(**common_options).filter(summary=options['summary'])
            if len(ticket):
                ticket = ticket[0]
            else:
                ticket = Ticket()

            for k, v in options.items():
                setattr(ticket, k, v)
            ticket.save()
            if cbt.get('estimated_time'):
                te, created = TicketEstimate.objects.get_or_create(ticket=ticket)
                te.hours = int(cbt.get('estimated_time')/60)
                te.save()
            print ticket




