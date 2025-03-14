from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment
from notifications.models import Notification
from .utils import notification_comment_template

@receiver(post_save, sender=Comment)
def notificate_comment(sender, instance, created, **kwargs):
    if created:
        if instance.user != instance.video.creator:
            Notification.objects.create(
                sender=instance.user,
                receiver=instance.video.creator,
                message=notification_comment_template(instance.user.username, instance.text))