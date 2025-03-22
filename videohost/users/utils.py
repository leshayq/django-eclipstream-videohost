from .models import Subscriptions

def notification_subscription_template(user: str) -> str:
    return f'На вас підписався користувач @{user}!'

def get_list_of_followers_to_notify(user):
    followers = Subscriptions.objects.filter(following=user, notify=True).only('follower').select_related('follower')
    return followers

