from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from .models import Video
from .forms import VideoUploadForm
from django.contrib.auth import get_user_model

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
                # video = Video.objects.create()
        return self.render_to_response({'form': form})