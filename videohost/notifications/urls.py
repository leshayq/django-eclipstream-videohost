from django.urls import path
from .views import NotificationListView, mark_notifications_as_read

app_name = 'notifications'

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),
    path('notifications/mark-read/', mark_notifications_as_read, name='mark-notifications-as-read'),
]