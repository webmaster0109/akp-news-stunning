from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from akp_epapers.views import download_epaper_view, view_epaper, redirect_short_url
from akp_accounts.admin import limited_admin_site

from akp_news import views as server_views
from webstories.views import story_detail

from akp_news.sitemaps import NewsSitemap, NewsCategorySitemap, NewsTagSitemap, HomeSitemap
from django.contrib.sitemaps.views import sitemap
from akp_epapers.sitemaps import EpaperSitemap

sitemaps = {
    'home': HomeSitemap,
    'news': NewsSitemap,
    'category': NewsCategorySitemap,
    'tag': NewsTagSitemap,
    'epaper': EpaperSitemap,
}

from admin_akp.views import download_sqlite_db, db_download_page

urlpatterns = [
    path("super-private-admin/", admin.site.urls, name="admin_login"),
    path("private-admin/", limited_admin_site.urls, name="admin_login"),
    path("", include("akp_news.urls")),
    path("account/", include("akp_accounts.urls")),
    path("control-admin-center/", include("admin_akp.urls")),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path("s/<str:short_url>/", redirect_short_url, name="redirect_short_url"),
    path("visualstories/<str:slug>/", story_detail, name="story_detail"),
    path("epapers/<str:epaper_id>/", view_epaper, name="view_epaper"),
    path("pdf/<str:epaper_id>/download/", download_epaper_view, name="download_epaper"),
]

urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('admin-tools-db-download/', download_sqlite_db, name='download_sqlite_db'),
    path('admin-tools/', db_download_page, name='db_download_page'),

]

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
  pass
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += [
    #     re_path(r'^.*/$', server_views.handler404, name='handler404_testing'),
    # ]


# urlpatterns += staticfiles_urlpatterns()


handler404 = server_views.handler404