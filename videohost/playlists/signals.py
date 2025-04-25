from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Playlist, Saving
from django.core.cache import cache

@receiver(post_save, sender=Playlist)
def delete_cached_created_playlists_on_save(sender, instance, created, **kwargs):
    cache.delete(f'{instance.creator.username}_created_playlists')

@receiver(post_delete, sender=Playlist)
def delete_cached_created_playlists_on_delete(sender, instance, **kwargs):
    cache.delete(f'{instance.creator.username}_created_playlists')

@receiver(post_save, sender=Saving)
def delete_cached_saved_playlists_on_save(sender, instance, created, **kwargs):
    cache.delete(f'{instance.user.username}_saved_playlists')

@receiver(post_delete, sender=Saving)
def delete_cached_saved_playlists_on_delete(sender, instance, **kwargs):
    cache.delete(f'{instance.user.username}_saved_playlists')