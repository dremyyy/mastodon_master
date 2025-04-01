from flask import Flask, jsonify, request, send_file
import threading
import os
import json
import time
from mastodon_listener import start_stream_for_instance
from config import Config
from pymongo import MongoClient
from dotenv import load_dotenv

app = Flask(__name__)

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path)

mongo_uri = os.getenv('MONGO_URI')
mongo_db_name = os.getenv('MONGO_DB_B')

# MongoDB client setup
mongo_client = MongoClient(mongo_uri)  # Use for Docker
db = mongo_client[mongo_db_name]


# Function to start streaming for all configured Mastodon instances
def start_streaming_for_all_instances():
    instances_config = Config.get_instance_config()  # Load instances from the .env file
    for instance_config in instances_config:
        stream_thread = threading.Thread(target=start_stream_for_instance, args=(instance_config,), name=instance_config['base_url'])
        stream_thread.daemon = True
        stream_thread.start()


@app.route('/')
def index():
    return "Mastodon Streaming Service is running."


@app.route("/threads", methods=["GET"])
def get_threads():
    threads = threading.enumerate()

    thread_list = []
    for thread in threads:
        thread_info = {
            "name": thread.name,
            "ident": thread.ident,
            "is_alive": thread.is_alive(),
            "daemon": thread.daemon
        }
        thread_list.append(thread_info)

    return jsonify(thread_list), 200

@app.route("/collections", methods=["GET"])
def list_collections():
    try:
        collections = db.list_collection_names()
        return jsonify({"collections": collections}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    start_streaming_for_all_instances()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
