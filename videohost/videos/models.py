from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid
from django.urls import reverse
import os

VISIBILITY_CHOICES = [
    ('Публичный', 'Публичный'),
    ('Приватный', 'Приватный'),
]

def user_directory_path(instance, filename):
    return os.path.join(
        'videos/videos',
        str(instance.creator.username),
        instance.created_at.strftime('%Y/%m/%d'),
        filename
    )

def user_thumbnail_path(instance, filename):
    return os.path.join(
        'videos/thumbnails',
        str(instance.creator.username),
        instance.created_at.strftime('%Y/%m/%d'),
        filename
    )

class Genre(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    icon = models.ImageField('Изображение', upload_to='icons/icons/%Y/%m/%d')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры видео'

    def __str__(self):
        return self.name

class Video(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(max_length=5000, blank=True, null=True)
    url = models.UUIDField(default=uuid.uuid4().hex, unique=True, null=False)
    visibility = models.CharField(max_length=15, default=VISIBILITY_CHOICES[0][0], choices=VISIBILITY_CHOICES)
    views = models.IntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    video = models.FileField(upload_to=user_directory_path)
    thumbnail = models.FileField(upload_to=user_thumbnail_path)

    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('videos:video-detail', args=[str(self.url)])

class Comment(models.Model):
    text = models.TextField(max_length=5000, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

class Like(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='like_set')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ('user', 'video')
        
    def __str__(self):
        return f'Лайк от {self.user} на видео: {self.video.title}'

class Subscriptions(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

class Playlist(models.Model):
    title = models.CharField(max_length=80)
    visibility = models.CharField(max_length=15, default=VISIBILITY_CHOICES[1][1], choices=VISIBILITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Плейлист'
        verbose_name_plural = 'Плейлисты'

class Saving(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    saving_playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True)
    saving_video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Сохранение'
        verbose_name_plural = 'Сохранения'

    def clean(self):
        if not self.saving_playlist and not self.saving_video:
            raise ValidationError('Вы должны сохранить либо плейлист либо видео.')
        if self.saving_playlist and self.saving_video:
            raise ValidationError('Вы не можете сохранить одновременно и плейлист и видео.')
        
class WatchHistory(models.Model):
    videos = models.ManyToManyField(Video, blank=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
