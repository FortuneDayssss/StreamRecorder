from record.base import RecorderBase
import requests
import json
import logging
import util.download
import re
import base64
import urllib.parse
import hashlib
import time


class Huya(RecorderBase):
    def __get_rtmp(self, room_id):

        r = requests.get(
            url="https://www.huya.com/{}".format(room_id),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
            }
        )
        data = r.content.decode("unicode-escape")
        data = data[data.find("var hyPlayerConfig"):data.find("window.TT_LIVE_TIMING")]
        data = data[data.find("{"):data.rfind("};") + 1]

        data = json.loads(data)

        logging.debug("hyPlayerConfig: " + str(data))
        print("hyPlayerConfig: " + str(data))

        ratio = 0
        stream_data = json.loads(base64.b64decode(data['stream']).decode())

        for ratio_info in stream_data["vMultiStreamInfo"]:
            if ratio_info["iBitRate"] > ratio:
                ratio = ratio_info["iBitRate"]

        print(ratio)

        data = stream_data["data"][0]["gameStreamInfoList"]
        game_info_data = data[0]
        logging.debug("gameStreamInfo: " + str(game_info_data))

        url = game_info_data["sFlvUrl"] \
              + "/" + game_info_data["sStreamName"] \
              + ".flv" \
              + "?" + game_info_data["sFlvAntiCode"].replace("&amp;", "&") \
              + "&" + "ratio={}".format(ratio)

        logging.debug("url: " + str(url))
        print(url)
        return url

    def probe(self, room_id):
        response = requests.get("https://www.huya.com/{}".format(room_id))
        room_data = response.text
        if room_data.__contains__("liveStatus-off"):
            return False
        else:
            return True

    def download(self, room_id, file_name, size_limit=None):
        rtmp = self.__get_rtmp(room_id)
        util.download.download_requests(rtmp, file_name, size_limit)


if __name__ == '__main__':
    room_id = "508504"

    hy = Huya()
    is_streaming = hy.probe(room_id)
    if is_streaming:
        print("{} is streaming".format(room_id))
        hy.download(room_id, "D:/huya.flv")
    else:
        print("{} is not streaming".format(room_id))

