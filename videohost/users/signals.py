from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Subscriptions
from notifications.models import Notification
from .utils import notification_subscription_template

@receiver(post_save, sender=Subscriptions)
def notificate_subscription(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            sender=instance.follower,
            receiver=instance.following,
            message=notification_subscription_template(instance.follower.username))