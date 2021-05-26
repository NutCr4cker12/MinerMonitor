from .MonitorBase import MonitorBase

class HWinfoMonitor(MonitorBase):

    def __init__(self, options, db):
        super().__init__(options, "HWinfo")
        self.db = db
        
    def run(self):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError

    def post_data(self):
        raise NotImplementedError