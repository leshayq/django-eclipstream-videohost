from django import forms
from .models import Video
from django.forms.widgets import FileInput
from django.core.exceptions import ValidationError
from django.conf import settings


class VideoUploadForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ('video', 'genre', 'title', 'description', 'visibility', 'thumbnail',)

    def clean_title(self):
        title = self.cleaned_data['title']

        if len(title) < 1:
            raise ValidationError("Назва повинна містити не менше 1 символу.")
        
        return title
    
    def clean_video(self):
        video = self.cleaned_data['video']

        valid_mime_types = ('video/mp4', 'video/avi', 'video/mkv')
        valid_extensions = ('.mp4', '.avi', '.mkv')

        if video != None:
            if video.size > int(settings.VIDEO_MAX_UPLOAD_SIZE):
                raise ValidationError("Файл відео не повинен перевищувати ліміт у 500МБ.")

            if video.content_type not in valid_mime_types:
                raise ValidationError("Файл відео повинен бути у форматі MP4, AVI або MKV.")
            
            if not any(video.name.endswith(extension) for extension in valid_extensions):
                raise ValidationError("Файл відео повинен мати розширення .mp4, .avi або .mkv.")

            return video
        else:
            raise ValidationError("Помилка при завантаженні файлу.")
    
    def clean_thumbnail(self):
        thumbnail = self.cleaned_data['thumbnail']

        valid_mime_types = ('image/jpeg', 'image/png')
        valid_extensions = ('.jpeg', '.jpg', '.png')

        if thumbnail != None:
            if thumbnail.size > int(settings.IMAGE_MAX_UPLOAD_SIZE):
                raise ValidationError("Файл зображення не повинен перевищувати ліміт у 20МБ.")
            
            if thumbnail.content_type not in valid_mime_types:
                raise ValidationError("Файл зображення повинен бути у форматі JPEG, JPG або PNG.")

            if not any(thumbnail.name.endswith(extension) for extension in valid_extensions):
                raise ValidationError("Файл зображення повинен мати розширення .jpeg, .jpg або .png.")

            return thumbnail
        else:
            raise ValidationError("Помилка при завантаженні файлу.")
        
class VideoEditForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'description', 'visibility', 'genre', 'thumbnail')

        widgets = {
            'thumbnail': FileInput()
        }

    def clean_title(self):
        title = self.cleaned_data['title']

        if len(title) < 1:
            raise ValidationError("Назва повинна містити не менше 1 символу.")
        
        return title
    
    def clean_thumbnail(self):
        thumbnail = self.cleaned_data['thumbnail']

        valid_mime_types = ('image/jpeg', 'image/png')
        valid_extensions = ('.jpeg', '.jpg', '.png')

        if thumbnail != None:
            if thumbnail.size > int(settings.IMAGE_MAX_UPLOAD_SIZE):
                raise ValidationError("Файл зображення не повинен перевищувати ліміт у 20МБ.")
            
            if thumbnail.content_type not in valid_mime_types:
                raise ValidationError("Файл зображення повинен бути у форматі JPEG, JPG або PNG.")

            if not any(thumbnail.name.endswith(extension) for extension in valid_extensions):
                raise ValidationError("Файл зображення повинен мати розширення .jpeg, .jpg або .png.")
            
            return thumbnail
        else:
            raise ValidationError("Помилка при завантаженні файлу.")