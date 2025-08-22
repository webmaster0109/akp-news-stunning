from django.contrib.sitemaps import Sitemap
from .models import News, NewsCategory, NewsSubCategory, NewsTag
from django.urls import reverse

class HomeSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['']

    def location(self, obj):
        return reverse("index_akp_news")

class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return News.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

class NewsCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return NewsCategory.objects.all()

# class NewsSubCategorySitemap(Sitemap):
#     changefreq = "weekly"
#     priority = 0.8

#     def items(self):
#         return NewsSubCategory.objects.all()

class NewsTagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return NewsTag.objects.all()