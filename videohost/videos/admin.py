from django.contrib import admin

from .models import Genre, Video, Like, Comment, WatchHistory

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

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('video', 'user', 'text', 'created_at')

@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user',)
    readonly_fields = ('videos',)

