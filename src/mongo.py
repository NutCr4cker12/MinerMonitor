
from pymongo import MongoClient
from multiprocessing import Process, Queue

def create_client(conn_string : str):
    client = MongoClient(conn_string)
    db = client["foodpickerdb"]
    return db

def handle_posts(connection_string : str, queue: Queue):
    print("Starting mongo...")
    db = create_client(connection_string)
    print("Mongo started")
    print("Waiting for something to post....")
    
    while True:
        payload = queue.get()

        # print("Got payload: ", json.dumps(payload, indent=2))

        source = payload["source"]
        data = payload["data"]

        if source not in ["hwinfo", "binance", "nicehash"]:
            raise Exception(f"Unkwnon source in payload: {str(payload)}")

        collection = db[source]
        if isinstance(data, dict):
            collection.insert(data)
        elif isinstance(data, list):
            collection.insert_many(data)
        else:
            raise Exception(f"Unkwnon data format in payload: {str(data)}")


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