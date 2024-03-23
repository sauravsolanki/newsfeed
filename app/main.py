import json
import threading
import time
from datetime import datetime, timedelta

from bson import json_util
from fastapi import FastAPI, Request
from rq import Queue
from rq_scheduler import Scheduler

import redis
from api import YouTubeClient, get_youtube_client
from db import MongoDB
from utils import get_config, get_logger

# env variable
config = get_config()

# redis
r = redis.Redis(host='redis', port=6379, db=0)
queue = Queue(connection=r)
scheduler = Scheduler(queue=queue, connection=r)

logger = get_logger()

app = FastAPI()

# for threading
stop_fetching_video = False


def fetchFromApiTODatabase(query: str, publishedAfter: str, max_results: int = 10):
    logger.info('Video Fetching ...')
    cls: YouTubeClient = get_youtube_client()
    video = cls.search(query, publishedAfter, max_results)
    if not video:
        print('No Video Found...')
    cls.database.push_video_data(video)


def start_sending_data(query: str):
    global stop_fetching_video
    start_date_time = datetime.now() - timedelta(days=1)
    while not stop_fetching_video:
        # execute one job after
        start_date_time = start_date_time + timedelta(hours=4)

        cur_time_string = start_date_time.astimezone().isoformat()
        # job = queue.enqueue(fetchFromApiTODatabase, args=(query, cur_time_string))
        time.sleep(10)


@app.on_event("startup")
async def startup_event():
    youTubeClient = YouTubeClient(config)
    mongoDB = MongoDB(uri=config['MONGO_URI'])

    app.state.youTubeClient = youTubeClient
    app.state.mongoDB = mongoDB.database

    app.state.youTubeClientThread = threading.Thread(target=start_sending_data, args=('IPL',))
    app.state.youTubeClientThread.start()
    logger.info('Thread started')


@app.on_event("shutdown")
async def startup_event():
    global stop_fetching_video
    stop_fetching_video = True
    app.state.youTubeClientThread.join()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/list")
def read_root(request: Request, page: int, page_limit: int):
    # Fetching books data and paginating
    fetch_books = request.app.state.mongoDB['video'].find().sort('_id', -1).skip(page_limit * (page - 1)).limit(
        page_limit)

    books_fetched = list(json.loads(json_util.dumps(fetch_books)))

    data = {'page': page,
            'showing': page_limit,
            'books': books_fetched}

    return data


@app.get("/search")
def search_video(request: Request, title: str, description: str = '', page: int = 1, page_limit: int = 10):
    search_criteria = {
        "title": {'$regex': f'{title}', '$options': 'i'},
    }
    if description:
        search_criteria["description"] = {'$regex': f'{description}', '$options': 'i'}

    fetch_books = request.app.state.mongoDB['video'].find(search_criteria).sort('_id', -1).skip(
        page_limit * (page - 1)).limit(
        page_limit)

    books_fetched = list(json.loads(json_util.dumps(fetch_books)))

    data = {'page': page,
            'showing': page_limit,
            'books': books_fetched}

    return data
