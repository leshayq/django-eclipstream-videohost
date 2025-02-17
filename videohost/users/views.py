from django.shortcuts import render
from django.views.generic import ListView
from videos.models import Video, Subscriptions
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, HttpResponse
from django.urls import reverse
from .forms import UserRegisterForm, UserLoginForm
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django import forms

User = get_user_model()

class ChannelDetail(ListView):
    template_name = 'users/channel_detail.html'
    context_object_name = 'channel'

    def get_queryset(self):
        username = self.kwargs.get('username')
        if username:
            queryset = Video.objects.filter(creator__username=username, visibility='Публичный')
        else:
            queryset = Video.objects.none()
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        channel_name = self.kwargs.get('username')
        video_count = self.get_queryset().count()
        channel_object = User.objects.get(username=channel_name)
        subscribers_count = Subscriptions.objects.filter(following=channel_object).count()

        if self.request.user.is_authenticated:
            is_user_subscribed = Subscriptions.objects.filter(follower=self.request.user, following=channel_object)
        else:
            is_user_subscribed = False
        
        context['channel_name'] = channel_name
        context['video_count'] = video_count
        context['subscribers_count'] = subscribers_count
        context['is_user_subscribed'] = is_user_subscribed

        return context
    
def subscribe_to_channel(request, username):
    channel_name = username
    channel_object = User.objects.get(username=channel_name)
    if request.user.username != channel_name and channel_object:
        subscription, created = Subscriptions.objects.get_or_create(follower=request.user, following=channel_object)
        if not created:
            subscription.delete()
        return HttpResponse(f"<script>window.location.href=document.referrer;</script>")
    return HttpResponseBadRequest(f"Упс.. Помилка.")


# Перенаправляє користувача на сторінку його каналу, якщо він авторизований
def redirect_if_user_authenticated(request):
    channel_object = User.objects.get(pk=request.user.pk)
    return HttpResponseRedirect(reverse('users:channel-detail', args=[channel_object]))

def register_user(request):
    if request.user.is_authenticated:
        redirect_if_user_authenticated()
    else:
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                
                return redirect('videos:main-page')
            else:
                form.add_error_css()
                return render(request, 'users/auth/register.html', {'form': form})
        form = UserRegisterForm()
        return render(request, 'users/auth/register.html', {'form': form})


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
