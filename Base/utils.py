from akp_news.models import *


def get_categories(request):
    return {
        'categories': NewsCategory.objects.all()
    }