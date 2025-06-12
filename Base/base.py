from django.db import models
import uuid

def generate_uuid_hex():
    return uuid.uuid4().hex

class HomeBaseModel(models.Model):
    id = models.UUIDField(default=generate_uuid_hex, editable=False, unique=True, primary_key=True)
    meta_title = models.CharField(max_length=200, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    meta_keywords = models.TextField(null=True, blank=True)
    meta_image = models.ImageField(upload_to='meta_images', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True