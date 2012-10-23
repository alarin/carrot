import datetime
from carrot_tickets.models import TicketStatus, TicketKind, Ticket
from carrot_timetrack.utils import work_hours
from django.db.models.aggregates import Sum
from carrot_timetrack.models import TicketEstimate, TimeLog
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, login
from carrot_dash.models import Roles
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse


@login_required
def home(request):
    if Roles.has_role(request.user, Roles.developer):
        return dash_developer(request)
    return TemplateResponse(request, 'carrot/site_base.html', {})


@login_required
def dash_developer(request):
    projects = request.user.carrotprofile.projects.all()
    if request.GET.get('project_slug'):
        project = projects.get(slug=request.GET.get('project_slug'))
    else:
        project = projects[0]
    versions = project.version_set.filter(is_completed=False).order_by('end_date')
    versions_data = []
    for v in versions:
        version_tickets = v.ticket_set.order_by('kind', '-priority', 'number')
        statistic = None
        if v.end_date >= datetime.datetime.now().date():
            tickets_hours = TicketEstimate.objects\
                .exclude(ticket__status__in=[TicketStatus.FIXED, TicketStatus.CLOSED, TicketStatus.REJECTED])\
                .filter(ticket__fix_version=v, is_expert=False)\
                .aggregate(Sum('hours'))['hours__sum'] or 0
            real_time_left = work_hours(v.end_date)
            all_real_time = work_hours(v.start_date, v.end_date)
            logged_time = TimeLog.objects.filter(ticket__fix_version=v)\
                .aggregate(Sum('hours'))['hours__sum'] or 0
            statistic = {
                'tickets_time': tickets_hours,
                'real_time_left': real_time_left,
                'real_time_passed': all_real_time - real_time_left,
                'logged_time': logged_time,
                'tickets_percent': int(tickets_hours/float(all_real_time) * 100),
                'real_percent': int(real_time_left/float(all_real_time) * 100),
            }
        versions_data.append((
            v,
            version_tickets,
            statistic))
    data = {
        'pm': Roles.has_role(request.user, Roles.pm),
        'project': project,
        'version': versions[0],# just for +ticket menu option
        'projects': projects,
        'versions': versions_data
    }
    return TemplateResponse(request, 'carrot/dash/developer.html', data)


def dash_designer(request):
    return HttpResponse('Not realized yet')


def dash_qa(request):
    return HttpResponse('Not realized yet')


def dash_pm(request):
    return HttpResponse('Not realized yet')


def logout_view(request):
    logout(request)
    return redirect('carrot_home')


def login_view(request):
    login_form = AuthenticationForm(request, request.POST or None)
    request.session.set_test_cookie()
    if login_form.is_valid():
        login(request, login_form.get_user())
        return redirect('carrot_home')
    data = {
        'login_form': login_form,
    }
    return TemplateResponse(request, 'carrot/dash/login.html', data)


def report_timelog(request):
    today = datetime.datetime.now()
    basedate = today
    try:
        basedate = datetime.datetime.strptime(request.GET['date'], '%d%m%y')
    except:
        pass
    start = basedate - datetime.timedelta(days=basedate.weekday())
    start = datetime.datetime.combine(start.date(), datetime.time(00,00))
    end = basedate + datetime.timedelta(days=6-basedate.weekday())
    end = datetime.datetime.combine(end.date(), datetime.time(23,59))

    prev = basedate - datetime.timedelta(weeks=1)
    next = basedate + datetime.timedelta(weeks=1)
    if (next - datetime.timedelta(days=next.weekday())) > today:
        next = None

    timelog_week = TimeLog.objects.filter(end__gte=start, start__lte=end)\
        .order_by('user').select_related()

    week_data = {}
    for tl in timelog_week:
        if not tl.user in week_data:
            week_data[tl.user] = {}
        week_data[tl.user]['total'] = week_data[tl.user].get('total', 0) + tl.hours
        if tl.ticket.estimates.count():
            week_data[tl.user]['estimate'] = week_data[tl.user].get('estimate', 0) + tl.ticket.estimates.all()[0].hours

        if tl.ticket.kind == TicketKind.BUG:
            week_data[tl.user]['total_bug'] = week_data[tl.user].get('total_bug', 0) + tl.hours
        else:
            week_data[tl.user]['total_task'] = week_data[tl.user].get('total_task', 0) + tl.hours

    week_tasks_data = {}
    for tl in timelog_week:
        if not tl.user in week_tasks_data:
            week_tasks_data[tl.user] = {}
        week_tasks_data[tl.user]['tasks'] = week_tasks_data[tl.user].get('total', 0) + tl.hours

    week_tickets = Ticket.objects.filter(pk__in=timelog_week.values_list('ticket__pk', flat=True))\
        .order_by('assignee')
    week_tickets_data = {}
    for t in week_tickets:
        if not t.assignee in week_tickets_data:
            week_tickets_data[t.assignee] = []
        week_tickets_data[t.assignee].append(
            (t, TimeLog.objects.filter(ticket=t, user=t.assignee).aggregate(Sum('hours'))['hours__sum'],
             t.time_spent(), t.estimate()))

    data = {
        'start': start,
        'end': end,
        'timelog_week': timelog_week,
        'week_data': week_data,
        'week_tickets': week_tickets,
        'week_tickets_data': week_tickets_data,
        'prev': prev,
        'next': next,
    }
    return TemplateResponse(request, 'carrot/dash/reports/timelog.html', data)