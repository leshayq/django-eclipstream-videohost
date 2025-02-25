from django.contrib import admin
from .models import Playlist, Saving

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'updated_at',)

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title',)}
    
@admin.register(Saving)
class SavingAdmin(admin.ModelAdmin):
    list_display = ('user', 'saving_playlist', 'created_at',)

