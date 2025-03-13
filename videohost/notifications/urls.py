from django.urls import path
from .views import NotificationListView

app_name = 'notifications'

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),
]