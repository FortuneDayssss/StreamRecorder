from rest_framework import serializers
from django.contrib.auth.models import User
from StreamRecorder.models import StreamerTask, StreamVideo, VideoChunk


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')


class StreamerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamerTask
        fields = (
            'id',
            'streamer_name',
            'platform',
            'room_id',
            'room_url',
            'record_enabled',
            'record_running',
            'record_dir_path',
            'record_chunk_size_limit',
            'upload_bilibili_enabled',
            'upload_bilibili_video_name',
            'upload_bilibili_info',
            'upload_onedrive_enabled'
        )


class StreamVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamVideo
        fields = (
            'id',
            'streamer_id',
            'start_time',
            'bilibili_status',
            'onedrive_status',
            'bilibili_url',
            'onedrive_url'
        )


class VideoChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoChunk
        fields = (
            'id',
            'stream_video_id',
            'file_name',
            'full_path',
            'fs_exist',
            'discard',
            'start_time'
        )