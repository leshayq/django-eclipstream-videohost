from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import TemplateView
from videos.models import Video
from .models import Subscriptions
from playlists.models import Playlist
from videos.models import WatchHistory, WatchHistoryItem
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, HttpResponse, JsonResponse
from django.urls import reverse
from .forms import UserRegisterForm, UserLoginForm
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from notifications.utils import delete_subscription_notification
from django.db.models import Count
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomUser
from .tasks import send_verification_email_delayed
from django.core.cache import cache

User = get_user_model()

# Перегляд сторінки каналу
class ChannelDetail(TemplateView):
    template_name = 'users/channel_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        channel_name = self.kwargs.get('username')
        channel_object = get_object_or_404(User, username=channel_name) 
        
        cached_subscribers_count = cache.get(f'{channel_name}_subs_count')
        if cached_subscribers_count is not None:
            subscribers_count = cached_subscribers_count
        else:
            subscribers_count = Subscriptions.objects.filter(following=channel_object).count()
            cache.set(f'{channel_name}_subs_count', subscribers_count, 60)

        is_user_subscribed = False

        if self.request.user.is_authenticated:
            if self.request.user != channel_object:
                try:
                    user_subscription = Subscriptions.objects.get(follower=self.request.user, following=channel_object)
                    is_user_subscribed = bool(user_subscription)

                    context['subscription_id'] = user_subscription.id if user_subscription else None
                    context['enabled_notifications'] = user_subscription.notify
                except Subscriptions.DoesNotExist:
                    context['subscription_id'] = None

            is_owner = channel_object == self.request.user

        else:
            is_owner = False
        
        if is_owner:
            playlists = Playlist.objects.filter(creator=channel_object).order_by('-created_at')
            videos = Video.objects.filter(creator__username=channel_name).order_by('-created_at')
        else:
            cached_videos = cache.get(f'{channel_name}_videos')
            cached_playlists = cache.get(f'{channel_name}_playlists')

            if cached_videos:
                videos = cached_videos
            else:
                videos = list(Video.objects.filter(creator__username=channel_name, visibility='Публічний').order_by('created_at'))
                cache.set(f'{channel_name}_videos', videos, 60)

            if cached_playlists:
                playlists = cached_playlists
            else:
                playlists = list(Playlist.objects.filter(creator=channel_object, visibility='Публічний').order_by('-created_at'))
                cache.set(f'{channel_name}_playlists', playlists, 60)


        video_count = videos.count()

        context['title'] = f'{channel_name} - EclipStream'
        context['is_owner'] = is_owner
        context['channel_name'] = channel_name
        context['channel_object'] = channel_object
        context['video_count'] = video_count
        context['subscribers_count'] = subscribers_count
        context['is_user_subscribed'] = is_user_subscribed
        context['videos'] = videos
        context['playlists'] = playlists

        return context
    
class SubscriptionsListView(LoginRequiredMixin, ListView):
    model =  CustomUser
    template_name = 'users/subscriptions_list.html'
    context_object_name = 'subscriptions'
    login_url = '/u/login/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        queryset = Subscriptions.objects.filter(follower=self.request.user).only('following').select_related('following').annotate(subscribers_count=Count('following__followers'))
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'EclipStream'
        context['section_title'] = f'Підписки @{self.request.user.username}'
        return context
    
class WatchHistoryListView(LoginRequiredMixin, ListView):
    model =  WatchHistory
    template_name = 'users/watch_history.html'
    context_object_name = 'videos'
    login_url = '/u/login/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        return WatchHistoryItem.objects.filter(watch_history__user=self.request.user)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'EclipStream'
        return context
    
class ManageChannelContentView(LoginRequiredMixin, TemplateView):
    template_name = 'users/manage/manage_channel_content.html'
    login_url = '/u/login/'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['title'] = 'EclipStream'
        context['videos'] = Video.objects.filter(creator=self.request.user)
        return context
    
class ManageChannelCustomizationView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/manage/manage_channel_customization.html'
    context_object_name = 'user'
    form_class = PasswordChangeForm
    login_url = '/u/login/'
    redirect_field_name = 'redirect_to'
    
    def get_success_url(self):
        return reverse('videos:main-page')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['title'] = 'EclipStream'
        return context

# Підписка на канал користувача
@login_required(login_url='/u/login/')
def subscribe_to_channel(request, username):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'unauthenticated', 'redirect_url': f'/u/login/?next={request.path}'}, status=401)
         
        try:
            channel_name = username
            channel_object = get_object_or_404(User, username=channel_name)
            if request.user.username != channel_name and channel_object:
                subscription, created = Subscriptions.objects.get_or_create(follower=request.user, following=channel_object)
                if not created:
                    # код, який виконується якщо юзер вже був підписаний (відписка)
                    subscription.delete()
                    delete_subscription_notification(sender=request.user, receiver=channel_object)

                    return JsonResponse({'status': 'success', 'subscription_id': None})
                else:
                    return JsonResponse({'status': 'success', 'subscription_id': subscription.id})
                
            raise Http404('Invalid request.')

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
    raise Http404('Invalid request. Only POST method allowed')


# Перенаправляє користувача на сторінку його каналу, якщо він авторизований
def redirect_if_user_authenticated(request):
    channel_object = User.objects.get(pk=request.user.pk)
    return HttpResponseRedirect(reverse('users:channel-detail', args=[channel_object]))

# Реєстрація нового користувача
def register_user(request):
    if request.user.is_authenticated:
        return redirect_if_user_authenticated(request)
    else:
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.is_active = False
                # try: 
                with transaction.atomic():

                    user.save()

                    print('регистрация юзера', user.id)
                    send_verification_email_delayed.delay(user.id)

                    Playlist.objects.create(
                        title="Переглянути пізніше",
                        visibility="Приватний",
                        creator=user
                    )

                    Playlist.objects.create(
                        title="Сподобалися",
                        visibility="Приватний",
                        creator=user
                    )

                    WatchHistory.objects.create(
                        user=user
                    )

                    return redirect('users:email-verification')
                
                return redirect('videos:main-page')
            else:
                form.add_error_css()
                return render(request, 'users/auth/register.html', {'form': form})
        form = UserRegisterForm()
        return render(request, 'users/auth/register.html', {'form': form, 'title': 'Реєстрація'})

# Авторизація користувача
def login_user(request):
    if request.user.is_authenticated:
        return redirect_if_user_authenticated(request)
    else:
        if request.method == 'POST':
            form = UserLoginForm(request, data=request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user = authenticate(request, username=cd['username'], password=cd['password'])
                if user is not None:
                    login(request, user)
                    next_url = request.POST.get('next') or request.GET.get('next') or '/'
                    return redirect(next_url)
            else:
                form.add_error_css()
            return render(request, 'users/auth/login.html', {'form': form}) 

        form = UserLoginForm()
        return render(request, 'users/auth/login.html', {'form': form, 'title': 'Авторизація', 'next': request.GET.get('next', '')})

def email_verification(request):
    return render(request, 'users/verification/email_verification.html')