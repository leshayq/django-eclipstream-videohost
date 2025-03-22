from videohost.celery import app
from .models import Notification
from users.utils import get_list_of_followers_to_notify
from videos.utils import notification_new_video_template
from celery import shared_task

@shared_task
def send_new_video_notification_to_all_followers(user, title):
    followers = get_list_of_followers_to_notify(user)

    notifications = [
        Notification(
            sender=user,
            receiver=follower.follower,
            message=notification_new_video_template(user.username, title))
    for follower in followers
    ]

    Notification.objects.bulk_create(notifications, batch_size=500)