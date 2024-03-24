import json
from functools import lru_cache
from typing import Dict

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from db import MongoDB
from utils import get_logger, get_config

logger = get_logger()


class YouTubeClient:
    def __init__(self, config: Dict):
        self.config = config
        self.api_version = 1
        self.youtube = build(config['YOUTUBE_API_SERVICE_NAME'],
                             config['YOUTUBE_API_VERSION'],
                             developerKey=config[f'DEVELOPER_KEY{self.api_version}'])

        self.database = MongoDB(uri=config['MONGO_URI'])

    def rebuild(self):
        self.api_version += 1
        if self.api_version == 6:
            raise NotImplemented('API Key Exhausted')
        self.youtube = build(self.config['YOUTUBE_API_SERVICE_NAME'],
                             self.config['YOUTUBE_API_VERSION'],
                             developerKey=self.config[f'DEVELOPER_KEY{(self.api_version)}'])

    def parse_for_interested_fields(self, search_result):
        return {
            "videoId": search_result['id']['videoId'],
            "channelId": search_result['snippet']['channelId'],
            "title": search_result['snippet']['title'],
            "description": search_result['snippet']['description'],
            "default_thumbnail_url": search_result['snippet']['thumbnails']['default'],
            "publishedAt": search_result['snippet']['publishedAt']
        }

    def __search(self, query: str, publishedAfter: str = None, max_results: int = 100):
        search_response = self.youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results,
            publishedAfter=publishedAfter
        ).execute()

        videos = []
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append(self.parse_for_interested_fields(search_result))

        return videos

    def search(self, query: str, publishedAfter: str = None, max_results: int = 100):
        try:
            return self.__search(query, publishedAfter, max_results)
        except HttpError as e:
            print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
            error_message = json.loads(e.content.decode())
            if 'error' in error_message:
                print(error_message['error']['message'])
                self.rebuild()
        except NotImplemented as e:
            print(e)
        return []


@lru_cache
def get_youtube_client():
    return YouTubeClient(get_config())
