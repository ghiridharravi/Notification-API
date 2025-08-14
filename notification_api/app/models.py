from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)
    
    def __str__(self):
        return self.event_type

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mail = models.CharField(max_length=500, default="")
    preferred_channels = models.CharField(max_length=50)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    daily_limit = models.IntegerField(default=5)
    
    def __str__(self):
        return self.user.username

class NotificationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    channel = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.message
