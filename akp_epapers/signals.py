from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Epaper, ShortURL

@receiver(post_save, sender=Epaper)
def create_short_url_for_epaper(sender, instance, created, **kwargs):
    """
    This signal is triggered automatically every time an Epaper instance is saved.
    It creates a corresponding ShortURL object.
    """
    if created and not hasattr(instance, 'short_url'):
        try:

            # Create the ShortURL object, which automatically generates a short_code
            ShortURL.objects.create(
                epaper=instance
            )
            print(f"Short URL created for newly saved Epaper: {instance.meta_title}")
        except Exception as e:
            print(f"---! ERROR creating Short URL for Epaper ID {instance.id} !---: {e}")