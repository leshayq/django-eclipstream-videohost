from django.contrib import admin

from .models import Genre, Video, Like, Subscriptions, Comment, Playlist, Saving

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fields = ('name', 'icon')
    ordering = ('name',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('creator', 'title', 'genre', 'views', 'thumbnail', 'created_at',)
    fields = ('creator', 'genre', 'title', 'description', 'thumbnail', 'url', 'visibility', 'views', 'likes_count', 'created_at', 'video')
    readonly_fields = ('creator', 'views', 'likes_count', 'url', 'video', 'created_at',)
    
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'video')
    readonly_fields = ('user', 'video')

@admin.register(Subscriptions)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at',)
    readonly_fields = ('follower', 'following', 'created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('video', 'user', 'text', 'created_at')

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'updated_at',)

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title',)}
    
@admin.register(Saving)
class SavingAdmin(admin.ModelAdmin):
    list_display = ('user', 'saving_playlist', 'saving_video', 'created_at',)
