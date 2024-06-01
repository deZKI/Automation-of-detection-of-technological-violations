from django.db import models


class OriginalVideo(models.Model):
    """Изначальное необработанное видео"""
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/', blank=False)


class ProceedVideo(models.Model):
    title = models.CharField(max_length=100, default='Processed')
    original_video = models.ForeignKey(OriginalVideo, on_delete=models.CASCADE)
    version = models.IntegerField(verbose_name='Версия нейросети')
    video = models.FileField(upload_to='proceed-videos/', blank=True)
    excel_file = models.FileField(upload_to='excels/', blank=True)
    pdf_file = models.FileField(upload_to='pdf/', blank=True)


class TimeCode(models.Model):
    proceed_video = models.ForeignKey(ProceedVideo, on_delete=models.CASCADE)
    prediction = models.CharField(max_length=128)
    time_in_seconds = models.IntegerField()
