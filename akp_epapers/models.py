from django.db import models
from Base.base import HomeBaseModel
from akp_accounts.models import CustomUser
from akp_news.base import BaseModel
# Create your models here.


class Epaper(HomeBaseModel):
    file = models.FileField(upload_to='epapers/')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "E-Papers"
    
    def __str__(self):
        return self.meta_title


class EpaperDownload(BaseModel):
    epaper = models.ForeignKey(Epaper, on_delete=models.CASCADE, related_name='downloads')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='epapers_downloads')
    ip_addr = models.CharField(max_length=50, null=True, blank=True)
    downloads_limit = models.PositiveIntegerField(default=5)  # Number of downloads allowed per month

    class Meta:
        verbose_name_plural = "E-Paper Downloads"

    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.epaper}"