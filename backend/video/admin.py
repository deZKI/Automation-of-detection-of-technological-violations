from django.contrib import admin
from video.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    pass
