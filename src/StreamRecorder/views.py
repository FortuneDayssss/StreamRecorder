from django.http import HttpResponse, HttpRequest
from rest_framework import viewsets
from django.contrib.auth.models import User
from StreamRecorder.models import StreamerTask, StreamVideo, VideoChunk
from StreamRecorder.serializers import UserSerializer, StreamerTaskSerializer, StreamVideoSerializer, VideoChunkSerializer


def index(request):
    return HttpResponse("hello world")


def add_task(request: HttpRequest):
    return HttpResponse(str(request.content_params))


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
