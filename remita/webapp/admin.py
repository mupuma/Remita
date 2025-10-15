from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from webapp.models import *

class CustmonUserAdmin(UserAdmin):
    list_display = ['username', 'password', 'role','is_active']
    fieldsets = (
        (None, {'fields': ( 'password',)}),
        ('Personal info', {'fields': ('username', )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'fields': ( 'username','role', 'password1', 'password2'),
        }),
    )
    search_fields = ( 'username',)
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')


# Register your models here.
admin.site.register(BankDetails)
admin.site.register(Projects)
admin.site.register(Users,CustmonUserAdmin)