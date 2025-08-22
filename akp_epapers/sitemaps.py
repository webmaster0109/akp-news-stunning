from django.contrib.sitemaps import Sitemap
from .models import Epaper

class EpaperSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Epaper.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at
