from .models import Video, Like, Comment, WatchHistory, WatchHistoryItem
from playlists.models import Playlist
from users.models import Subscriptions
from .forms import VideoUploadForm
from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse, Http404
from django.urls import reverse
from django.db.models import F
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .utils import build_comment_tree, get_video_duration
from django.utils.timezone import now
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.generic.edit import UpdateView
from .forms import VideoEditForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from random import choice
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string

User = get_user_model()

class VideosListView(ListView):
    '''Головна сторінка'''
    model = Video
    template_name = 'videos/index.html'
    context_object_name = 'videos'

    def get_queryset(self):

        popular_videos = cache.get('popular_videos')
        if popular_videos:
            queryset = popular_videos
        else:
            queryset = self.model.objects.filter(visibility='Публічний').order_by('-views')
            cache.set('popular_videos', queryset, 60)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        random_video = generate_random_video()

        context['title'] = 'EclipStream'
        context['random_video'] = random_video
        return context
    
class VideoDetailView(DetailView):
    '''Сторінка перегляду відео'''
    model = Video
    template_name = 'videos/video_detail.html'
    context_object_name = 'video'
    slug_field = 'url'
    slug_url_kwarg = 'url'

    def dispatch(self, request, *args, **kwargs):
        video = self.get_object()
        if video.visibility == 'Приватний' and video.creator != self.request.user:
            return redirect('videos:main-page')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        if not hasattr(self, 'object') or self.object is None:
            video_url = self.kwargs.get('url')
            video = get_object_or_404(Video, url=video_url)

            if video:
                video.views = F('views') + 1
                video.save(update_fields=['views'])

                video.refresh_from_db()

                # додавання відео у історію перегляду
                if self.request.user.is_authenticated:
                    add_video_to_watch_history(user=self.request.user, video=video)

                self.object = video
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.object

        channel_name = self.object.creator
        channel_object = User.objects.get(username=channel_name)

        if self.request.user.is_authenticated:
            if self.request.user != channel_object:
                try:
                    user_subscription = Subscriptions.objects.get(follower=self.request.user, following=channel_object)
                    context['is_user_subscribed'] = bool(user_subscription)

                    context['subscription_id'] = user_subscription.id if user_subscription else None
                    context['enabled_notifications'] = user_subscription.notify
                except Subscriptions.DoesNotExist:
                    context['subscription_id'] = None

            context['user_has_liked'] = Like.objects.filter(user=self.request.user, video=video).exists()
            context['is_owner'] = channel_object == self.request.user

            context['created_by_user_playlists'] = Playlist.objects.filter(creator=self.request.user)

        else:
            context['is_user_subscribed'] = False
            context['user_has_liked'] = False
        


        cached_comments = cache.get(f'{video.url}_comments')
        if cached_comments:
            grouped_comments = cached_comments
        else:
            comments = Comment.objects.filter(video=video).select_related('parent', 'user').order_by('created_at')
            grouped_comments = build_comment_tree(comments)
            cache.set(f'{video.url}_comments', grouped_comments, 60)

        cached_subscribers_count = cache.get(f'{channel_object.username}_subs_count')
        if cached_subscribers_count is not None:
            subscribers_count = cached_subscribers_count
        else:
            subscribers_count = Subscriptions.objects.filter(following=channel_object).count()
            cache.set(f'{channel_object.username}_subs_count', subscribers_count, 60)

        context['subscribers_count'] = subscribers_count
        context['grouped_comments'] = grouped_comments
        context['title'] = video.title

        return context

class VideoUploadView(LoginRequiredMixin, TemplateView):
    '''Сторінка завантаження відео'''
    template_name = 'videos/upload_video.html'
    login_url = '/u/login/'
    redirect_field_name = 'redirect_to'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_active:
            return redirect('videos:not-allowed')
        return super().dispatch(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'EclipStream'
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
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'unauthenticated', 'redirect_url': f'/u/login/?next={request.path}'}, status=401)
    
        liking_video = get_object_or_404(Video, url=url)
        
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

                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
    raise Http404('Invalid request. Only POST method allowed')

@login_required(login_url='/u/login/')  
def comment_video(request, url, pk=None):
    '''Коментування відео'''
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'unauthenticated', 'redirect_url': f'/u/login/?next={request.path}'}, status=401)
        
        text = request.POST.get('comment_text') or request.POST.get('reply_text')
        video = get_object_or_404(Video, url=url)
        parent_id = request.POST.get('parent_id')
        try:
            if video:
                if not parent_id:
                    Comment.objects.create(text=text, parent=None, video=video, user=request.user)
                    return JsonResponse({'status': 'success', 'user': request.user.username, 'parent_id': None})
                else:
                    parent_comment = Comment.objects.get(pk=parent_id)
                    parent_comment_owner = parent_comment.user
                    Comment.objects.create(text=text, parent=parent_comment, video=video, user=request.user)

                    root = parent_comment
                    while root.parent is not None:
                        root = root.parent
                    return JsonResponse({'status': 'success', 
                                         'user': request.user.username, 
                                         'parent_id': parent_id,
                                         'root_id': root.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
    raise Http404('Invalid request. Only POST method allowed')

def add_video_to_watch_history(user, video):
    watch_history, _ = WatchHistory.objects.get_or_create(user=user) 

    is_video_exists = WatchHistoryItem.objects.filter(watch_history=watch_history, video=video).exists()

    if not is_video_exists:
        WatchHistoryItem.objects.create(watch_history=watch_history, video=video)
    else:
        item = WatchHistoryItem.objects.get(watch_history=watch_history, video=video)
        item.added_at = now()
        item.save()

@login_required(login_url='/u/login/') 
def delete_video_from_watch_history(request, username, video_url):
    watch_history = get_object_or_404(WatchHistory, user__username=username)
    video = get_object_or_404(Video, url=video_url)

    WatchHistoryItem.objects.filter(watch_history=watch_history, video=video).delete()
    return HttpResponseRedirect(reverse('users:watch-history'))

@login_required(login_url='/u/login/') 
def delete_video(request):
    if request.method == 'POST':
        videos_list = request.POST.getlist('video_select_checkbox')
        if videos_list:
            for i in range(len(videos_list)):
                video = get_object_or_404(Video, pk=videos_list[i])
                if video and video.creator == request.user:
                    video.delete()
        return redirect('videos:main-page')


class UpdateVideoView(LoginRequiredMixin, UpdateView):
    model = Video
    form_class = VideoEditForm
    template_name = 'users/manage/manage_video.html'
    success_url = '/'
    slug_field = 'url'
    slug_url_kwarg = 'url'
    login_url = '/u/login/'
    redirect_field_name = 'redirect_to'

    def dispatch(self, request, *args, **kwargs):
        video = self.get_object()
        if video.visibility == 'Приватний' and video.creator != self.request.user:
            return redirect('videos:main-page')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.object.title
        return context
    
def generate_random_video():
    pks = Video.objects.values_list('pk', flat=True)
    if not pks:
        return None
    random_pk = choice(pks)
    random_obj = Video.objects.get(pk=random_pk)
    return random_obj

@require_POST
def generate_random_video_html(request):
    pks = Video.objects.filter(visibility='Публічний').values_list('pk', flat=True)
    if not pks:
        return JsonResponse({'status': 'Error', 'message': 'No videos found'}, status=404)

    random_pk = choice(pks)
    video = Video.objects.get(pk=random_pk)

    html = render_to_string('videos/include/video_card.html', {'video': video}, request=request)

    return JsonResponse({
        'status': 'Success',
        'html': html
    })