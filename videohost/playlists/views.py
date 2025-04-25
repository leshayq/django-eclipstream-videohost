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
from unidecode import unidecode
from django.template.defaultfilters import slugify
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache

class PlaylistListView(LoginRequiredMixin, TemplateView):
    '''Сторінка перегляду списку плейлистів користувача'''
    template_name = 'playlists/playlist_list.html'
    login_url = '/u/login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        created_by_user_playlists = None
        saved_by_user_playlists = None

        if self.request.user.is_authenticated:

            cached_created_by_user_playlists = cache.get(f'{self.request.user.username}_created_playlists')
            cached_saved_by_user_playlists = cache.get(f'{self.request.user.username}_saved_playlists')

            if cached_created_by_user_playlists:
                created_by_user_playlists = cached_created_by_user_playlists
            else:
                created_by_user_playlists = list(Playlist.objects.filter(creator=self.request.user))
                cache.set(f'{self.request.user.username}_created_playlists', created_by_user_playlists, 300)

            if cached_saved_by_user_playlists:
                saved_by_user_playlists = cached_saved_by_user_playlists
            else:
                saved_by_user_playlists = Saving.objects.filter(user=self.request.user)
                cache.set(f'{self.request.user.username}_saved_playlists', saved_by_user_playlists, 300)


        context['title'] = 'Список плейлистів'
        context['created_by_user_playlists'] = created_by_user_playlists
        context['saved_by_user_playlists'] = saved_by_user_playlists
        context['form'] = PlaylistCreateForm()

        return context


class PlaylistDetailView(DetailView):
    '''Сторінка перегляду плейлисту'''
    model = Playlist
    template_name = 'playlists/playlist_detail.html'
    context_object_name = 'playlist'
    
    def dispatch(self, request, *args, **kwargs):
        playlist = self.get_object()
        if playlist.visibility == 'Приватний' and playlist.creator != self.request.user:
            return redirect('videos:main-page')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        username = self.kwargs.get('username')
        playlist_slug = self.kwargs.get('slug')
        playlist = get_object_or_404(self.model, creator__username=username, slug=playlist_slug)
        return playlist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_is_owner'] = self.request.user == self.object.creator
        if context['user_is_owner']:
            playlist_videos = self.object.videos.all()
        else:

            cached_videos = cache.get(f'{self.request.user.username}_{self.object.title}_playlist_videos')
            if cached_videos:
                playlist_videos = cached_videos
            else:
                playlist_videos = list(self.object.videos.filter(visibility='Публічний'))
                cache.set(f'{self.request.user.username}_{self.object.title}_playlist_videos', playlist_videos, 60)
        
        context['videos'] = playlist_videos
        context['title'] = self.object.title
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
        return HttpResponseRedirect(reverse('playlists:playlist-list'))


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
                playlist.slug = slugify(unidecode(playlist.title))
                playlist.save()
            else:
                return HttpResponseBadRequest("Базові плейлисти неможливо змінити.")
        return HttpResponseRedirect(reverse('playlists:playlist-list'))
    
@login_required(login_url='/u/login/')  
def delete_playlist(request, slug):
    playlist_object = Playlist.objects.get(creator__username=request.user.username, slug=slug).delete()
    return HttpResponseRedirect(reverse('playlists:playlist-list'))

@login_required(login_url='/u/login/')  
def add_video_to_playlist(request, url):
    '''Додавання відео до плейлисту'''
    if request.method == 'POST':
        playlist_slug = request.POST.get('playlist_slug')
        playlist = Playlist.objects.get(slug=playlist_slug, creator=request.user)
        video = Video.objects.get(url=url)
        if not playlist.videos.filter(url=video.url).exists():
            if request.user == playlist.creator: 
                playlist.videos.add(video)
            else:
                return HttpResponseBadRequest("Відео можна додавати тількі у свої плейлисти.")
            
            return HttpResponseRedirect(reverse('playlists:playlist-list'))
        return HttpResponseRedirect(reverse('playlists:playlist-list'))
    
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