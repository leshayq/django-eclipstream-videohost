from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video, Comment
from notifications.models import Notification
from .utils import notification_comment_template
from notifications.tasks import send_new_video_notification_to_all_followers
from .utils import get_video_duration, set_video_duration
from django.http import Http404

@receiver(post_save, sender=Comment)
def notificate_comment(sender, instance, created, **kwargs):
    if created:
        if instance.user != instance.video.creator:
            Notification.objects.create(
                sender=instance.user,
                receiver=instance.video.creator,
                message=notification_comment_template(instance.user.username, instance.text))

@receiver(post_save, sender=Video)
def notificate_new_video(sender, instance, created, **kwargs):
    if created:
        send_new_video_notification_to_all_followers(instance.creator, instance.title)

@receiver(post_save, sender=Video)
def validate_video_duration(sender, instance, created, **kwargs):
    if created:
        duration = get_video_duration(instance.video.path)
        if duration > 61:
            instance.delete()
            raise Http404
        else:
            set_video_duration(video=instance, duration=duration)