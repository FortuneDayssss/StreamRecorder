from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock, patch
from StreamRecorder.models import StreamerTask, StreamVideo, VideoChunk
from datetime import timedelta


class TestTasks(TestCase):
    @patch('StreamRecorder.tasks.probe_and_download')
    def test_period_record(self, mock_probe_and_download):
        from StreamRecorder.tasks import periodic_record
        st1 = StreamerTask(
            streamer_name='test_streamer1',
            platform='douyu',
            room_id='000001',
            room_url='https://www.douyu.com/000001',
            record_enabled=True,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=False,
            upload_bilibili_video_name='',
            upload_bilibili_info='{}',
            upload_onedrive_enabled=False
        )
        st1.save()
        st2 = StreamerTask(
            streamer_name='test_streamer2',
            platform='douyu',
            room_id='000002',
            room_url='https://www.douyu.com/000002',
            record_enabled=False,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=False,
            upload_bilibili_video_name='',
            upload_bilibili_info='{}',
            upload_onedrive_enabled=False
        )
        st2.save()
        result = periodic_record()
        self.assertEqual(len(StreamerTask.objects.all()), 2)
        self.assertEqual(StreamerTask.objects.get(streamer_name='test_streamer1').record_running, True)
        self.assertEqual(StreamerTask.objects.get(streamer_name='test_streamer2').record_running, False)
        self.assertEqual(mock_probe_and_download.delay.call_count, 1)
        self.assertEqual(result, "test_streamer1,")

    @patch('StreamRecorder.tasks.upload_bilibili')
    def test_period_upload(self, mock_upload_bilibili):
        from StreamRecorder.tasks import periodic_upload
        st1 = StreamerTask(
            id=1,
            streamer_name='test_streamer1',
            platform='douyu',
            room_id='000001',
            room_url='https://www.douyu.com/000001',
            record_enabled=True,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=True,
            upload_bilibili_video_name='',
            upload_bilibili_info='{}',
            upload_onedrive_enabled=False
        )
        st1.save()
        st2 = StreamerTask(
            id=2,
            streamer_name='test_streamer2',
            platform='douyu',
            room_id='000002',
            room_url='https://www.douyu.com/000002',
            record_enabled=False,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=True,
            upload_bilibili_video_name='',
            upload_bilibili_info='{}',
            upload_onedrive_enabled=False
        )
        st2.save()
        sv1 = StreamVideo(
            id=1,
            streamer_id=st1,
            start_time=(timezone.now() - timedelta(hours=6)),
        )
        sv1.save()
        vc1 = VideoChunk(
            stream_video_id=sv1,
            file_name='vc1.flv',
            full_path='/dummy/dir/vc1.flv',
            fs_exist=True,
            start_time=(timezone.now() - timedelta(hours=6))
        )
        vc1.save()
        sv2 = StreamVideo(
            id=2,
            streamer_id=st2,
            start_time=timezone.now(),
        )
        sv2.save()
        vc2 = VideoChunk(
            stream_video_id=sv2,
            file_name='vc2.flv',
            full_path='/dummy/dir/vc2.flv',
            fs_exist=True,
            start_time=timezone.now()
        )
        vc2.save()

        periodic_upload()

        self.assertEqual(StreamVideo.objects.get(id=1).bilibili_status, "started")
        self.assertEqual(StreamVideo.objects.get(id=2).bilibili_status, None)
        self.assertEqual(mock_upload_bilibili.delay.call_count, 1)

    @patch('StreamRecorder.tasks.os.makedirs')
    @patch('StreamRecorder.tasks.RecorderFactory')
    def test_probe_and_download_success_extend_stream_video(self, mock_RecorderFactory, mock_os_makedirs):
        from StreamRecorder.tasks import probe_and_download
        st1 = StreamerTask(
            id=1,
            streamer_name='test_streamer1',
            platform='douyu',
            room_id='000001',
            room_url='https://www.douyu.com/000001',
            record_enabled=True,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=True,
            upload_bilibili_video_name='',
            upload_bilibili_info='{}',
            upload_onedrive_enabled=False
        )
        st1.save()
        sv1 = StreamVideo(
            id=1,
            streamer_id=st1,
            start_time=(timezone.now() - timedelta(hours=1)),
        )
        sv1.save()
        vc1 = VideoChunk(
            id=1,
            stream_video_id=sv1,
            file_name='vc1.flv',
            full_path='/dummy/dir/vc1.flv',
            fs_exist=True,
            start_time=(timezone.now() - timedelta(hours=1))
        )
        vc1.save()
        mock_recorder = MagicMock()
        mock_recorder.probe.return_value = True
        mock_RecorderFactory.return_value = mock_recorder
        probe_and_download(1)

        self.assertEqual(StreamerTask.objects.get(id=1).record_running, False)
        self.assertEqual(len(StreamVideo.objects.all()), 1)
        self.assertEqual(len(VideoChunk.objects.all()), 2)
        self.assertEqual(mock_recorder.probe.call_count, 1)
        self.assertEqual(mock_recorder.download.call_count, 1)
        self.assertEqual(mock_os_makedirs.call_count, 1)

    @patch('StreamRecorder.tasks.os.makedirs')
    @patch('StreamRecorder.tasks.RecorderFactory')
    def test_probe_and_download_success_new_stream_video_by_none_stream_video(self, mock_RecorderFactory, mock_os_makedirs):
        from StreamRecorder.tasks import probe_and_download
        st1 = StreamerTask(
            id=1,
            streamer_name='test_streamer1',
            platform='douyu',
            room_id='000001',
            room_url='https://www.douyu.com/000001',
            record_enabled=True,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=True,
            upload_bilibili_video_name='',
            upload_bilibili_info='{}',
            upload_onedrive_enabled=False
        )
        st1.save()

        mock_recorder = MagicMock()
        mock_recorder.probe.return_value = True
        mock_RecorderFactory.return_value = mock_recorder
        probe_and_download(1)

        self.assertEqual(StreamerTask.objects.get(id=1).record_running, False)
        self.assertEqual(len(StreamVideo.objects.all()), 1)
        self.assertEqual(len(VideoChunk.objects.all()), 1)
        self.assertEqual(mock_recorder.probe.call_count, 1)
        self.assertEqual(mock_recorder.download.call_count, 1)
        self.assertEqual(mock_os_makedirs.call_count, 1)

    @patch('StreamRecorder.tasks.os.makedirs')
    @patch('StreamRecorder.tasks.RecorderFactory')
    def test_probe_and_download_success_new_stream_video_by_empty_expired_stream_video(self, mock_RecorderFactory, mock_os_makedirs):
        from StreamRecorder.tasks import probe_and_download
        st1 = StreamerTask(
            id=1,
            streamer_name='test_streamer1',
            platform='douyu',
            room_id='000001',
            room_url='https://www.douyu.com/000001',
            record_enabled=True,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=True,
            upload_bilibili_video_name='',
            upload_bilibili_info='{}',
            upload_onedrive_enabled=False
        )
        st1.save()
        sv1 = StreamVideo(
            id=1,
            streamer_id=st1,
            start_time=(timezone.now() - timedelta(hours=6)),
        )
        sv1.save()

        mock_recorder = MagicMock()
        mock_recorder.probe.return_value = True
        mock_RecorderFactory.return_value = mock_recorder
        probe_and_download(1)

        self.assertEqual(StreamerTask.objects.get(id=1).record_running, False)
        self.assertEqual(len(StreamVideo.objects.all()), 2)
        self.assertEqual(len(VideoChunk.objects.all()), 1)
        self.assertEqual(mock_recorder.probe.call_count, 1)
        self.assertEqual(mock_recorder.download.call_count, 1)
        self.assertEqual(mock_os_makedirs.call_count, 1)

    @patch('StreamRecorder.tasks.os.makedirs')
    @patch('StreamRecorder.tasks.RecorderFactory')
    def test_probe_and_download_success_new_stream_video_by_expired_last_chunk(self, mock_RecorderFactory, mock_os_makedirs):
        from StreamRecorder.tasks import probe_and_download
        st1 = StreamerTask(
            id=1,
            streamer_name='test_streamer1',
            platform='douyu',
            room_id='000001',
            room_url='https://www.douyu.com/000001',
            record_enabled=True,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=True,
            upload_bilibili_video_name='',
            upload_bilibili_info='{}',
            upload_onedrive_enabled=False
        )
        st1.save()
        sv1 = StreamVideo(
            id=1,
            streamer_id=st1,
            start_time=(timezone.now() - timedelta(hours=1)),
        )
        sv1.save()

        vc1 = VideoChunk(
            id=1,
            stream_video_id=sv1,
            file_name='vc1.flv',
            full_path='/dummy/dir/vc1.flv',
            fs_exist=True,
            start_time=(timezone.now() - timedelta(hours=6))
        )
        vc1.save()

        mock_recorder = MagicMock()
        mock_recorder.probe.return_value = True
        mock_RecorderFactory.return_value = mock_recorder
        probe_and_download(1)

        self.assertEqual(StreamerTask.objects.get(id=1).record_running, False)
        self.assertEqual(len(StreamVideo.objects.all()), 2)
        self.assertEqual(len(VideoChunk.objects.all()), 2)
        self.assertEqual(mock_recorder.probe.call_count, 1)
        self.assertEqual(mock_recorder.download.call_count, 1)
        self.assertEqual(mock_os_makedirs.call_count, 1)

    @patch('StreamRecorder.tasks.os.makedirs')
    @patch('StreamRecorder.tasks.RecorderFactory')
    def test_probe_and_download_fail_not_streaming(self, mock_RecorderFactory, mock_os_makedirs):
        from StreamRecorder.tasks import probe_and_download
        st1 = StreamerTask(
            id=1,
            streamer_name='test_streamer1',
            platform='douyu',
            room_id='000001',
            room_url='https://www.douyu.com/000001',
            record_enabled=True,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=True,
            upload_bilibili_video_name='',
            upload_bilibili_info='{}',
            upload_onedrive_enabled=False
        )
        st1.save()
        sv1 = StreamVideo(
            id=1,
            streamer_id=st1,
            start_time=(timezone.now() - timedelta(hours=1)),
        )
        sv1.save()
        vc1 = VideoChunk(
            id=1,
            stream_video_id=sv1,
            file_name='vc1.flv',
            full_path='/dummy/dir/vc1.flv',
            fs_exist=True,
            start_time=(timezone.now() - timedelta(hours=1))
        )
        vc1.save()
        mock_recorder = MagicMock()
        mock_recorder.probe.return_value = False
        mock_RecorderFactory.return_value = mock_recorder
        probe_and_download(1)

        self.assertEqual(StreamerTask.objects.get(id=1).record_running, False)
        self.assertEqual(len(StreamVideo.objects.all()), 1)
        self.assertEqual(len(VideoChunk.objects.all()), 1)
        self.assertEqual(mock_recorder.probe.call_count, 1)
        self.assertEqual(mock_recorder.download.call_count, 0)
        self.assertEqual(mock_os_makedirs.call_count, 0)

    @patch('StreamRecorder.tasks.upload.bilibili') # uploader
    @patch('StreamRecorder.tasks.os.path.isfile')
    @patch('StreamRecorder.tasks.bilibiliuploader') # lib module
    def test_upload_bilibili(self, mock_lib_bilibiliuploader, mock_isfile, mock_upload_bilibili):
        from StreamRecorder.tasks import upload_bilibili
        st1 = StreamerTask(
            id=1,
            streamer_name='test_streamer1',
            platform='douyu',
            room_id='000001',
            room_url='https://www.douyu.com/000001',
            record_enabled=True,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=True,
            upload_bilibili_video_name='',
            upload_bilibili_info='{ \
              "title": "{date}棋客老师第一视角", \
              "tid": 171, \
              "tag": ["电子竞技", "星际争霸2", "神族", "棋客"], \
              "description": "{date}棋客老师第一视角", \
              "source": "https://www.douyu.com/120219", \
              "no_reprint": true, \
              "open_elec": true \
            }',
            upload_onedrive_enabled=False
        )
        st1.save()
        sv1 = StreamVideo(
            id=1,
            streamer_id=st1,
            start_time=timezone.now().replace(2020, 2, 1, 19, 30, 00),
        )
        sv1.save()
        vc1 = VideoChunk(
            id=1,
            stream_video_id=sv1,
            file_name='vc1.flv',
            full_path='/dummy/dir/vc1.flv',
            fs_exist=True,
            start_time=timezone.now().replace(2020, 2, 1, 19, 30, 00),
        )
        vc1.save()
        vc2 = VideoChunk(
            id=2,
            stream_video_id=sv1,
            file_name='vc2.flv',
            full_path='/dummy/dir/vc2.flv',
            fs_exist=True,
            start_time=timezone.now().replace(2020, 2, 1, 19, 40, 00),
        )
        vc2.save()

        mock_isfile.return_value = True

        upload_bilibili(1)

        self.assertEqual(mock_isfile.call_count, 2)
        self.assertEqual(mock_lib_bilibiliuploader.VideoPart.call_count, 2)
        self.assertEqual(mock_upload_bilibili.upload.call_count, 1)
        upload_args = mock_upload_bilibili.upload.call_args_list[0][1]
        self.assertEqual(upload_args['title'], '2020年2月1日棋客老师第一视角')
        self.assertEqual(StreamVideo.objects.get(id=1).bilibili_status, "finished")

    @patch('StreamRecorder.tasks.os.path.exists')
    @patch('StreamRecorder.tasks.os.remove')
    def test_periodic_delete(self, mock_os_remove, mock_os_path_exists):
        from StreamRecorder.tasks import periodic_delete
        st1 = StreamerTask(
            id=1,
            streamer_name='test_streamer1',
            platform='douyu',
            room_id='000001',
            room_url='https://www.douyu.com/000001',
            record_enabled=True,
            record_running=False,
            record_dir_path='/dummy/dir',
            record_chunk_size_limit='1G',
            upload_bilibili_enabled=True,
            upload_bilibili_video_name='',
            upload_bilibili_info='{ \
                      "title": "{date}棋客老师第一视角", \
                      "tid": 171, \
                      "tag": ["电子竞技", "星际争霸2", "神族", "棋客"], \
                      "description": "{date}棋客老师第一视角", \
                      "source": "https://www.douyu.com/120219", \
                      "no_reprint": true, \
                      "open_elec": true \
                    }',
            upload_onedrive_enabled=False
        )
        st1.save()
        sv1 = StreamVideo(
            id=1,
            streamer_id=st1,
            start_time=timezone.now().replace(2020, 2, 1, 19, 30, 00),
        )
        sv1.save()
        vc1 = VideoChunk(
            id=1,
            stream_video_id=sv1,
            file_name="1.flv",
            full_path="/data/video/dummystreamername/1.flv",
            fs_exist=True,
            start_time=timezone.now() - timedelta(days=14),
        )
        vc1.save()
        vc2 = VideoChunk(
            id=2,
            stream_video_id=sv1,
            file_name="2.flv",
            full_path="/data/video/dummystreamername/2.flv",
            fs_exist=True,
            start_time=timezone.now() - timedelta(days=6),
        )
        vc2.save()
        vc3 = VideoChunk(
            id=3,
            stream_video_id=sv1,
            file_name="3.flv",
            full_path="/data/video/dummystreamername/3.flv",
            fs_exist=True,
            start_time=timezone.now() - timedelta(days=7),
        )
        vc3.save()

        mock_os_path_exists.return_value = True

        periodic_delete()

        vc1 = VideoChunk.objects.all().filter(id=1).first()
        vc2 = VideoChunk.objects.all().filter(id=2).first()
        vc3 = VideoChunk.objects.all().filter(id=3).first()

        self.assertEqual(vc1.fs_exist, False)
        self.assertEqual(vc2.fs_exist, True)
        self.assertEqual(vc3.fs_exist, False)
        self.assertEqual(mock_os_path_exists.call_count, 2)
        self.assertEqual(mock_os_remove.call_count, 2)
