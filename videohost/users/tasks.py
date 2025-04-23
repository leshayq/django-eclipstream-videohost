from celery import shared_task
from django_email_verification import send_email
from django.core.mail import send_mail
from .models import CustomUser

@shared_task
def send_verification_email_delayed(user_id):
    user = CustomUser.objects.get(pk=user_id)
    send_email(user)

@shared_task
def send_email_async(subject, message, from_email, recipient_list, html_message=None):
    send_mail(subject, message, from_email, recipient_list, html_message=html_message)