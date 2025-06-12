from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from akp_epapers.views import download_epaper_view
from akp_accounts.admin import limited_admin_site

urlpatterns = [
    path("super-private-admin/", admin.site.urls, name="admin_login"),
    path("private-admin/", limited_admin_site.urls, name="admin_login"),
    path("", include("akp_news.urls")),
    path("account/", include("akp_accounts.urls")),
    path("control-admin-center/", include("admin_akp.urls")),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path("pdf/<str:epaper_id>/download/", download_epaper_view, name="download_epaper"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += staticfiles_urlpatterns()
