from django.db import models


class StreamerTask(models.Model):
    id = models.AutoField(primary_key=True)
    streamer_name = models.CharField(max_length=255, null=False)
    platform = models.CharField(max_length=255, null=False)
    room_id = models.CharField(max_length=255, null=False)
    room_url = models.CharField(max_length=255, null=False)
    record_enabled = models.BooleanField(default=False, null=False)
    record_running = models.BooleanField(default=False, null=False)
    record_dir_path = models.CharField(max_length=255, null=False)
    record_chunk_size_limit = models.CharField(max_length=255, default='3G', null=False)
    upload_bilibili_enabled = models.BooleanField(default=False, null=False)
    upload_bilibili_video_name = models.CharField(max_length=255, null=False)
    upload_bilibili_info = models.CharField(max_length=10240, null=False)
    upload_onedrive_enabled = models.BooleanField(default=False)


class StreamVideo(models.Model):
    id = models.AutoField(primary_key=True)
    streamer_id = models.ForeignKey(StreamerTask, null=True, default=None, on_delete=models.SET_DEFAULT)
    start_time = models.DateTimeField()
    bilibili_status = models.CharField(max_length=255, null=True, blank=True)
    onedrive_status = models.CharField(max_length=255, null=True, blank=True)
    bilibili_url = models.CharField(max_length=255, null=True, blank=True)
    onedrive_url = models.CharField(max_length=255, null=True, blank=True)

    def bilibili_upload_ready(self):
        if self.bilibili_status and (self.bilibili_status == "finished" or self.bilibili_status == "started"):
            return False
        return True


class VideoChunk(models.Model):
    id = models.AutoField(primary_key=True)
    stream_video_id = models.ForeignKey(StreamVideo, null=True, default=None, on_delete=models.SET_DEFAULT)
    file_name = models.CharField(max_length=255)
    full_path = models.CharField(max_length=255)
    fs_exist = models.BooleanField(default=False, null=False)
    start_time = models.DateTimeField()
