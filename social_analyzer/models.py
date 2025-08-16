from django.db import models
from django.contrib.auth.models import User

class SocialPost(models.Model):
    title = models.CharField(max_length=255, default="Post Title")
    description = models.TextField()
    platform = models.CharField(max_length=50)
    sentiment_score = models.FloatField()
    sentiment_label = models.CharField(max_length=20)
    emotion_label = models.CharField(max_length=20, default='netural')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
     

class TrackedKeyword(models.Model):
    keyword = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank=True)

    def __str__(self):
        return self.keyword
    
class AlertSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.ForeignKey(TrackedKeyword, on_delete=models.CASCADE)
    threshold = models.FloatField(default = 0.7)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Alert for {self.keyword.keyword} by {self.user.username}"
    
class SavedReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    report_data = models.TextField()

    def __str__(self):
        return f"{self.name} by {self.user.username}"