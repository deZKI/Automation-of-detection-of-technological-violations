from django.conf import settings

from config.celery import app

from ai.video import process_video
from video.models import OriginalVideo, ProceedVideo

@app.task
def process_video_task(original_video_id):
    try:
        original_video = OriginalVideo.objects.get(id=original_video_id)
        proceed_video = ProceedVideo.objects.create(
            original_video=original_video,
            version=settings.AI_VERSION,
        )
        process_video(original_video, proceed_video)
    except OriginalVideo.DoesNotExist:
        print(f"OriginalVideo with id {original_video_id} does not exist.")
