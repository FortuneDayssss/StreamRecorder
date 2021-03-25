from django.http import HttpResponse, HttpRequest, JsonResponse
from rest_framework import viewsets
from django.contrib.auth.models import User
from StreamRecorder.models import StreamerTask, StreamVideo, VideoChunk
from StreamRecorder.serializers import UserSerializer, StreamerTaskSerializer, StreamVideoSerializer, VideoChunkSerializer
from StreamRecorder.tasks import *
import json


def index(request):
    return HttpResponse("hello world")


def add_task(request: HttpRequest):
    task_name = request.GET.get('task_name')
    if task_name == 'periodic_upload':
        periodic_upload.delay()
    elif task_name == 'fix_track':
        fix_track.delay(request.GET.get('video_chunk_id'))
    elif task_name == 'upload_bilibili':
        upload_bilibili.delay(request.GET.get('sv_id'))
    else:
        return JsonResponse({
            'status': 'error',
            'info': 'task not exist'
        })

    return JsonResponse({
        'status': 'success',
    })


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class StreamerTaskViewSet(viewsets.ModelViewSet):
    queryset = StreamerTask.objects.all()
    serializer_class = StreamerTaskSerializer


class StreamVideoViewSet(viewsets.ModelViewSet):
    queryset = StreamVideo.objects.all()
    serializer_class = StreamVideoSerializer


class VideoChunkViewSet(viewsets.ModelViewSet):
    queryset = VideoChunk.objects.all()
    serializer_class = VideoChunkSerializer
