from django.shortcuts import render, redirect, get_object_or_404
from .models import *
import random
from .utils import get_nested_comments
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
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

    comments = get_nested_comments(article.id)

    comments_json_data = json.dumps(comments)

    context = {
        'article': article,
        'random_ads': random_ads,
        'comments_json_data': comments_json_data,
        'comment': comments
    }

    return render(request, template_name='news/details/news_details.html', context=context)

@login_required
@require_POST
def add_comment_view(request):
    """
    Handles POST requests from a standard HTML form to add a new comment or reply.
    Expects 'news_id', 'content', and optional 'parent_id' in request.POST.
    """
    if request.method == "POST":
        news_id = request.POST.get('news_id')
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id') # Can be None or an empty string

    # Basic validation
    if not content:
        # messages.error(request, 'Comment content cannot be empty.')
        # Redirect back to the news page, or a more specific error handling page
        if news_id:
            try:
                news_article_for_redirect = get_object_or_404(News, pk=news_id)
                # Assuming your news detail URL is named 'news_detail_by_slug' and uses a slug
                # Adjust if your URL pattern is different (e.g., uses pk)
                return redirect('news_details', slug=news_article_for_redirect.slug)
            except: # Fallback if news_id is bad or slug logic fails
                 return redirect('index_akp_news') # Or some other appropriate fallback
        return redirect('index_akp_news') # Fallback if news_id is missing

    try:
        news_article = get_object_or_404(News, pk=news_id)
        parent_comment = None
        if parent_id: # If parent_id is provided and not an empty string
            parent_comment = get_object_or_404(NewsComment, pk=parent_id)

        # Create the new comment
        NewsComment.objects.create(
            news=news_article,
            author=request.user,
            content=content,
            parent=parent_comment
        )
        # messages.success(request, 'Your comment has been posted successfully!')
        # Redirect back to the news detail page
        # Ensure you have a URL pattern named 'news_detail_by_slug' that takes a slug,
        # or 'news_detail_by_id' that takes an ID, etc.
        return redirect('news_details', slug=news_article.slug) # Adjust 'slug' if your model uses a different field for URL

    except News.DoesNotExist:
        # messages.error(request, 'News article not found.')
        return redirect('index_akp_news') # Or your main news listing page
    except NewsComment.DoesNotExist:
        # messages.error(request, 'Parent comment not found. Could not post reply.')
        if news_id: # Try to redirect to the original article
             news_article_for_redirect = get_object_or_404(News, pk=news_id)
             return redirect('news_details', slug=news_article_for_redirect.slug)
        return redirect('index_akp_news')
    except Exception as e:
        # messages.error(request, f'An unexpected error occurred: {e}')
        # Log the error for debugging
        # import logging
        # logging.error(f"Error adding comment: {e}")
        if news_id: # Try to redirect to the original article
             news_article_for_redirect = get_object_or_404(News, pk=news_id)
             return redirect('news_details', slug=news_article_for_redirect.slug)
        return redirect('index_akp_news')


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