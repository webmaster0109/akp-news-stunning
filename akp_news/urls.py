from django.urls import path
from .views import *


urlpatterns = [
    path("", index_akp_news, name="index_akp_news"),
    path("news/<slug:slug>/", category_details, name="category_details"),
    path("topics/<slug:slug>/", tags_details, name="tags_detail"),
    path("news/story/<slug:slug>/", news_details, name="news_details"),

    path('add-comment/', add_comment_view, name='add_comment'),
]
