import threading
import time
from datetime import datetime, timedelta

from rq import Queue

import redis
from scheduled_fn import fetchFromApiTODatabase
from utils import get_logger

# redis
r = redis.Redis(host='redis', port=6379, db=0)
queue = Queue(connection=r)

# for threading
stop_fetching_video = False
logger = get_logger()


def start_sending_data(query: str):
    global stop_fetching_video
    start_date_time = datetime.now() - timedelta(hours=4)
    while not stop_fetching_video:
        # execute one job after
        start_date_time = start_date_time + timedelta(hours=1)

        cur_time_string = start_date_time.astimezone().isoformat()
        job = queue.enqueue(fetchFromApiTODatabase, args=(logger, query, cur_time_string))
        logger.info('Added in Queue. Waiting...')

        time.sleep(5)


def main():
    global stop_fetching_video

    logger.info('Thread started')
    youTubeClientThread = threading.Thread(target=start_sending_data, args=('IPL',))
    youTubeClientThread.start()

    time.sleep(300)

    stop_fetching_video = True
    youTubeClientThread.join()

    logger.info('Thread stopped')


main()
