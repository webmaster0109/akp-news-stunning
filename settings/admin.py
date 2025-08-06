from django.contrib import admin
from akp_accounts.admin import limited_admin_site
# Register your models here.
from .models import Settings

class SettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key',)

limited_admin_site.register(Settings, SettingsAdmin)
