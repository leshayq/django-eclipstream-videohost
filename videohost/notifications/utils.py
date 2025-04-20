from .models import Notification
from django.shortcuts import get_object_or_404


def delete_subscription_notification(sender, receiver):
    '''Функція призначена для пошуку та видалення повідомлення про підписку юзера на той чи інший канал при відписці'''
    notification = Notification.objects.filter(sender=sender, receiver=receiver).last()
    if notification:
          notification.delete()
