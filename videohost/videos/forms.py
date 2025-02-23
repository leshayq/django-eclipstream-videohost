from django import forms
from .models import Video, Playlist
from django.contrib.auth import authenticate, get_user_model


class VideoUploadForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ('video', 'genre', 'title', 'description', 'visibility', 'thumbnail',)

class PlaylistCreateForm(forms.ModelForm):

    class Meta:
        model = Playlist
        fields = ('title', 'visibility',)