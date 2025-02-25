from django import forms
from .models import Video
from django.contrib.auth import authenticate, get_user_model


class VideoUploadForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ('video', 'genre', 'title', 'description', 'visibility', 'thumbnail',)

