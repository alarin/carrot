#encoding: utf-8
from __future__ import unicode_literals

from carrot_tickets.models import TicketStatus, CommentKind, TicketComment


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
        if workflow.get(group.name, {}).get(ticket.status):
            actions.update(workflow.get(group.name, {}).get(ticket.status))
    return actions


def apply_action(user, ticket, action):
    actions = get_actions(user, ticket)
    if not action in actions:
        raise Exception('Unexpected actions')
    descr = actions.get(action)
    old_status = ticket.status
    ticket.status = action
    ticket.save()
    TicketComment.objects.create(kind=CommentKind.CHANGES, ticket=ticket, author=user,
        content='%s → %s' % (old_status, action))
    if descr.get('action'):
        descr.get('action')(user, ticket, action)
