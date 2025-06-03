from django.contrib import admin
from .models import Epaper, EpaperDownload
from akp_accounts.admin import limited_admin_site
# Register your models here.

limited_admin_site.register(Epaper)
limited_admin_site.register(EpaperDownload)
