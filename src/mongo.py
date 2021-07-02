
import datetime
import json
from pymongo import MongoClient
from multiprocessing import Process, Queue

def handle_posts(connection_string: str, queue: Queue):
    print("Starting mongo...")
    client = MongoClient(connection_string)
    db = client["foodpickerdb"]
    print("Mongo started")
    print("Waiting for something to post....")
    
    while True:
        payload = queue.get()

        print("Got payload: ", json.dumps(payload, indent=2))

        source = payload["source"]
        data = payload["data"]
        data["time"] = datetime.datetime.utcnow()

        if source not in ["hwinfo", "binance", "nicehash"]:
            raise Exception(f"Unkwnon source in payload: {str(payload)}")

        collection = db[source]
        collection.insert(data)


class Mongo:

    def __init__(self, options):
        self.connection_string = options.connectionString
        self.queue = Queue()

        self.running = False
        self.proc = None

    def start(self):
        self.running = True
        self.proc = Process(target=handle_posts, args=(self.connection_string, self.queue, ))
        self.proc.start()

    def stop(self):
        print("Stopping mongo...")
        self.proc.terminate()
        self.running = False
        print("Mongo stopped")

    def post(self, payload):
        if not self.running:
            raise Exception("Cannot post data when mongo is not running!")
        self.queue.put(payload)