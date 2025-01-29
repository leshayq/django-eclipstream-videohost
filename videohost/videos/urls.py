from django.urls import path, include
from .views import *

app_name = 'videos'

urlpatterns = [
    path('', VideosListView.as_view(), name='main-page'),
    path('upload/', VideoUploadView.as_view(), name='upload-video'),
    #watch video
    path('watch/<uuid:url>/', VideoDetailView.as_view(), name='video-detail'),
    #liking video
    path('like/<uuid:url>/', likes_video, name='likes-video'),
]