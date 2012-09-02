from carrot_github.models import ProjectGitHub
import carrot_tickets.admin
from carrot_tickets.models import Project
from django.contrib import admin


class GitHubInline(admin.TabularInline):
    model = ProjectGitHub
    extra = 1
    max_num = 1


class ProjectAdmin(carrot_tickets.admin.ProjectAdmin):
    def __init__(self, *args, **kwargs):
        self.inlines += [GitHubInline]
        super(ProjectAdmin, self).__init__(*args, **kwargs)


admin.site.unregister(Project)
admin.site.register(Project, ProjectAdmin)
