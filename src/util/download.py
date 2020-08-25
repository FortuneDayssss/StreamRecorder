import requests
import logging
import threading
from datetime import datetime
from time import sleep


def download_requests(url, file_name, size_limit=None):
    response = requests.get(
        url=url,
        stream=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }
    )

    if response.status_code != 200:
        logging.debug("error when downloading")
        return None
    else:
        logging.debug("download response status code = 200... download start")

    with open(file_name, 'wb+') as f:
        size_counter = 0
        for i, chunk in enumerate(response.iter_content(chunk_size=1024 * 1024)):  # 1M chunk
            if chunk:
                f.write(chunk)
                size_counter += len(chunk)
                f.flush()
                if i % 100 == 0:
                    logging.info("stream download: {}B".format(size_counter))
                if size_limit is not None and size_counter > size_limit:
                    logging.info("file size reached {} Byte, stop record".format(size_limit))
                    f.close()
                    response.close()
                    break
            else:
                logging.info("download finished")


def download_requests_supervised(url, file_name, size_limit=None):
    last_chunk_timestamp = datetime.now().timestamp()
    download_finished = False
    response = None

    def download(url, file_name, size_limit=None):
        nonlocal last_chunk_timestamp, download_finished, response
        try:
            response = requests.get(
                url=url,
                stream=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
                }
            )

            if response.status_code != 200:
                logging.debug("error when downloading")
                return None
            else:
                logging.debug("download response status code = 200... download start")

            with open(file_name, 'wb+') as f:
                size_counter = 0
                for i, chunk in enumerate(response.iter_content(chunk_size=1024 * 1024)):  # 1M chunk
                    last_chunk_timestamp = datetime.now().timestamp()
                    if chunk:
                        f.write(chunk)
                        size_counter += len(chunk)
                        f.flush()
                        if i % 100 == 0:
                            logging.info("stream download: {}B".format(size_counter))
                        if size_limit is not None and size_counter > size_limit:
                            logging.info("file size reached {} Byte, stop record".format(size_limit))
                            f.close()
                            response.close()
                            break
                    else:
                        logging.info("download finished")
                        break
        finally:
            download_finished = True

    download_thread = threading.Thread(
        target=download,
        args=(url, file_name, size_limit)
    )

    download_thread.setDaemon(True)
    download_thread.start()

    while not download_finished:
        current_stamp = datetime.now().timestamp()
        if current_stamp - last_chunk_timestamp > 60:
            logging.info("download is blocked, stop download...")
            response.close()
            break
        sleep(10)


if __name__ == '__main__':
    download_requests_supervised(None, None)


