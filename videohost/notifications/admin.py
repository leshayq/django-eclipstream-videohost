from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificaitonAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'read', 'created_at',)
    fields = ('sender', 'receiver', 'message',)