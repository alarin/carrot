from carrot_dash.models import CarrotProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib import admin


class CarrotProfileInline(admin.TabularInline):
    model = CarrotProfile


class UserAdmin(DjangoUserAdmin):
    inlines = [CarrotProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)