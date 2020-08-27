from django.utils import timezone
from celery import shared_task
from StreamRecorder.models import StreamerTask, StreamVideo, VideoChunk
from record.factory import RecorderFactory
from datetime import timedelta
import os.path
from util.file import parse_file_size
import upload.bilibili
import bilibiliuploader
import json
import StreamRecorder.settings


@shared_task
def probe_and_download(streamer_task_id):
    try:
        st = StreamerTask.objects.get(id=streamer_task_id)
    except:
        return "error when finding StreamerTask in db"

    recorder = RecorderFactory(platform_name=st.platform)
    if recorder is None:
        return "platform error"

    try:
        if recorder.probe(st.room_id):
            record_time = timezone.now()
            file_name = "{}_{}.flv".format(st.room_id, str(int(record_time.timestamp())))
            full_path = os.path.join(st.record_dir_path, file_name)
            sv = StreamVideo.objects.filter(streamer_id=st).order_by('-start_time').first()
            if not sv:
                sv = StreamVideo(
                    streamer_id=st,
                    start_time=record_time,
                )
                sv.save()
            else:
                last_chunk = VideoChunk.objects.filter(stream_video_id=sv).order_by('-start_time').first()
                if not last_chunk:
                    last_chunk_time = sv.start_time
                else:
                    last_chunk_time = last_chunk.start_time
                if last_chunk_time.timestamp() < (record_time - timedelta(hours=5)).timestamp():
                    sv = StreamVideo(
                        streamer_id=st,
                        start_time=record_time,
                    )
                    sv.save()
            new_chunk = VideoChunk(
                stream_video_id=sv,
                file_name=file_name,
                full_path=full_path,
                fs_exist=True,
                start_time=record_time
            )
            new_chunk.save()
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            recorder.download(st.room_id, full_path, parse_file_size(st.record_chunk_size_limit))
    finally:
        st.record_running = False
        st.save()


@shared_task
def periodic_record():
    result = ""
    sts = StreamerTask.objects.all().filter(record_enabled=True, record_running=False)

    for st in sts:
        st.record_running = True
        probe_and_download.delay(st.id)
        result += st.streamer_name + ","
        st.save()
    print(result)
    return result


@shared_task
def upload_bilibili(sv_id):
    def parse_title_date(origin_title, title_datetime=timezone.now()):
        if origin_title.__contains__("{date}"):
            origin_title = origin_title.format(
                date="{}年{}月{}日".format(title_datetime.year, title_datetime.month, title_datetime.day))
        return origin_title

    sv = StreamVideo.objects.filter(id=sv_id).first()
    if not sv:
        return "stream video id {} not found".format(sv_id)
    st = StreamerTask.objects.filter(id=sv.streamer_id.id).first()
    if not st:
        return "streamer task id {} not found".format(sv_id)

    try:
        cover = st.upload_bilibili_cover_file_path
        vchunks = VideoChunk.objects.filter(stream_video_id=sv).order_by('start_time')
        parts = []
        part_counter = 0
        for chunk in vchunks:
            if os.path.isfile(chunk.full_path):
                part_counter += 1
                part = bilibiliuploader.VideoPart(
                    path=chunk.full_path,
                    title="P{}".format(part_counter)
                )
                parts.append(part)

        binfo_json = json.loads(st.upload_bilibili_info)
        upload.bilibili.upload(
            username=StreamRecorder.settings.BILIBILI_USERNAME,
            password=StreamRecorder.settings.BILIBILI_PASSWORD,
            parts=parts,
            title=parse_title_date(binfo_json['title'], sv.start_time),
            tid=int(binfo_json['tid']),
            tag=",".join(binfo_json['tag']),
            description=parse_title_date(binfo_json['title'], sv.start_time),
            source=binfo_json['source'],
            no_reprint=int(binfo_json['no_reprint']),
            open_elec=int(binfo_json['open_elec']),
            copyright=2,
            cover=cover
        )
    except:
        sv.bilibili_status = 'fail'
        sv.save()
    finally:
        if sv.bilibili_status != 'fail':
            sv.bilibili_status = "finished"
            sv.save()


@shared_task
def periodic_upload():
    def record_finished(stream_video):
        if not stream_video:
            return False
        last_chunk = VideoChunk.objects.all().filter(stream_video_id=stream_video).order_by('-start_time').first()
        if last_chunk and last_chunk.start_time < timezone.now() - timedelta(hours=5):
            return True
        return False

    result = ""
    streamer_tasks = StreamerTask.objects.all().filter(upload_bilibili_enabled=True)

    for streamer_task in streamer_tasks:
        sv = StreamVideo.objects.filter(streamer_id=streamer_task).order_by('-start_time').first()
        if sv and record_finished(sv) and sv.bilibili_upload_ready():
            sv.bilibili_status = "started"
            sv.save()
            upload_bilibili.delay(sv.id)
            result += "id"
    return result


@shared_task
def periodic_delete():
    result = ""
    vcs = VideoChunk.objects.all().filter(start_time__lte=timezone.now()-timedelta(days=7), fs_exist=True)
    for vc in vcs:
        if os.path.exists(vc.full_path):
            os.remove(vc.full_path)
            result += vc.full_path
        vc.fs_exist = False
        vc.save()
