from akp_news.models import *
from settings.models import Settings

def get_categories(request):
    return {
        'categories': NewsCategory.objects.prefetch_related('subcategories').all().order_by('order'),
    }

def social_accounts_context(request):
    return {
        'social_accounts': SocialAccount.objects.all()
    }

def get_header_settings(request):
    try:
        return {
            'header_settings': Settings.objects.filter(key='Header')
        }
    except Settings.DoesNotExist:
        return None

def get_body_settings(request):
    try:
        return {
            'body_settings': Settings.objects.filter(key='Body')
        }
    except Settings.DoesNotExist:
        return None
