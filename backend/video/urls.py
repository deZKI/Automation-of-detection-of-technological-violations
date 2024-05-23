from django.urls import path
from .views import upload_video, video_list, video_stream

urlpatterns = [
    path('upload/', upload_video, name='upload_video'),
    path('', video_list, name='video_list'),
    path('video/<int:video_id>/', video_stream, name='video_stream'),
]
