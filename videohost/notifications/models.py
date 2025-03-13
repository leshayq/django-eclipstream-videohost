from django.db import models
from users.models import CustomUser

class Notification(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications', verbose_name='Відправник')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_notifications', verbose_name='Отримувач')
    message = models.TextField(null=False)
    read = models.BooleanField(default=False,null=False)
    created_at = models.DateTimeField(auto_now_add=True)