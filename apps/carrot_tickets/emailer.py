#encoding: utf-8
from __future__ import unicode_literals
from sets import Set
from carrot_dash.models import Roles
from django.contrib import sites
from django.contrib.auth.models import User
from carrot_tickets.models import Ticket, TicketComment, CommentKind
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse


EXCLUDE_FIELDS = ['created']


def email_on_ticket_changes(sender, ticket, changer, **kwargs):
    mail_to = _get_ticket_mailto(ticket, changer)

    if len(mail_to):
        if ticket.pk:
            old_ticket = Ticket.objects.get(pk=ticket.pk)
            changed_fields = {}

            for f in old_ticket._meta.fields:
                fname = f.name
                if not fname in EXCLUDE_FIELDS and getattr(old_ticket, fname) != getattr(ticket, fname):
                    changed_fields[fname] = [getattr(old_ticket, fname), getattr(ticket, fname)]

            if not changed_fields:
                return

            body = '%s\n' % ticket.get_url()
            if len(changed_fields) == 1 and 'status' in changed_fields:
                subject = '%s: #%s %s→%s by %s' \
                    % (ticket.project.full_name(), ticket.number, changed_fields['status'][0],
                       changed_fields['status'][1], changer.get_full_name())
            else:
                subject = '%s: #%s changed by %s' % (ticket.project.full_name(), ticket.number, changer.get_full_name())
                body += '\n'.join(['%s: %s → %s' % (k, v[0], v[1]) for k, v in changed_fields.items()])
        else:
            subject = '%s: #%s created by %s' % (ticket.project.full_name(), ticket.number, changer.get_full_name())
            body = ''
        send_mail(subject, body, settings.SERVER_EMAIL, mail_to, fail_silently=False)


def email_on_comment(sender, instance, **kwargs):
    if instance.kind != CommentKind.COMMENT:
        #skip status changes and commits
        return
    ticket = instance.ticket
    mail_to = _get_ticket_mailto(ticket, instance.author)

    subject = '%s: #%s commented by %s' % (ticket.project.full_name(), ticket.number, instance.author.get_full_name())
    body = instance.content
    send_mail(subject, body, settings.SERVER_EMAIL, mail_to, fail_silently=False)


def _get_ticket_mailto(ticket, changer):
    mail_to = [ticket.reporter.email]
    if ticket.assignee:
        mail_to.append(ticket.assignee.email)
        #pms
    mail_to += User.objects.filter(groups=Roles.pm, carrotprofile__projects=ticket.project)\
    .values_list('email', flat=True)
    #commentators
    mail_to += TicketComment.objects.filter(ticket=ticket).values_list('author__email', flat=True)

    #remove dublicates, remove changer
    mail_to = Set(mail_to)
    mail_to.discard(changer.email)
    return mail_to
