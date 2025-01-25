from django.contrib import admin

from .models import Genre, Video

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
    

