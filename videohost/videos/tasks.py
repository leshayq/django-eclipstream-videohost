from celery import shared_task
from .utils import compress_image

@shared_task
def compress_image_delayed(video_id):
    from .models import Video

    try:
        video = Video.objects.get(pk=video_id)
        compress_image(video)
        video.save(update_fields=['thumbnail'], disable_compression=True)
    except Video.DoesNotExist:
        pass
