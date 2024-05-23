from django.shortcuts import render, redirect, get_object_or_404

from .models import Video
from .forms import VideoForm
from django.http import StreamingHttpResponse, HttpResponse
import os
from wsgiref.util import FileWrapper


def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('video_list')
    else:
        form = VideoForm()
    return render(request, 'video/upload_video.html', {'form': form})


def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video/video_list.html', {'videos': videos})


def video_stream(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    file_path = video.file.path
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
