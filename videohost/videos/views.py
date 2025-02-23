from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from .models import Video, Like, Subscriptions, Comment, Playlist, Saving
from .forms import VideoUploadForm, PlaylistCreateForm
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.urls import reverse
from django.db.models import F
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required

User = get_user_model()

class VideosListView(ListView):
    '''Головна сторінка'''
    model = Video
    template_name = 'videos/index.html'
    context_object_name = 'videos'

class VideoDetailView(DetailView):
    '''Сторінка перегляду відео'''
    model = Video
    template_name = 'videos/video_detail.html'
    context_object_name = 'video'
    slug_field = 'url'
    slug_url_kwarg = 'url'

    def get_object(self):
        video_url = self.kwargs.get('url')
        video = get_object_or_404(Video, url=video_url)

        if video:
            video.views = F('views') + 1
            video.save(update_fields=['views'])

            video.refresh_from_db()

        return video
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.object

        channel_name = self.object.creator
        channel_object = User.objects.get(username=channel_name)

        if self.request.user.is_authenticated:
            context['is_user_subscribed'] = Subscriptions.objects.filter(follower=self.request.user, following=channel_object)
            context['user_has_liked'] = Like.objects.filter(user=self.request.user, video=video).exists()
            context['is_owner'] = channel_object == self.request.user

            context['created_by_user_playlists'] = Playlist.objects.filter(creator=self.request.user)

        else:
            context['is_user_subscribed'] = False
            context['user_has_liked'] = False
        
        context['comments'] = Comment.objects.filter(video=video, parent=None).order_by('-created_at')

        return context

class VideoUploadView(TemplateView):
    '''Сторінка завантаження відео'''
    template_name = 'videos/upload_video.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = VideoUploadForm()
        return context

    def post(self, request, *args, **kwargs):
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
                video = form.save(commit=False)
                video.creator = request.user
                video.save()
        return self.render_to_response({'form': form})

class PlaylistListView(TemplateView):
    '''Сторінка перегляду списку плейлистів користувача'''
    template_name = 'videos/playlist_list.html'
    
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
    template_name = 'videos/playlist_detail.html'
    context_object_name = 'playlist'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = self.object.videos.all()

        context['user_is_owner'] = self.request.user == self.object.creator

        return context

@login_required(login_url='/u/login/')
def like_video(request, url):
    '''Лайк на відео'''
    liking_video = get_object_or_404(Video, url=request.POST.get('video_url'))
    
    user_like, created = Like.objects.get_or_create(user=request.user, video=liking_video)
    try:
        with transaction.atomic():
            if not created:
                    user_like.delete()
                    liking_video.likes_count = F('likes_count') - 1
            else:
                liking_video.likes_count = F('likes_count') + 1

            liking_video.save(update_fields=['likes_count'])
    except Exception as e:
        return HttpResponseBadRequest(f"Помилка: {str(e)}")
    return HttpResponseRedirect(reverse('videos:video-detail', args=[str(url)]))

@login_required(login_url='/u/login/')  
def comment_video(request, url, pk=None):
    '''Коментування відео'''
    if request.method == 'POST':
        text = request.POST.get('comment_text') or request.POST.get('reply_text')
        video = Video.objects.get(url=url)
        parent_id = request.POST.get('parent_id')
        if video:
            if not parent_id:
                Comment.objects.create(text=text, parent=None, video=video, user=request.user)
            else:
                parent_comment = Comment.objects.get(pk=parent_id)
                parent_comment_owner = parent_comment.user
                Comment.objects.create(text=f'@{str(parent_comment_owner)} {text}', parent=parent_comment, video=video, user=request.user)
            return HttpResponseRedirect(reverse('videos:video-detail', args=[str(url)]))

@login_required(login_url='/u/login/')  
def create_new_playlist(request):
    '''Створення нового плейлиста'''
    if request.method == 'POST':
        form = PlaylistCreateForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)

            playlist.creator = request.user
            playlist.save()

        return HttpResponseRedirect(reverse('videos:playlist-list', args=[str(request.user.username)]))

@login_required(login_url='/u/login/')  
def add_video_to_playlist(request, url):
    '''Додавання відео до плейлисту'''
    if request.method == 'POST':
        playlist_slug = request.POST.get('playlist_slug')
        playlist = Playlist.objects.get(slug=playlist_slug)
        if request.user == playlist.creator:
            video = Video.objects.get(url=url)
            if not playlist.videos.filter(url=video.url).exists():
                playlist.videos.add(video)
                return HttpResponseRedirect(reverse('videos:playlist-list', args=[str(request.user.username)]))
            return HttpResponseBadRequest("Відео вже додано до плейлисту.")
        return HttpResponseBadRequest("Ви не можете змінювати плейлисти інших користувачів.")

@login_required(login_url='/u/login/')  
def save_playlist_to_favorites(request, slug):
    '''Збереження плейлисту до обраного'''
    if request.method == 'POST':
        playlist = Playlist.objects.get(slug=slug)
        if request.user != playlist.creator:
            saving, created = Saving.objects.get_or_create(
                user=request.user, 
                saving_playlist = playlist, 
                saving_video = None)
            
            if not created:
                return HttpResponseBadRequest("Ви вже зберігли цей плейлист.")
            else:
                return HttpResponseRedirect(reverse('videos:playlist-list', args=[str(request.user.username)]))
        else:
            return HttpResponseBadRequest("Ви не можете зберігти свій плейлист.")