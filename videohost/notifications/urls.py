from django.urls import path
from .views import NotificationListView, mark_notifications_as_read, disable_notifications, enable_notifications

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications-list'),
    path('mark-read/', mark_notifications_as_read, name='mark-notifications-as-read'),
 
    path('disable-notifications/<int:subscription_id>/', disable_notifications, name='disable-notifications'),
    path('enable-notifications/<int:subscription_id>/', enable_notifications, name='enable-notifications'),
]