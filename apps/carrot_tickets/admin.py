from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from carrot_tickets.models import Version, Ticket, Project
from django.contrib import admin

class VersionAdmin(admin.ModelAdmin):
    list_display = ('project', '__unicode__', 'start_date', 'end_date', 'description')
    list_display_links = ('__unicode__',)
    list_filter = ('project', 'start_date', 'end_date')

admin.site.register(Project)
admin.site.register(Version, VersionAdmin)
admin.site.register(Ticket)
