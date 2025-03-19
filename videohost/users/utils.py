from .models import Subscriptions

def notification_subscription_template(user: str) -> str:
    return f'На вас підписався користувач @{user}!'

def get_list_of_followers(user):
    followers = Subscriptions.objects.filter(following=user).only('follower').select_related('follower')
    return followers

