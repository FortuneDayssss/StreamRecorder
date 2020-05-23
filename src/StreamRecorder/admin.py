from django.contrib import admin
from StreamRecorder.models import StreamerTask, StreamVideo, VideoChunk

admin.site.register(StreamerTask)
admin.site.register(StreamVideo)
admin.site.register(VideoChunk)
