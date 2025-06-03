from akp_news.models import *


def get_categories(request):
    return {
        'categories': NewsCategory.objects.all()
    }

def social_accounts_context(request):
    return {
        'social_accounts': SocialAccount.objects.all()
    }