from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import TemplateView
from videos.models import Video
from .models import Subscriptions
from playlists.models import Playlist
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, HttpResponse
from django.urls import reverse
from .forms import UserRegisterForm, UserLoginForm
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django import forms
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.text import slugify
from unidecode import unidecode
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from notifications.utils import delete_subscription_notification
from django.db.models import Count

User = get_user_model()

# Перегляд сторінки каналу
class ChannelDetail(TemplateView):
    template_name = 'users/channel_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        channel_name = self.kwargs.get('username')

        channel_object = get_object_or_404(User, username=channel_name) 
        
        subscribers_count = Subscriptions.objects.filter(following=channel_object).count()

        if self.request.user.is_authenticated:
            is_user_subscribed = Subscriptions.objects.filter(follower=self.request.user, following=channel_object)

            is_owner = channel_object == self.request.user

        else:
            is_owner = False
            is_user_subscribed = False
        
        if is_owner:
            playlists = Playlist.objects.filter(creator=channel_object)
            videos = Video.objects.filter(creator__username=channel_name)
        else:
            playlists = Playlist.objects.filter(creator=channel_object, visibility='Публічний')
            videos = Video.objects.filter(creator__username=channel_name, visibility='Публічний')

        video_count = videos.count()

        context['is_owner'] = is_owner
        context['channel_name'] = channel_name
        context['video_count'] = video_count
        context['subscribers_count'] = subscribers_count
        context['is_user_subscribed'] = is_user_subscribed
        context['videos'] = videos
        context['playlists'] = playlists

        return context
    
class SubscriptionsListView(ListView):
    template_name = 'users/subscriptions_list.html'
    context_object_name = 'subscriptions'

    def get_queryset(self):
        queryset = Subscriptions.objects.filter(follower=self.request.user).only('following').select_related('following').annotate(subscribers_count=Count('following__followers'))
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['section_title'] = f'Підписки @{self.request.user.username}'
        return context

# Підписка на канал користувача
@login_required(login_url='/u/login/')
def subscribe_to_channel(request, username):
    channel_name = username
    channel_object = User.objects.get(username=channel_name)
    if request.user.username != channel_name and channel_object:
        subscription, created = Subscriptions.objects.get_or_create(follower=request.user, following=channel_object)
        if not created:
            # код, який виконується якщо юзер вже був підписаний (відписка)
            subscription.delete()
            delete_subscription_notification(sender=request.user, receiver=channel_object)

        return HttpResponse(f"<script>window.location.href=document.referrer;</script>")
    return HttpResponseBadRequest(f"Упс.. Помилка.")


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

                try: 
                    with transaction.atomic():
                        user.save()

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
                    
                except Exception as e:
                    return HttpResponseBadRequest(f"Помилка: {str(e)}")
                
                return redirect('videos:main-page')
            else:
                form.add_error_css()
                return render(request, 'users/auth/register.html', {'form': form})
        form = UserRegisterForm()
        return render(request, 'users/auth/register.html', {'form': form})

# Авторизація користувача
def login_user(request):
    if request.user.is_authenticated:
        redirect_if_user_authenticated()
    else:
        if request.method == 'POST':
            form = UserLoginForm(request, data=request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user = authenticate(request, username=cd['username'], password=cd['password'])
                if user is not None:
                    login(request, user)
                    return redirect('videos:main-page')
            else:
                form.add_error_css()
            return render(request, 'users/auth/login.html', {'form': form}) 

        form = UserLoginForm()
        return render(request, 'users/auth/login.html', {'form': form})
