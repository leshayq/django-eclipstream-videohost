from django.db import models
from django.template.defaultfilters import slugify
from unidecode import unidecode
from videos.models import Video
from users.models import CustomUser
from django.urls import reverse
from django.core.exceptions import ValidationError

VISIBILITY_CHOICES = [
    ('Публічний', 'Публічний'),
    ('Приватний', 'Приватний'),
]

class Playlist(models.Model):
    title = models.CharField(max_length=80)
    visibility = models.CharField(max_length=15, default=VISIBILITY_CHOICES[1][1], choices=VISIBILITY_CHOICES)
    slug = models.SlugField('URL', max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    videos = models.ManyToManyField(Video, blank=True, related_name='playlists')

    class Meta:
        verbose_name = 'Плейлист'
        verbose_name_plural = 'Плейлисти'
        unique_together = ('slug', 'creator')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.title))
            new_slug = base_slug
            counter = 1

            while Playlist.objects.filter(slug=new_slug, creator=self.creator).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = new_slug 

        super().save(*args, **kwargs)   
    
    def get_absolute_url(self):
        return reverse('playlists:playlist-detail', args=[str(self.creator.username), str(self.slug)])
    
    def get_first_video_thumbnail(self):
        first_video = self.videos.first()
        if first_video:
            return first_video.thumbnail 
        else:
            return None

    def count_videos(self):
        return self.videos.all().count()
            

class Saving(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    saving_playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = 'Збереження'
        verbose_name_plural = 'Збереження'

    def clean(self):
        if not self.saving_playlist:
            raise ValidationError('Ви повинні вказати плейлист для зберження.')
