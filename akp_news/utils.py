from .models import NewsComment, News

def get_nested_comments(news_id):

    try:
        news_article = News.objects.get(pk=news_id)
    except News.DoesNotExist:
        return []

    all_comments = NewsComment.objects.filter(
            news=news_article, 
            is_approved=True
        ).select_related('author', 'parent').order_by('-created_at')
    
    comment_map = {
        comment.id : {
            'id' : comment.id,
            'author' : comment.author.get_full_name() if hasattr(comment.author, 'get_full_name') else comment.author.username,
            'author_id' : comment.author.id,
            'content' : comment.content,
            'parent_id' : comment.parent_id,
            'created_at' : comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'time_since_published' : comment.time_since_published(),
            'replies' : []
        } for comment in all_comments
    }

    nested_comments = []

    for comment_data in comment_map.values():
        if comment_data['parent_id']:
            parent_comment = comment_map[comment_data['parent_id']]
            if parent_comment:
                parent_comment['replies'].append(comment_data)
        else:
            nested_comments.append(comment_data)


    return nested_comments