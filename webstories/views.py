from django.shortcuts import render, get_object_or_404
from .models import WebStory
# Create your views here.

def story_detail(request, slug):

  story = get_object_or_404(
    WebStory.objects.prefetch_related('slides'),
    slug=slug,
    is_active=True
  )

  context = {
    'story': story
  }

  return render(request, template_name='webstories/story_detail.html', context=context)