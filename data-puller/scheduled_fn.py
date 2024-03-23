from api import get_youtube_client, YouTubeClient


def fetchFromApiTODatabase(logger, query: str, publishedAfter: str, max_results: int = 10):
    logger.info('Video Fetching ...')
    cls: YouTubeClient = get_youtube_client()
    video = cls.search(query, publishedAfter, max_results)
    if not video:
        logger.info('No Video Found...')
    cls.database.push_video_data(video)
