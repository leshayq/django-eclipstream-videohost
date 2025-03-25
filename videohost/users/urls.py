from django.urls import path, include
from .views import *
from videos.views import delete_video_from_watch_history

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
    path('subscriptions/', SubscriptionsListView.as_view(), name='subscriptions-list'),
    # сторінка історія перегляду відео
    path('wh/', WatchHistoryListView.as_view(), name='watch-history'),
    # видалити відео з історії перегляду
    path('wh/delete-video/<slug:username>/<uuid:video_url>/', delete_video_from_watch_history, name='wh-delete-video'),
    path('manage/content/', ManageChannelContentView.as_view(), name='manage-channel-content'),
    path('manage/customization/', ManageChannelCustomizationView.as_view(), name='manage-channel-customization'),
]