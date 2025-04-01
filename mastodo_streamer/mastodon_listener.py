from mastodon import Mastodon, StreamListener
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from config import Config
import json


class MastodonListener(StreamListener):
    def __init__(self, collection_name):

        #dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
        #load_dotenv(dotenv_path)

        mongo_uri = os.getenv('MONGO_URI')
        mongo_db_name = os.getenv('MONGO_DB_B')

        client = MongoClient(mongo_uri)    #USE FOR DOCKER
        db = client[mongo_db_name]
        self.collection = db[collection_name]  # Each instance has its own collection


    def on_update(self, status):
        status_data = {
            'id': status.id,
            'created_at': status.created_at.isoformat(),
            'username': None,
            'user_id': status.account.id,
            'user_bot': status.account.bot,
            'visibility': status.visibility,
            'language': status.language
        }

        # Insert the status data into MongoDB
        self.collection.insert_one(status_data)

        print(f"Saved update to MongoDB collection {self.collection.name}: {status_data}")


def start_stream_for_instance(instance_config):
    mastodon = Mastodon(
        access_token=instance_config["access_token"],
        api_base_url=instance_config["base_url"]
    )
    listener = MastodonListener(instance_config["collection_name"])

    while True:
        try:
            mastodon.stream_public(listener, local=True)
        except Exception as e:
            print(f"Error in streaming for {instance_config['base_url']}: {e}")

