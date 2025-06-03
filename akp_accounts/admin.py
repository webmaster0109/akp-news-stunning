from django.contrib import admin
from .models import CustomUser, AdminLoginAttempt
from .forms import LimitedConcurrentSessionAdminAuthenticationForm
from django.conf import settings
from django.contrib.admin import AdminSite
# Register your models here.

class LimitedAdminSite(AdminSite):
    login_form = LimitedConcurrentSessionAdminAuthenticationForm

limited_admin_site = LimitedAdminSite(name='limited_admin')
limited_admin_site.register(CustomUser)
limited_admin_site.register(AdminLoginAttempt)