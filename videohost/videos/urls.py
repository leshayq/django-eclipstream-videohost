from django.urls import path, include
from .views import *

app_name = 'videos'

urlpatterns = [
    #main page
    path('', VideosListView.as_view(), name='main-page'),
    #upload video
    path('upload/', VideoUploadView.as_view(), name='upload-video'),
    #watch video
    path('watch/<uuid:url>/', VideoDetailView.as_view(), name='video-detail'),
    #liking video
    path('like/<uuid:url>/', like_video, name='likes-video'),
    #comment video
    path('comment/<uuid:url>/', comment_video, name='comment-video'),
    #reply to comment
    path('reply/<uuid:url>/<int:pk>/', comment_video, name='reply-to-comment'),
]