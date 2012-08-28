from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from carrot_tickets.models import Version, Ticket, Project, TicketComment, TicketAttachment
from django.contrib import admin

class VersionAdmin(admin.ModelAdmin):
    list_display = ('project', '__unicode__', 'start_date', 'end_date', 'description')
    list_display_links = ('__unicode__',)
    list_filter = ('project', 'start_date', 'end_date')


class AttachmentInline(admin.StackedInline):
    model = TicketAttachment

class TicketAdmin(admin.ModelAdmin):
    list_display = ('project', 'fix_version', 'kind', 'summary')
    list_display_links = ('summary',)
    list_filter = ('project', 'fix_version')

    inlines = [AttachmentInline]


admin.site.register(Project)
admin.site.register(Version, VersionAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketComment)
admin.site.register(TicketAttachment)
