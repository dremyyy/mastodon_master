from flask import Flask, jsonify
import threading
import time
from mastodon_listener import start_stream_for_instance
from config import Config

app = Flask(__name__)


# Function to start streaming for all configured Mastodon instances
def start_streaming_for_all_instances():
    instances_config = Config.get_instance_config()  # Load instances from the .env file
    for instance_config in instances_config:
        stream_thread = threading.Thread(target=start_stream_for_instance, args=(instance_config,))
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

if __name__ == "__main__":
    start_streaming_for_all_instances()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
