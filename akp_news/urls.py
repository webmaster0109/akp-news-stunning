from django.urls import path
from .views import *


urlpatterns = [
    path("", index_akp_news, name="index_akp_news"),
    path("news/<str:slug>/", category_details, name="category_details"),
    path("topics/<str:slug>/", tags_details, name="tags_detail"),
    path("news/story/<str:slug>/", news_details, name="news_details"),

    path('add-comment/', add_comment_view, name='add_comment'),

    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('api/live-search/', live_search_api, name='live_search_api'),
]
