from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import (OriginalVideoListAPIView, OriginalVideoDownloadAPIView,
                    ProceedVideoListAPIView, ProceedVideoDownloadAPIView,
                    TimeCodeListAPIView, TaskStatusAPIView)

urlpatterns = [
    path('api/videos/tasks/<str:task_id>/', TaskStatusAPIView.as_view(), name='task-status'),
    path('api/videos/', csrf_exempt(OriginalVideoListAPIView.as_view({'get': 'list', 'post': 'create'})), name='original-video-list'),
    path('api/videos/<int:pk>/download/', OriginalVideoDownloadAPIView.as_view(), name='original-video-download'),
    path('api/proceed-videos/<int:original_video_id>/', ProceedVideoListAPIView.as_view(), name='proceed-video-list'),
    path('api/proceed-videos/<int:pk>/download/', ProceedVideoDownloadAPIView.as_view(), name='proceed-video-download'),
    path('api/timecodes/<int:proceed_video_id>/', TimeCodeListAPIView.as_view(), name='timecode-list'),
]
