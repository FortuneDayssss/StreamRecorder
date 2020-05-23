from bilibiliuploader import VideoPart, BilibiliUploader
import logging
import sys


# 电子竞技tid=171
def upload(username, password, parts, title, tid, tag, description, source, no_reprint, open_elec, copyright):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    b = BilibiliUploader()
    b.login(username, password)
    b.upload(
        copyright=copyright,
        parts=parts,
        title=title,
        tid=tid,
        tag=tag,
        desc=description,
        source=source,
        no_reprint=no_reprint,
        open_elec=open_elec
    )


if __name__ == '__main__':
    vchunk1 = VideoPart(
        path="C:/Users/yisic/PycharmProjects/StreamRecorderSystem/data/video/yyf/957090_1585270502.flv",
        title="p1",
        desc=""
    )
    vchunk2 = VideoPart(
        path="C:/Users/yisic/PycharmProjects/StreamRecorderSystem/data/video/yyf/957090_1585271594.flv",
        title="p2",
        desc=""
    )
    from secret import *
    upload(
        copyright=2,
        username=BILIBILI_USERNAME,
        password=BILIBILI_PASSWORD,
        parts=[vchunk1, vchunk2],
        title="pythons上传测试2",
        tid=171,
        tag=",".join(["测试", "tag2"]),
        description="python upload test",
        source="https://www.douyu.com/120219",
        no_reprint=0,
        open_elec=1
    )
