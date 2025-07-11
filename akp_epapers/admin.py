from django.contrib import admin
from .models import Epaper, EpaperDownload, ShortURL
from akp_accounts.admin import limited_admin_site
# Register your models here.

# limited_admin_site.register(Epaper)
# limited_admin_site.register(EpaperDownload)

class EpaperDownloadInline(admin.TabularInline):
  model = EpaperDownload
  extra = 0

class ShortURLInline(admin.TabularInline):
    model = ShortURL
    extra = 0
    fields = ('short_url', 'created_at')
    readonly_fields = ('short_url', 'created_at')

class EpaperAdmin(admin.ModelAdmin):
    list_display = ('meta_title', 'timestamp', 'is_active', 'get_short_url')
    search_fields = ('meta_title',)
    list_filter = ('is_active', 'timestamp')
    inlines = [ShortURLInline, EpaperDownloadInline]

    def get_short_url(self, obj):
        return f"https://aajkaprahari.com/s/{obj.short_url.short_url}/" if obj.short_url else 'No URL'

limited_admin_site.register(Epaper, EpaperAdmin)
limited_admin_site.register(ShortURL)