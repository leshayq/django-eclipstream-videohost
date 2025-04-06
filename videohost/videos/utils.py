from math import floor
from django.core.exceptions import ValidationError
import subprocess
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def build_comment_tree(comments):
    grouped_comments = {}

    for comment in comments:
        if comment.parent is None:
            grouped_comments[comment.id] = {"main": comment, "replies": []}
        else:
            root_parent = comment.parent
            while root_parent.parent is not None: 
                root_parent = root_parent.parent

            if root_parent.id in grouped_comments:
                grouped_comments[root_parent.id]["replies"].append(comment)
            else:
                grouped_comments[root_parent.id] = {"main": root_parent, "replies": [comment]}

    return grouped_comments.values()


def notification_comment_template(user: str, message: str) -> str:
    return f'Користувач @{user} залишив коментар: "{message}"'

def notification_new_video_template(user: str, title: str) -> str:
    return f'На каналі @{user} з\'явилося нове відео: "{title}"'

def get_video_duration(filepath):
    try:
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of",
                                "default=noprint_wrappers=1:nokey=1", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return floor(float(result.stdout.strip()))
    except Exception as e:
        print('Помилка при отриманні тривалості відео: ', e)

def set_video_duration(video, duration):
    video.duration = duration
    video.save()

def compress_image(self, *args, **kwargs):
    try:
        img = Image.open(self.thumbnail)
        img = img.convert('RGB')

        output = BytesIO()

        img = img.resize((640, 360))

        img.save(output, format='JPEG', quality=90)
        output.seek(0)
        img.close()
        
        self.thumbnail = InMemoryUploadedFile(output, 'FileField', f'{'.'.join(self.thumbnail.name.split('.')[:-1])}.jpg', 'image/jpeg',
                                    sys.getsizeof(output), None)
    except Exception as e:
        raise ValueError('Сталася помилка при відкритті та компресуванні файлу зображення.') from e