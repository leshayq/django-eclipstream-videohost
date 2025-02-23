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


    # PLAYLIST RELATED 
    
    # list of playlists
    path('playlist/list/@<slug:username>/', PlaylistListView.as_view(), name='playlist-list'),
    # playlist detail view
    path('playlist/@<slug:username>/<slug:slug>/', PlaylistDetailView.as_view(), name='playlist-detail'),
    # saving playlist to favorites
    path('playlist/save/<slug:slug>/', save_playlist_to_favorites, name='save-playlist-to-favorites'),
    # add video to playlist
    path('video/save/<uuid:url>', add_video_to_playlist, name='add-video-to-playlist'),
    # create new playlist
    path('playlist/create/', create_new_playlist, name='create-playlist'),
]