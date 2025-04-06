from django.db import models
from users.models import CustomUser
import uuid
from django.urls import reverse
import os
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from .utils import compress_image

VISIBILITY_CHOICES = [
    ('Публічний', 'Публічний'),
    ('Приватний', 'Приватний'),
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
    icon = models.ImageField('Зображення', upload_to='icons/icons/%Y/%m/%d')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанри відео'

    def __str__(self):
        return self.name

class Video(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(max_length=5000, blank=True, null=True)
    url = models.UUIDField(default=uuid.uuid4, unique=True, null=False)
    visibility = models.CharField(max_length=15, default=VISIBILITY_CHOICES[0][0], choices=VISIBILITY_CHOICES)
    views = models.IntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(default=0, null=False)

    video = models.FileField(upload_to=user_directory_path)
    thumbnail = models.FileField(upload_to=user_thumbnail_path)

    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Відео'
        verbose_name_plural = 'Відео'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('videos:video-detail', args=[str(self.url)])
    
    def count_comments(self):
        count_of_comments = Comment.objects.filter(video=self).count()
        return count_of_comments
    
    def save(self, *args, **kwargs):
        if self.pk:
            old_video = Video.objects.get(pk=self.pk)
            if old_video.thumbnail == self.thumbnail:
                return super().save(*args, **kwargs)
        compress_image(self)

        return super().save(*args, **kwargs)

class Comment(models.Model):
    text = models.TextField(max_length=5000, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'

class Like(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='like_set')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ('user', 'video')
        
    def __str__(self):
        return f'Лайк від {self.user} на відео: {self.video.title}'
        
class WatchHistory(models.Model):
    videos = models.ManyToManyField(Video, through='WatchHistoryItem', blank=True)

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class WatchHistoryItem(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watch_history = models.ForeignKey(WatchHistory, on_delete=models.CASCADE)
    added_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-added_at']