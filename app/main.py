import logging
from datetime import datetime

from dotenv import dotenv_values
from fastapi import FastAPI
from rq import Queue
from rq_scheduler import Scheduler

import redis
from api import YouTubeClient

r = redis.Redis(host='redis', port=6379, db=0)
queue = Queue(connection=r)
scheduler = Scheduler(queue=queue, connection=r)
app = FastAPI()

logger = logging.getLogger(__file__)

config = dotenv_values(".env")


@app.on_event("startup")
async def startup_event():
    # # push one job
    # job = queue.enqueue_in(timedelta(seconds=10), get_youtube_data)
    # registry = ScheduledJobRegistry(queue=queue)
    # logger.info(job in registry)

    youTubeClient = YouTubeClient(config)
    app.state.youTubeClient = youTubeClient
    # push job at interval
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),  # Time for first execution, in UTC timezone
        func=youTubeClient.search,  # Function to be queued
        # args=[],  # Arguments passed into function when executed
        kwargs={"query": 'ipl'},  # Keyword arguments passed into function when executed
        interval=10,  # Time before the function is called again, in seconds
        repeat=5,  # Repeat this number of times (None means repeat forever)
        # meta={'foo': 'bar'}  # Arbitrary pickleable data on the job itself
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/list")
def read_root():
    return {"Hello": "World"}


@app.get("/search")
def read_root(query_string: str):
    return {"Hello": "World"}
