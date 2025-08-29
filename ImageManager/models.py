from django.db import models
from datetime import datetime

class UploadedImage(models.Model):
    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='uploads/')
    details = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"IMG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
