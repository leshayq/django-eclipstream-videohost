from .models import Video, Like, Comment
from playlists.models import Playlist, Saving
from users.models import Subscriptions
from playlists.forms import PlaylistCreateForm
from .forms import VideoUploadForm
from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.urls import reverse
from django.db.models import F
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .utils import build_comment_tree

User = get_user_model()

class VideosListView(ListView):
    '''Головна сторінка'''
    model = Video
    template_name = 'videos/index.html'
    context_object_name = 'videos'

    def get_queryset(self):
        queryset = self.model.objects.filter(visibility='Публічний')
        return queryset

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
        
        comments = Comment.objects.filter(video=video).select_related('parent', 'user').prefetch_related('replies').order_by('created_at')
        grouped_comments = build_comment_tree(comments)
        context['grouped_comments'] = grouped_comments
 
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


@login_required(login_url='/u/login/')
def like_video(request, url):
    '''Лайк на відео'''
    liking_video = get_object_or_404(Video, url=request.POST.get('video_url'))
    
    user_like, created = Like.objects.get_or_create(user=request.user, video=liking_video)
    try:
        with transaction.atomic():
            liked_by_user_playlist = Playlist.objects.get(slug='spodobalisia', creator=request.user)

            if not created:
                    user_like.delete()
                    liking_video.likes_count = F('likes_count') - 1

                    liked_by_user_playlist.videos.remove(liking_video)
            else:
                liking_video.likes_count = F('likes_count') + 1

                liked_by_user_playlist.videos.add(liking_video)

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
