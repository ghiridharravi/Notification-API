from celery import shared_task
from django.utils import timezone
from .models import NotificationLog, UserPreference

@shared_task
def send_notification_task(notification_id, user):
    notif = NotificationLog.objects.get(id=notification_id)
    # Fake send logic
    channel = UserPreference.objects.filter(user=user)
    if len(channel) > 0:
        email = channel[0].mail
        preferred_channel = channel[0].preferred_channels
    else:
        preferred_channel = "email"
    print(f"Sending '{notif.message}' via {preferred_channel} to {email}")
    notif.status = 'sent'
    notif.sent_at = timezone.now()
    notif.save()
