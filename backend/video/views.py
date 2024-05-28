from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OriginalVideo, ProceedVideo, TimeCode
from .serializers import OriginalVideoSerializer, ProceedVideoSerializer, TimeCodeSerializer
from django.shortcuts import get_object_or_404
from django.http import FileResponse, StreamingHttpResponse, HttpResponse
import os
from wsgiref.util import FileWrapper


class OriginalVideoListAPIView(APIView):
    def get(self, request):
        videos = OriginalVideo.objects.all()
        serializer = OriginalVideoSerializer(videos, many=True)
        return Response(serializer.data)


class OriginalVideoDownloadAPIView(APIView):
    def get(self, request, pk):
        video = get_object_or_404(OriginalVideo, pk=pk)
        return self.video_stream(request, video.video.path)

    def video_stream(self, request, file_path):
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


class ProceedVideoListAPIView(APIView):
    def get(self, request, original_video_id):
        videos = ProceedVideo.objects.filter(original_video_id=original_video_id)
        serializer = ProceedVideoSerializer(videos, many=True)
        return Response(serializer.data)


class ProceedVideoDownloadAPIView(APIView):
    def get(self, request, pk):
        video = get_object_or_404(ProceedVideo, pk=pk)
        return self.video_stream(request, video.video.path)

    def video_stream(self, request, file_path):
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


class TimeCodeListAPIView(APIView):
    def get(self, request, proceed_video_id):
        timecodes = TimeCode.objects.filter(proceed_video_id=proceed_video_id)
        serializer = TimeCodeSerializer(timecodes, many=True)
        return Response(serializer.data)
