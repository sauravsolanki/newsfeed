from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MongoDB:

    def __init__(self, uri):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        assert self.check_connection()

        self.database = self.client['newsfeeds']

    def check_connection(self):
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            return True
        except Exception as e:
            print(e)
        return False

    def push_video_data(self, video_data):
        for v in video_data:
            self.database['video'].insert_one(v)
        print('Pushed Data .... ')

