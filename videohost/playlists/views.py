from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from .models import Playlist, Saving
from videos.models import Video
from .forms import PlaylistCreateForm, PlaylistEditForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .utils import check_if_basic_playlist

class PlaylistListView(TemplateView):
    '''Сторінка перегляду списку плейлистів користувача'''
    template_name = 'playlists/playlist_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        created_by_user_playlists = Playlist.objects.filter(creator=self.request.user)
        saved_by_user_playlists = Saving.objects.filter(user=self.request.user)

        context['created_by_user_playlists'] = created_by_user_playlists
        context['saved_by_user_playlists'] = saved_by_user_playlists
        context['form'] = PlaylistCreateForm()

        return context
    
class PlaylistDetailView(DetailView):
    '''Сторінка перегляду плейлисту'''
    model = Playlist
    template_name = 'playlists/playlist_detail.html'
    context_object_name = 'playlist'
    
    def get_object(self):
        username = self.kwargs.get('username')
        playlist_slug = self.kwargs.get('slug')
        playlist = get_object_or_404(self.model, creator__username=username, slug=playlist_slug)
        return playlist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_is_owner'] = self.request.user == self.object.creator
        if context['user_is_owner']:
            context['videos'] = self.object.videos.all()
        else:
            context['videos'] = self.object.videos.filter(visibility='Публічний')
        

        context['form'] = PlaylistEditForm(instance=self.object) 
        return context

@login_required(login_url='/u/login/')  
def create_new_playlist(request):
    '''Створення нового плейлиста'''
    if request.method == 'POST':
        form = PlaylistCreateForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)

            if not check_if_basic_playlist(playlist.title):
                playlist.creator = request.user
                playlist.save()
            else:
                return HttpResponseBadRequest("Базовий плейлист з таким ім'ям вже існує.")
        return HttpResponseRedirect(reverse('playlists:playlist-list', args=[str(request.user.username)]))


@login_required(login_url='/u/login/')  
def edit_playlist(request, slug):
    '''Оновлення існуючого плейлиста'''
    if request.method == 'POST':
        playlist_object = Playlist.objects.get(creator__username=request.user.username, slug=slug)
        playlist_object_title = playlist_object.title
        form = PlaylistEditForm(data=request.POST, instance=playlist_object)
        if form.is_valid():
            playlist = form.save(commit=False)
            
            if not check_if_basic_playlist(playlist_object_title):
                playlist.creator = request.user
                playlist.save()
            else:
                return HttpResponseBadRequest("Базові плейлисти неможливо змінити.")
        return HttpResponseRedirect(reverse('playlists:playlist-list', args=[str(request.user.username)]))
    
@login_required(login_url='/u/login/')  
def delete_playlist(request, slug):
    playlist_object = Playlist.objects.get(creator__username=request.user.username, slug=slug).delete()
    return HttpResponseRedirect(reverse('playlists:playlist-list', args=[str(request.user.username)]))

@login_required(login_url='/u/login/')  
def add_video_to_playlist(request, url):
    '''Додавання відео до плейлисту'''
    if request.method == 'POST':
        playlist_slug = request.POST.get('playlist_slug')
        playlist = Playlist.objects.get(slug=playlist_slug, creator=request.user)
        video = Video.objects.get(url=url)
        if not playlist.videos.filter(url=video.url).exists():
            playlist.videos.add(video)
            return HttpResponseRedirect(reverse('playlists:playlist-list', args=[str(request.user.username)]))
        return HttpResponseBadRequest("Відео вже додано до плейлисту.")
    
@login_required(login_url='/u/login/')  
def save_playlist_to_favorites(request, username, slug):
    '''Збереження плейлисту до обраного'''
    if request.method == 'POST':
        playlist = get_object_or_404(Playlist, slug=slug, creator__username=username)
        if request.user != playlist.creator:
            saving, created = Saving.objects.get_or_create(
                user=request.user, 
                saving_playlist = playlist)
            
            if not created:
                return HttpResponseBadRequest("Ви вже зберігли цей плейлист.")
            else:
                return HttpResponseRedirect(reverse('playlists:playlist-list', args=[str(request.user.username)]))
        else:
            return HttpResponseBadRequest("Ви не можете зберігти свій плейлист.")