from django.db import models


class OriginalVideo(models.Model):
    """ Изначальное необработанное видео """
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/')


class ProceedVideo(models.Model):
    title = models.CharField(max_length=100, default='Procceedd')
    original_video = models.ForeignKey(to=OriginalVideo, on_delete=models.CASCADE)
    version = models.IntegerField(verbose_name='Версия нейроки')
    video = models.FileField(upload_to='proceed-videos/')


class TimeCode(models.Model):
    proceed_video = models.ForeignKey(to=ProceedVideo, on_delete=models.CASCADE)
    prediction = models.CharField(max_length=128)  # Потом изменится
    time_in_seconds = models.IntegerField()
