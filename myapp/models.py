from django.db import models

# Create your models here.

class PostImage(models.Model):
    image = models.ImageField(upload_to='Images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
