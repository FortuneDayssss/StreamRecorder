import requests
import logging
import threading


def download_requests(url, file_name, size_limit=None):
    response = requests.get(
        url=url,
        stream='true',
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
    response = requests.get(
        url=url,
        stream='true',
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }
    )

    if response.status_code != 200:
        logging.debug("error when downloading")
        return None
    else:
        logging.debug("download response status code = 200... download start")


# class TimeSupervisor(threading.Thread):
#     def __init__(self, threadID, period, counter):
#         threading.Thread.__init__(self)
#
#     def run(self):
#
#
#
# def ph():
#     while True:
#         print("hello")

if __name__ == '__main__':

    pass

