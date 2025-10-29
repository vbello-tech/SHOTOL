from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.


class URL(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    slug = models.SlugField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    click_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def increment_click(self):
        """Increment click count and update last clicked time."""
        self.click_count += 1
        self.save(update_fields=['click_count', ])

    def __str__(self):
        return self.url


class UrlHistory(models.Model):
    url = models.ForeignKey(URL, related_name="clicks", on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(max_length=50, blank=True)  # mobile, desktop, tablet
    browser = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-clicked_at']

    def __str__(self):
        return f"{self.url} history"
