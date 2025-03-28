from django import forms
from .models import Video
from django.views.generic.edit import UpdateView
from django.forms.widgets import FileInput

class VideoUploadForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ('video', 'genre', 'title', 'description', 'visibility', 'thumbnail',)

class VideoEditForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'description', 'visibility', 'genre', 'thumbnail')

        widgets = {
            'thumbnail': FileInput()
        }