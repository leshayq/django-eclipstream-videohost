from django.views import View
from .models import Notification
from django.http import JsonResponse
from django.utils.timesince import timesince
from django.utils.translation import gettext as _ 
import locale

locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')

class NotificationListView(View):
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
        data = [
            {"message": n.message, "timesince": _(timesince(n.created_at)) + ' тому'}
            for n in notifications
        ]

        return JsonResponse({'notifications': data})