from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'category', 'is_published')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(NewsTag)
admin.site.register(NewsComment)
admin.site.register(NewsTagBanner)
admin.site.register(NewsHomeBanner)
admin.site.register(LiveUpdates)
admin.site.register(Advertisement)


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}


from django.contrib.auth.models import Group

# Unregister the Group model from the admin panel
admin.site.unregister(Group)