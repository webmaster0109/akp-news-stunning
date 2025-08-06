from django.db import models

# Create your models here.

class Settings(models.Model):
    KEY__CHOICES = (
        ('Header', 'Header'),
        ('Body', 'Body'),
    )
    key = models.CharField(max_length=255, choices=KEY__CHOICES, default="Header")
    value = models.TextField()

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"

    def __str__(self):
        return self.key