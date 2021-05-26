from threading import Thread, Timer

class MonitorBase(Thread):

    def __init__(self, options, name: str):
        Thread.__init__(self, name=name or "Thread")
        self.interval = options.interval * 60 if hasattr(options, "interval") else False

    def run(self):
        for i in range(5):
            timer = Timer(self.interval, self.get_data)
            timer.start()
            timer.join()

    def get_data(self):
        raise NotImplementedError

    def post_data(self):
        raise NotImplementedError