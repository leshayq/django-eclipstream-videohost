from django import forms
from .models import Playlist

class PlaylistCreateForm(forms.ModelForm):

    class Meta:
        model = Playlist
        fields = ('title', 'visibility',)


class PlaylistEditForm(forms.ModelForm):

    class Meta:
        model = Playlist
        fields = ('title', 'visibility',)