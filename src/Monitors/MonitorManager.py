from .BinanceMonitor import BinanceMonitor
from .HWinfoMonitor import HWinfoMonitor
from .NiceHashMonitor import NiceHashMonitor

class MonitorManager:

    def __init__(self, options, database):
        self.options = options
        self.db = database
        self.binance = BinanceMonitor(options.binance, database, "First")
        self.hwinfo = BinanceMonitor(options.hwinfo, database, "Second")  # TODO, just for testing
        # self.hwinfo = HWinfoMonitor(options.hwinfo, database)
        self.nh = NiceHashMonitor(options.nicehash, database)

    def start(self):
        if self.options.binance.enabled:
            self.binance.start()

        if self.options.hwinfo.enabled:
            self.hwinfo.start()

        if self.options.nicehash.enabled:
            self.nh.start()

    def stop(self):
        self.binance.join()
        self.hwinfo.join()
        return

        if self.options.binance.enabled:
            self.binance.stop()

        if self.options.hwinfo.enabled:
            self.hwinfo.stop()

        if self.options.nicehash.enabled:
            self.nh.stop()