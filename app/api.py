from typing import Dict

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeClient:
    def __init__(self, config: Dict):
        self.youtube = build(config['YOUTUBE_API_SERVICE_NAME'],
                             config['YOUTUBE_API_VERSION'],
                             developerKey=config['DEVELOPER_KEY'])

    def parse_for_interested_fields(self, search_result):
        return {
            "videoId": search_result['id']['videoId'],
            "channelId": search_result['snippet']['channelId'],
            "title": search_result['snippet']['title'],
            "description": search_result['snippet']['description'],
            "default_thumbnail_url": search_result['snippet']['thumbnails']['default'],
            "publishedAt": search_result['snippet']['publishedAt']
        }

    def __search(self, query: str, max_results: int = 100):
        search_response = self.youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results
        ).execute()

        videos = []
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append(self.parse_for_interested_fields(search_result))

        return videos

    def search(self, query: str, max_results: int = 100):
        try:
            return self.__search(query, max_results)
        except HttpError as e:
            print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
        return []


def get_youtube_data():
    print('get_youtube_data called')
