import json

from bson import json_util
from fastapi import FastAPI, Request
from rq import Queue

import redis
from db import MongoDB
from utils import get_config, get_logger

# env variable
config = get_config()

# redis
r = redis.Redis(host='redis', port=6379, db=0)
queue = Queue(connection=r)

logger = get_logger()

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    mongoDB = MongoDB(uri=config['MONGO_URI'])
    app.state.mongoDB = mongoDB.database


@app.on_event("shutdown")
async def startup_event():
    pass


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
