from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    is_staff = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_subscriber = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile_images', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    epaper_downloads = models.PositiveIntegerField(default=0, help_text="Number of E-Paper downloads")

    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    

class AdminLoginAttempt(models.Model):
    username_attempt = models.CharField(max_length=255, help_text="The username attempted to log in")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The user account if the username matched an existing staff user.",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    LOGIN_STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED_CREDENTIALS', 'Failed - Wrong Credentials'),
        ('FAILED_CONCURRENT_LIMIT', 'Failed - Concurrent Limit Reached'),
        ('FAILED_NOT_STAFF', 'Failed - Not a Staff Account'),
        ('FAILED_OTHER', 'Failed - Other Reason'),
    ]
    status = models.CharField(max_length=50, choices=LOGIN_STATUS_CHOICES)
    failure_reason = models.TextField(null=True, blank=True, help_text="Details if the login failed.")

    def __str__(self):
        return f"Attempt for {self.username_attempt} from {self.ip_address} at {self.timestamp} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Admin Login Attempt"
        verbose_name_plural = "Admin Login Attempts"
        ordering = ['-timestamp']