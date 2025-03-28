from .models import Video, Like, Comment, WatchHistory, WatchHistoryItem
from playlists.models import Playlist
from users.models import Subscriptions
from .forms import VideoUploadForm
from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.db.models import F
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .utils import build_comment_tree
from django.utils.timezone import now
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.generic.edit import UpdateView
from .forms import VideoEditForm



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

            # додавання відео у історію перегляду
            add_video_to_watch_history(user=self.request.user, video=video)


        return video

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
        
        comments = Comment.objects.filter(video=video).select_related('parent', 'user').prefetch_related('replies').order_by('created_at')
        grouped_comments = build_comment_tree(comments)

        subscribers_count = Subscriptions.objects.filter(following=channel_object).count()
        context['subscribers_count'] = subscribers_count
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
                else:
                    print('відео не знайдено/немає доступу')
        return redirect('videos:main-page')

# @login_required(login_url='/u/login/') 
# def edit_video(request, id):
#     video = get_object_or_404(Video, pk=id)

#     if request.method == 'POST':
#         pass
#     else:
#         form = 

class UpdateVideoView(UpdateView):
    model = Video
    form_class = VideoEditForm
    template_name = 'users/manage/manage_video.html'
    success_url = '/'
    slug_field = 'url'
    slug_url_kwarg = 'url'