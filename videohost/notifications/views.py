from django.views import View
from .models import Notification
from users.models import Subscriptions
from django.http import JsonResponse
from django.utils.timesince import timesince
from django.utils.translation import gettext as _ 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import redirect

class NotificationListView(LoginRequiredMixin, View):
    login_url = '/u/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
        unread_notifications_count = Notification.objects.filter(read=False, receiver=request.user).order_by('-created_at').count()
        
        data = [
            {"message": n.message, "timesince": _(timesince(n.created_at)) + ' тому'}
            for n in notifications
        ]

        return JsonResponse({'notifications': data, 'unread_notifications_count': unread_notifications_count})

@login_required(login_url='/u/login/')
def mark_notifications_as_read(request):
    if request.method == 'POST':
        try:
            notifications = Notification.objects.filter(receiver=request.user, read=False).order_by('-created_at')
            notifications.update(read=True)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    
@login_required(login_url='/u/login/')
def disable_notifications(request, subscription_id):
    try:
        subscription = Subscriptions.objects.get(id=subscription_id)
        if subscription.notify:
            subscription.notify = False
            subscription.save(update_fields=['notify'])
            return JsonResponse({'success': 'True', 'message': 'Notifications disabled'})
    except Subscriptions.DoesNotExist:
        return JsonResponse({
            'success': 'False',
            'message': 'Subscription not found'
        }, status=404)

    
@login_required(login_url='/u/login/')
def enable_notifications(request, subscription_id):
    try:
        subscription = Subscriptions.objects.get(id=subscription_id)
        if not subscription.notify:
            subscription.notify = True
            subscription.save(update_fields=['notify'])
            return JsonResponse({'success': 'True', 'message': 'Notifications disabled'})
    except Subscriptions.DoesNotExist:
        return JsonResponse({
            'success': 'False',
            'message': 'Subscription not found'
        }, status=404)