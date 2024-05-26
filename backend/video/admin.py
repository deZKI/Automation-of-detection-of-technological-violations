from django.contrib import admin
from video.models import OriginalVideo, ProceedVideo, TimeCode


@admin.register(OriginalVideo)
class OriginalVideoAdmin(admin.ModelAdmin):
    pass


@admin.register(ProceedVideo)
class ProceedVideoAdmin(admin.ModelAdmin):
    pass

@admin.register(TimeCode)
class TimeCodeAdmin(admin.ModelAdmin):
    pass