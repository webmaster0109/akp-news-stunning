from django.shortcuts import render, redirect, get_object_or_404
from .models import *
import random
from .utils import get_nested_comments
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from akp_epapers.models import Epaper
from .search import perform_search
# Create your views here.


def index_akp_news(request):

    news_tags = NewsTagBanner.objects.all()
    news_banner = NewsHomeBanner.objects.all()

    article = News.objects.all().order_by('-published_at').filter(is_published=True)

    live_updates = LiveUpdates.objects.all().order_by('-created_at').filter(is_active=True)

    active_ads = Advertisement.objects.filter(is_active=True)
    random_ads = active_ads.order_by('?') if active_ads.exists() else None

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

class SearchResultsView(ListView):
    model = News
    template_name = 'news/details/search_details.html'
    context_object_name = 'news_list'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        sort_by = self.request.GET.get('sort_by', 'latest')
        return perform_search(query, sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['result_count'] = self.get_queryset().count()
        context['sort_by'] = self.request.GET.get('sort', 'latest')
        return context

def live_search_api(request):
    query = request.GET.get('q', None)
    results_data = []

    if query and len(query.strip()) > 0:
        search_results = perform_search(query.strip(), sort_by='latest')
        query_lower = query.strip().lower() # Lowercase query once for snippet matching

        for news_item in search_results[:5]: # Limit to top 5 suggestions
            title_str = news_item.title if news_item.title else ""
            content_str = news_item.content if news_item.content else ""
            
            item_url = "#" # Default URL if get_absolute_url fails or is not defined
            try:
                # Ensure get_absolute_url() is defined on your News model and handles potential errors
                if hasattr(news_item, 'get_absolute_url') and callable(news_item.get_absolute_url):
                    item_url = news_item.get_absolute_url()
            except Exception:
                # Log this error in a real application
                pass 

            snippet_text = ""
            if content_str:
                content_lower = content_str.lower()
                start_index = content_lower.find(query_lower)
                
                snippet_start = 0
                if start_index > 50 : # If query is found far into the content
                    snippet_start = start_index - 40 # Start a bit before the query term
                elif start_index == -1 and title_str.lower().find(query_lower) != -1: # Query in title but not content
                    snippet_start = 0 # Just show start of content
                elif start_index == -1: # Query not in content or title for this item (unlikely if search works)
                    snippet_start = 0

                snippet_start = max(0, snippet_start) # Ensure snippet_start is not negative

                if snippet_start < len(content_str):
                    temp_snippet = content_str[snippet_start : snippet_start + 120] # Max 120 chars for snippet
                    
                    # Add leading ellipsis if not starting from the beginning and query was actually in content here
                    if snippet_start > 0 and start_index != -1 and start_index > snippet_start :
                         snippet_text = "..." + temp_snippet
                    else:
                        snippet_text = temp_snippet

                    if len(content_str) > snippet_start + 120:
                        snippet_text += "..."
                elif len(content_str) > 0: # If snippet_start is out of bounds but content exists
                    snippet_text = content_str[:120]
                    if len(content_str) > 120:
                        snippet_text += "..."
                
            if not snippet_text and title_str: # Fallback to title if no content snippet
                snippet_text = title_str[:120]
                if len(title_str) > 120:
                     snippet_text += "..."
            
            # Ensure snippet is plain text (escape HTML if content can have it)
            # snippet_text = escape(snippet_text) # Uncomment if your content has HTML

            results_data.append({
                'title': title_str,
                'url': item_url,
                'snippet': snippet_text
            })
            
    return JsonResponse({'results': results_data})

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
        return JsonResponse({'status': 'error', 'message': 'Comment content is required'}, status=400)
        # Redirect back to the news page, or a more specific error handling page
    if not news_id:
        return JsonResponse({'status': 'error', 'message': 'News ID is required'}, status=400)
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
        return JsonResponse({'status': 'success', 'message': 'Comment submitted successfully. Now waiting for approval!'}, status=200)
        # messages.success(request, 'Your comment has been posted successfully!')
        # Redirect back to the news detail page
        # Ensure you have a URL pattern named 'news_detail_by_slug' that takes a slug,
        # or 'news_detail_by_id' that takes an ID, etc.

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

    epapers = Epaper.objects.filter(is_active=True).order_by('-timestamp')

    context = {
        'category': category,
        'epapers': epapers
    }
    return render(request, template_name='news/details/category_details.html', context=context)

def tags_details(request, slug):

    tag = get_object_or_404(NewsTag, slug=slug)

    context = {
        'tag': tag
    }

    return render(request, template_name='news/details/tags_details.html', context=context)