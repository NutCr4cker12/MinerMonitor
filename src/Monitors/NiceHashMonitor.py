from threading import Thread, Timer

class NiceHashMonitor(Thread):

    def __init__(self, options, db):
        Thread.__init__(self, name="NiceHash")
        self.db = db

    def run(self):
        pass

    def get_data(self):
        pass

    def post_data(self):
        pass
