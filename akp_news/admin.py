from django.contrib import admin
from akp_accounts.admin import limited_admin_site
from .models import *

# Register your models here.


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'category', 'is_published')
    prepopulated_fields = {'slug': ('title',)}

limited_admin_site.register(News, NewsAdmin)

limited_admin_site.register(NewsTag)
limited_admin_site.register(NewsTagBanner)
limited_admin_site.register(NewsHomeBanner)
limited_admin_site.register(LiveUpdates)
limited_admin_site.register(Advertisement)
limited_admin_site.register(SocialAccount)


class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

limited_admin_site.register(NewsCategory, NewsCategoryAdmin)

from django.contrib.auth.models import Group

# Unregister the Group model from the admin panel
admin.site.unregister(Group)

class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ('news', 'author', 'parent', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at', 'news')
    search_fields = ('content', 'author__username', 'news__title')
    actions = ['approve_comments', 'disapprove_comments']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = "Disapprove selected comments"

limited_admin_site.register(NewsComment, NewsCommentAdmin)