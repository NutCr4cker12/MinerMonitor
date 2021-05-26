from .MonitorBase import MonitorBase

class NiceHashMonitor(MonitorBase):

    def __init__(self, options, db):
        super().__init__(options, "NiceHash")
        self.db = db

    def run(self):
        pass
