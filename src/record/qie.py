import requests
import re
import util.download
from record.base import RecorderBase


class QieEGame(RecorderBase):
    def probe(self, room_id):
        room_url = 'https://share.egame.qq.com/cgi-bin/pgg_async_fcgi'
        post_data = {
            'param': '''{"0":{"module":"pgg_live_read_svr","method":"get_live_and_profile_info","param":{"anchor_id":''' + str(
                room_id) + ''',"layout_id":"hot","index":1,"other_uid":0}}}'''
        }
        try:
            response = requests.post(url=room_url, data=post_data).json()
            data = response.get('data', 0)
            if data:
                video_info = data.get('0').get(
                    'retBody').get('data').get('video_info')
                pid = video_info.get('pid', 0)
                if pid:
                    is_live = data.get('0').get(
                        'retBody').get('data').get('profile_info').get('is_live', 0)
                    if is_live:
                        play_url = video_info.get('stream_infos')[
                            0].get('play_url')
                        real_url = re.findall(r'([\w\W]+?)&uid=', play_url)[0]
                    else:
                        return False
                else:
                    return False
            else:
                return False
        except:
            return False
        return True

    def download(self, room_id, file_name, size_limit=None):
        room_url = 'https://share.egame.qq.com/cgi-bin/pgg_async_fcgi'
        post_data = {
            'param': '''{"0":{"module":"pgg_live_read_svr","method":"get_live_and_profile_info","param":{"anchor_id":''' + str(
                room_id) + ''',"layout_id":"hot","index":1,"other_uid":0}}}'''
        }
        try:
            response = requests.post(url=room_url, data=post_data).json()
            data = response.get('data', 0)
            if data:
                video_info = data.get('0').get(
                    'retBody').get('data').get('video_info')
                pid = video_info.get('pid', 0)
                if pid:
                    is_live = data.get('0').get(
                        'retBody').get('data').get('profile_info').get('is_live', 0)
                    if is_live:
                        play_url = video_info.get('stream_infos')[
                            0].get('play_url')
                        real_url = re.findall(r'([\w\W]+?)&uid=', play_url)[0]
                    else:
                        real_url = '直播间未开播'
                else:
                    real_url = '直播间未启用'
            else:
                real_url = '直播间不存在'
        except:
            real_url = '数据请求错误'


        util.download.download_requests_supervised(real_url, file_name, size_limit)


if __name__ == '__main__':
    q = QieEGame()
    print(q.probe("403580700"))