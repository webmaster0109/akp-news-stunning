from django.shortcuts import render, redirect, get_object_or_404
from .models import *
import random
# Create your views here.


def index_akp_news(request):

    news_tags = NewsTagBanner.objects.all()
    news_banner = NewsHomeBanner.objects.all()

    article = News.objects.all().order_by('-published_at').filter(is_published=True)

    live_updates = LiveUpdates.objects.all().order_by('-created_at').filter(is_active=True)

    active_ads = Advertisement.objects.filter(is_active=True)
    random_ads = active_ads.order_by('?') if active_ads.exists() else []

    context = {
        'news_tags': news_tags,
        'news_banners': news_banner,
        'articles': article,
        'live_updates': live_updates,
        'random_ads': random_ads
    }

    return render(request, template_name='base/index.html', context=context)


def news_details(request, slug):

    article = get_object_or_404(News, slug=slug, is_published=True)
    active_ads = Advertisement.objects.filter(is_active=True)
    random_ads = active_ads.order_by('?') if active_ads.exists() else []

    context = {
        'article': article,
        'random_ads': random_ads
    }

    return render(request, template_name='news/details/news_details.html', context=context)

def category_details(request, slug):

    category = get_object_or_404(NewsCategory, slug=slug)

    context = {
        'category': category
    }

    return render(request, template_name='news/details/category_details.html', context=context)

def tags_details(request, slug):

    tag = get_object_or_404(NewsTag, slug=slug)

    context = {
        'tag': tag
    }

    return render(request, template_name='news/details/tags_details.html', context=context)