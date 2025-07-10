from django.contrib import admin
from .models import Epaper, EpaperDownload
from akp_accounts.admin import limited_admin_site
# Register your models here.

# limited_admin_site.register(Epaper)
# limited_admin_site.register(EpaperDownload)

class EpaperDownloadInline(admin.TabularInline):
  model = EpaperDownload

class EpaperAdmin(admin.ModelAdmin):
    list_display = ('meta_title', 'timestamp', 'is_active')
    search_fields = ('meta_title',)
    list_filter = ('is_active', 'timestamp')
    inlines = [EpaperDownloadInline]
  
limited_admin_site.register(Epaper, EpaperAdmin)
