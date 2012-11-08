#encoding: utf-8
from carrot_tickets import signals
from carrot_tickets.forms import CommentForm, TicketForm
from carrot_tickets.workflow import get_actions, apply_action
from carrot_timetrack.models import TicketEstimate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from carrot_tickets.models import Ticket, TicketComment, TicketAttachment, Version, CommentAttachment


@login_required
def ticket(request, project_slug, ticket_number):
    ticket = get_object_or_404(Ticket, number=ticket_number, project__slug=project_slug)
    comments = TicketComment.objects.filter(ticket=ticket)
    actions = get_actions(request.user, ticket)

    comment_form = CommentForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action:
            apply_action(request.user, ticket, action, request.POST)
            return redirect('.')


        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()

            for f in request.FILES.getlist('comment_attachment'):
                CommentAttachment.objects.create(comment=comment, file=f)
            return redirect(request.path + '#c%d' % comment.pk)

    from carrot_timetrack.models import TimeLog
    data = {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
        'actions': actions,
        'timelogs': TimeLog.objects.filter(ticket=ticket),
        'project': ticket.project, #for navigation
        'version': ticket.fix_version, #for navigation
    }
    return TemplateResponse(request, 'carrot/tickets/ticket.html', data)


@login_required
def ticket_edit(request, project_slug=None, ticket_number=None):
    is_new = not ticket_number
    if is_new:
        ticket = Ticket()
    else:
        ticket = get_object_or_404(Ticket, number=ticket_number, project__slug=project_slug)
    images = ticket.attachments.filter(kind='image').order_by('created')
    files = ticket.attachments.exclude(kind='image').order_by('created')
    estimate = TicketEstimate.objects.filter(ticket=ticket)
    if is_new:
        initial_data = {
            'project': request.GET.get('project'),
            'fix_version': request.GET.get('version'),
            'estimate': estimate and estimate[0].hours or '',
        }
    else:
        initial_data = {
            'estimate': estimate and estimate[0].hours or '',
        }
    ticket_form = TicketForm(instance=ticket, initial=initial_data)

    def get_redirect_path(ticket):
        if not ticket.pk:
            return redirect('/')
        return request.POST.get('next') or\
            redirect('carrot_ticket', project_slug=ticket.project.slug, ticket_number=ticket.number)

    if request.method == 'POST':
        if request.POST.get('action') == 'save':
            ticket_form = TicketForm(request.POST, files=request.FILES, instance=ticket)
            if ticket_form.is_valid():
                ticket = ticket_form.save(commit=False)
                if not ticket.pk or not ticket.reporter:
                    ticket.reporter = request.user
                ticket.save(user=request.user)
                if request.user.carrotprofile.role() == 'pm':
                    if ticket_form.cleaned_data['estimate']:
                        te = TicketEstimate.objects.get_or_create(ticket=ticket)[0]
                        te.hours = int(ticket_form.cleaned_data['estimate'])
                        te.save()
                if ticket_form.cleaned_data['file']:
                    TicketAttachment.objects.create(ticket=ticket, file=ticket_form.cleaned_data['file'])
                return get_redirect_path(ticket)
        if request.POST.get('action', 'cancel') == 'cancel':
            return get_redirect_path(ticket)

    data = {
        'new': is_new,
        'ticket': ticket,
        'files': files,
        'images': images,
        'ticket_form': ticket_form,
        'all_versions': Version.objects.filter(is_completed=False).select_related(),
    }
    return TemplateResponse(request, 'carrot/tickets/ticket_edit.html', data)


@login_required
def ticket_new(request):
    return ticket_edit(request)