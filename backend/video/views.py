import os

from django.shortcuts import get_object_or_404
from django.http.request import HttpRequest
from django.http import StreamingHttpResponse, HttpResponse

from wsgiref.util import FileWrapper

from drf_yasg.utils import swagger_auto_schema
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .tasks import process_video_task
from .models import OriginalVideo, ProceedVideo, TimeCode
from .serializers import OriginalVideoSerializer, ProceedVideoSerializer, TimeCodeSerializer


class OriginalVideoListAPIView(ModelViewSet):
    """ Получение списка оригинальных видео """
    queryset = OriginalVideo.objects.all()
    serializer_class = OriginalVideoSerializer
    parser_classes = (FormParser, MultiPartParser, FileUploadParser)

    @swagger_auto_schema(
        operation_description="Загрузка нового оригинального видео",
        request_body=OriginalVideoSerializer,
        responses={HTTP_201_CREATED: OriginalVideoSerializer, HTTP_400_BAD_REQUEST: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        serializer = OriginalVideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            process_video_task.delay(serializer.data.id)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ProceedVideoListAPIView(APIView):
    """ Получение списка обработанных видео по Оригинальному видео"""

    def get(self, request: HttpRequest, original_video_id: int):
        videos = ProceedVideo.objects.filter(original_video_id=original_video_id)
        serializer = ProceedVideoSerializer(videos, many=True)
        return Response(serializer.data)


class TimeCodeListAPIView(APIView):
    """ Получение списка таймкодов по обработанному видео"""

    def get(self, request: HttpRequest, proceed_video_id: int):
        timecodes = TimeCode.objects.filter(proceed_video_id=proceed_video_id)
        serializer = TimeCodeSerializer(timecodes, many=True)
        return Response(serializer.data)


class VideoDownloadAPIView(APIView):
    """ Апи для стриминга видео """

    def video_stream(self, request: HttpRequest, file_path: str):
        file_size = os.path.getsize(file_path)
        range_header = request.headers.get('Range', None)
        if range_header:
            start, end = range_header.replace('bytes=', '').split('-')
            start = int(start)
            end = int(end) if end else file_size - 1
            length = end - start + 1

            with open(file_path, 'rb') as f:
                f.seek(start)
                data = f.read(length)

            response = HttpResponse(data, status=206, content_type='video/mp4')
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Accept-Ranges'] = 'bytes'
            response['Content-Length'] = str(length)
        else:
            response = StreamingHttpResponse(FileWrapper(open(file_path, 'rb')), content_type='video/mp4')
            response['Content-Length'] = str(file_size)
            response['Accept-Ranges'] = 'bytes'

        return response


class ProceedVideoDownloadAPIView(VideoDownloadAPIView):
    """ Загрузка обработанного видео """

    def get(self, request: HttpRequest, pk: int):
        video = get_object_or_404(ProceedVideo, pk=pk)
        return self.video_stream(request, video.video.path)


class OriginalVideoDownloadAPIView(VideoDownloadAPIView):
    """ Загрузка оригинального видео """

    def get(self, request: HttpRequest, pk: int):
        video = get_object_or_404(OriginalVideo, pk=pk)
        return self.video_stream(request, video.video.path)
