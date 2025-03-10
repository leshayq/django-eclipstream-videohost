from django.urls import path, include
from .views import *

app_name = 'playlists'

urlpatterns = [
    # PLAYLIST RELATED 
    
    # list of playlists
    path('list/@<slug:username>/', PlaylistListView.as_view(), name='playlist-list'),
    # playlist detail view
    path('@<slug:username>/<slug:slug>/', PlaylistDetailView.as_view(), name='playlist-detail'),
    # saving playlist to favorites
    path('save/<slug:username>/<slug:slug>/', save_playlist_to_favorites, name='save-playlist-to-favorites'),
    # add video to playlist
    path('video/save/<uuid:url>', add_video_to_playlist, name='add-video-to-playlist'),
    # create new playlist
    path('create/', create_new_playlist, name='create-playlist'),
    # update existing playlist
    path('update/<slug:slug>/', edit_playlist, name='edit-playlist'),
    # delete existing playlist
    path('delete/<slug:slug>/', delete_playlist, name='delete-playlist'),
]