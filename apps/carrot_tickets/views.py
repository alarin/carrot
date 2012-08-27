from carrot_tickets.forms import CommentForm
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


    comment_form = CommentForm()

    if request.method == 'POST':
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
    }
    return TemplateResponse(request, 'carrot/tickets/ticket.html', data)