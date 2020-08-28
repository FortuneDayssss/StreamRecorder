from bilibiliuploader import VideoPart, BilibiliUploader
import logging
import sys


# 电子竞技tid=171
def upload(username, password, parts, title, tid, tag, description, source, no_reprint, open_elec, copyright, cover='', thread_pool_workers=1):
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
        open_elec=open_elec,
        cover=cover,
        thread_pool_workers=thread_pool_workers,
    )
