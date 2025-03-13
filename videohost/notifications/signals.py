from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from .models import Notification

@receiver(post_save, sender=Notification)
def send_notification_to_ws(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = f'notifications_{instance.receiver.id}'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'data': {
                    'message': instance.message,
                    'timesince': 'щойно'
                }
            }
        )