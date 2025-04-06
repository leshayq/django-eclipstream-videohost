from django.urls import path, include, reverse_lazy
from .views import *
from videos.views import delete_video_from_watch_history
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

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

    path('password-reset/', PasswordResetView.as_view(
        template_name='users/password_reset/password_reset_form.html',
        email_template_name='users/password_reset/password_reset_email.html',
        success_url = reverse_lazy('users:password-reset-done')
        ), name="password-reset"),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset/password_reset_done.html'), name="password-reset-done"),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='users/password_reset/password_reset_confirm.html',
        success_url = reverse_lazy('users:password-reset-complete')
        ), name="password-reset-confirm"),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(template_name='users/password_reset/password_reset_complete.html'), name="password-reset-complete"),

]