from django.shortcuts import render
from django.views.generic import ListView
from videos.models import Video, Subscriptions
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, HttpResponse
from django.urls import reverse

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
        is_user_subscribed = Subscriptions.objects.filter(follower=self.request.user, following=channel_object)
        
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