from math import floor
from django.core.exceptions import ValidationError
import subprocess

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