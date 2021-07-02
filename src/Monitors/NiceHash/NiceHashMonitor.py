from threading import Thread

class NiceHashMonitor(Thread):

    def __init__(self, options, db):
        Thread.__init__(self, name="NiceHash")
        self.name = options.name
        self.defaultEnabled = options.defaultEnabled
        self.db = db
        self.running = False

    def run(self):
        pass

    def get_data(self):
        pass

    def post_data(self):
        pass
