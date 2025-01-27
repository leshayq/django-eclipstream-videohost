from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from .models import Video, Like
from .forms import VideoUploadForm
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.urls import reverse
from django.db.models import F
from django.db import transaction
from django.http import JsonResponse
import json

User = get_user_model()


class VideosListView(ListView):
    model = Video
    template_name = 'videos/index.html'
    context_object_name = 'videos'

class VideoDetailView(DetailView):
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
        if self.request.user.is_authenticated:
            context['user_has_liked'] = Like.objects.filter(user=self.request.user, video=video).exists()
        else:
            context['user_has_liked'] = False

        return context
    
def likes_video(request, url):
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
        return HttpResponseBadRequest(f"Ошибка: {str(e)}")
    return HttpResponseRedirect(reverse('videos:video-detail', args=[str(url)]))


class VideoUploadView(TemplateView):
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