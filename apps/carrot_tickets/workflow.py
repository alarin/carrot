#encoding: utf-8
from __future__ import unicode_literals
import datetime
from carrot_tickets import signals

from carrot_tickets.models import TicketStatus, CommentKind, TicketComment
from carrot_timetrack.models import TimeLog


def assign(user, ticket, new_state):
    ticket.assignee = user
    ticket.save()


workflow = {
    'developer': {
        TicketStatus.OPEN: [
            {
                'name': 'Начать работу',
                'status': TicketStatus.IN_PROGRESS,
                'action': assign,
            },
            {
                'name': 'Reject',
                'status': TicketStatus.REJECTED,
                'class': 'btn-danger pull-right',
            }
        ],
        TicketStatus.REOPENED: [
            {
                'status': TicketStatus.IN_PROGRESS,
                'name': 'Начать работу',
                'action': assign,
            }
        ],
        TicketStatus.IN_PROGRESS: [
            {
                'status': TicketStatus.FIXED,
                'name': 'Задача выполнена',
                'class': 'js_fixed',
                'condition': lambda user, ticket, new_state: ticket.assignee.pk == user.pk
            },
        ],
        TicketStatus.FIXED: [
            {
                'status': TicketStatus.REOPENED,
                'name': 'Открыть заново',
            }
        ]
    }
}

def get_actions(user, ticket):
    actions = []
    for group in user.groups.all():
        new_actions = workflow.get(group.name, {}).get(ticket.status)
        if new_actions:
            for descr in new_actions:
                new_state = descr.get('action', None)
                if descr.get('condition', lambda user, ticket, new_state: True)(user, ticket, new_state):
                    actions.append(descr)
    return actions


def apply_action(user, ticket, action_name, POST):
    actions = get_actions(user, ticket)
    action = None
    for a in actions:
        if a['name'] == action_name:
            action = a
            break
    if not action:
        raise Exception('Unexpected action %s' % (actions))
    old_status = ticket.status
    new_status = action.get('status', None)

    if new_status:
        if new_status == TicketStatus.FIXED and POST.get('hours', None):
            hours = int(POST.get('hours', None))
            TimeLog.objects.create(user=ticket.assignee, ticket=ticket, hours=hours, end=datetime.datetime.now())

        ticket.status = new_status
        signals.ticket_will_update.send(sender=__name__, ticket=ticket, changer=user)
        ticket.save()

        TicketComment.objects.create(kind=CommentKind.CHANGES, ticket=ticket, author=user,
            content='%s → %s' % (old_status, new_status))

    if action.get('action'):
        action.get('action')(user, ticket, new_status)
