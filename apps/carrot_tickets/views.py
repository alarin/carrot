#encoding: utf-8
from carrot_tickets.forms import CommentForm, TicketForm
from carrot_tickets.workflow import get_actions, apply_action
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from carrot_tickets.models import Ticket, TicketComment


@login_required
def ticket(request, project_slug, ticket_number):
    ticket = get_object_or_404(Ticket, number=ticket_number, project__slug=project_slug)
    comments = TicketComment.objects.filter(ticket=ticket)
    images = ticket.attachments.filter(kind='image').order_by('created')
    files = ticket.attachments.exclude(kind='image').order_by('created')
    actions = get_actions(request.user, ticket)

    comment_form = CommentForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action:
            if not action in actions:
                messages.error(request, 'Действие недоступно!')
            else:
                apply_action(request.user, ticket, action)
            return redirect('.')


        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            return redirect(request.path + '#c%d' % comment.pk)

    data = {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
        'files': files,
        'images': images,
        'actions': actions,
    }
    return TemplateResponse(request, 'carrot/tickets/ticket.html', data)


@login_required
def ticket_edit(request, project_slug, ticket_number):
    ticket = get_object_or_404(Ticket, number=ticket_number, project__slug=project_slug)
    images = ticket.attachments.filter(kind='image').order_by('created')
    files = ticket.attachments.exclude(kind='image').order_by('created')

    ticket_form = TicketForm(instance=ticket)

    if request.method == 'POST':
        redirect_path = request.POST.get('next') or\
            redirect('carrot_ticket', project_slug=ticket.project.slug, ticket_number=ticket.number)
        if request.POST.get('action', 'cancel') == 'cancel':
            return redirect_path
        if request.POST.get('action') == 'save':
            ticket_form = TicketForm(request.POST, instance=ticket)
            if ticket_form.is_valid():
                ticket = ticket_form.save(commit=False)
                if not ticket.reporter:
                    ticket.reporter = request.user
                ticket.save()
            return redirect_path

    data = {
        'ticket': ticket,
        'files': files,
        'images': images,
        'ticket_form': ticket_form,
    }
    return TemplateResponse(request, 'carrot/tickets/ticket_edit.html', data)
