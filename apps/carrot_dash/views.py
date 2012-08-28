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
    project = request.user.carrotprofile.projects.all()[0]
    versions = project.version_set.filter(is_completed=False).order_by('end_date')
    versions_data = []
    for v in versions:
        versions_data.append((v, v.ticket_set.order_by('kind', 'number')))
    data = {
        'project': project,
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