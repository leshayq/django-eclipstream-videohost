from django.urls import path, include
from .views import *

app_name = 'users'

urlpatterns = [
    #retrieve channel
    path('@<slug:username>/', ChannelDetail.as_view(), name='channel-detail'),
    #subscribe to channel
    path('subscribe/<slug:username>/', subscribe_to_channel, name='subscribe-to-channel'),
    #register new user
    path('register/', register_user, name='register-user'),
    #login user
    path('login/', login_user, name='login-user'),
    # сторінка з підписками користувача
    path('subscriptions/', SubscriptionsListView.as_view(), name='subscriptions-list')
]