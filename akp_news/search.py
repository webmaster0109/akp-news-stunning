from django.db.models import Q
from .models import News

def perform_search(query, sort_by="latest"):
    if not query:
        return News.objects.none()

    title_q = Q(title__icontains=query)
    content_q = Q(content__icontains=query)

    combined_q = title_q | content_q

    queryset = News.objects.filter(
        combined_q,
        is_published=True
    ).distinct()

    if sort_by == 'title_match_first':
        queryset = queryset.order_by(
            Q(title__icontains=query).desc(),
            '-published_at'
        )
    else:
        queryset = queryset.order_by('-published_at')

    return queryset