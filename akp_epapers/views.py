from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Epaper, EpaperDownload, ShortURL

# Create your views here.

def view_epaper(request, epaper_id):
    epaper = get_object_or_404(Epaper, id=epaper_id)
    filename = str(epaper.file.name).split('/')[-1]

    short_url, created = ShortURL.objects.get_or_create(epaper=epaper)
    if created:
        short_url.save()

    context = {
        'epaper': epaper,
        'filename': filename,
    }

    return render(request, template_name="epapers/epaper_detail.html", context=context)

def redirect_short_url(request, short_url):
    short_url_obj = get_object_or_404(ShortURL, short_url=short_url)

    return redirect(short_url_obj.epaper.get_new_absolute_url())

@login_required
def download_epaper_view(request, epaper_id):
    epaper = get_object_or_404(Epaper, id=epaper_id)

    DOWNLOAD_LIMIT = 365

    if request.user.epaper_downloads >= DOWNLOAD_LIMIT:
        return JsonResponse({'status': 'error', 'message': 'You have reached the download limit for this epaper.'}, status=400)
    
    request.user.epaper_downloads += 1
    request.user.save()

    EpaperDownload.objects.create(customer=request.user, epaper=epaper)

    if epaper.file and hasattr(epaper.file, 'url'):
        return redirect(epaper.file.url)
        return JsonResponse({'status': 'success', 'url': epaper.file.url}, status=200)
    else:
        return JsonResponse({'status': 'error', 'message': 'E-Paper file not found.'}, status=404)
    