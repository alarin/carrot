#encoding: utf-8
from __future__ import unicode_literals
import datetime

from carrot_tickets.models import TicketStatus, CommentKind, TicketComment
from carrot_timetrack.models import TimeLog


def assign(user, ticket, new_state):
    ticket.assignee = user
    ticket.save()


workflow = {
    'developer': {
        TicketStatus.OPEN: {
            TicketStatus.IN_PROGRESS : {
                'name': 'Начать работу',
                'action': assign,
            }
        },
        TicketStatus.REOPENED: {
            TicketStatus.IN_PROGRESS: {
                'name': 'Начать работу',
                'action': assign,
            }
        },
        TicketStatus.IN_PROGRESS: {
            TicketStatus.FIXED: {
                'name': 'Задача выполнена',
                'condition': lambda user, ticket, new_state: ticket.assignee.pk == user.pk
            },
        },
        TicketStatus.FIXED: {
            TicketStatus.REOPENED: {
                'name': 'Открыть заново',
            }
        }
    }
}

def get_actions(user, ticket):
    actions = {}
    for group in user.groups.all():
        new_actions = workflow.get(group.name, {}).get(ticket.status)
        if new_actions:
            for action, descr in new_actions.items():
                if descr.get('condition', lambda user, ticket, new_state: True)(user, ticket, action):
                    actions[action] = descr
    return actions


def apply_action(user, ticket, action):
    actions = get_actions(user, ticket)
    if not action in actions:
        raise Exception('Unexpected actions')
    descr = actions.get(action)
    old_status = ticket.status
    new_status = action
    ticket.status = action
    ticket.save()
    TicketComment.objects.create(kind=CommentKind.CHANGES, ticket=ticket, author=user,
        content='%s → %s' % (old_status, action))

    #timeloggins
    if new_status == TicketStatus.IN_PROGRESS:
        timelog, created = TimeLog.objects.get_or_create(ticket=ticket, user=user, end=None)

    if new_status == TicketStatus.FIXED:
        timelog, created = TimeLog.objects.get_or_create(ticket=ticket, user=user, end=None)
        timelog.end = datetime.datetime.now()
        timelog.save()

    if descr.get('action'):
        descr.get('action')(user, ticket, action)
