from django.db import models

from .tasks import process_video_task


class OriginalVideo(models.Model):
    """Изначальное необработанное видео"""
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/', blank=False)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save()
        process_video_task(self.id)


class ProceedVideo(models.Model):
    title = models.CharField(max_length=100, default='Processed')
    original_video = models.ForeignKey(OriginalVideo, on_delete=models.CASCADE)
    version = models.IntegerField(verbose_name='Версия нейросети')
    video = models.FileField(upload_to='proceed-videos/', blank=True)
    excel_file = models.FileField(upload_to='excels/', blank=True)


class TimeCode(models.Model):
    proceed_video = models.ForeignKey(ProceedVideo, on_delete=models.CASCADE)
    prediction = models.CharField(max_length=128)
    time_in_seconds = models.IntegerField()
