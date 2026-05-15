import uuid
from django.db import models
from django.utils import timezone

class Announcement(models.Model):
    """Model for dynamic announcements"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(help_text="Announcement content/message")
    is_active = models.BooleanField(default=True, help_text="Show this announcement on homepage")
    order = models.IntegerField(default=0, help_text="Order of display (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiry date")
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
    
    def __str__(self):
        return self.content[:50] + "..." if len(self.content) > 50 else self.content
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class CarouselImage(models.Model):
    """Model for homepage carousel images"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='carousel/', help_text="Upload landscape image (1920x1080 recommended)")
    order = models.IntegerField(default=0, help_text="Order of display (lower numbers first)")
    is_active = models.BooleanField(default=True, help_text="Show this image in carousel")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Carousel Image"
        verbose_name_plural = "Carousel Images"
    
    def __str__(self):
        return f"Image {self.order}"