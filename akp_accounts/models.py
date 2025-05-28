from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_staff = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_subscriber = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile_images', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"