from threading import Timer
from .BinanceMonitor import BinanceMonitor
from .HWinfoMonitor import HWinfoMonitor
from .NiceHashMonitor import NiceHashMonitor

class MonitorManager:

    def __init__(self, options, database):
        self.options = options
        self.db = database
        self.binance = None
        self.hwinfo = None
        self.nh = None

    def start(self):
        if self.options.binance.enabled:
            self.binance = BinanceMonitor(self.options.binance, self.db)
            self.binance.start()

        if self.options.hwinfo.enabled:
            self.hwinfo = HWinfoMonitor(self.options.hwinfo, self.db)
            self.hwinfo.start()

        if self.options.nicehash.enabled:
            self.nh = NiceHashMonitor(self.options.nicehash, self.db)
            self.nh.start()

    def is_alive(self):
        alive = []
        if self.options.binance.enabled and self.binance.is_alive():
            alive.append("Binance")
        if self.options.hwinfo.enabled and self.hwinfo.is_alive():
            alive.append("HWinfo")
        if self.options.nicehash.enabled and self.nh.is_alive():
            alive.append("NiceHash")
        
        if len(alive) > 0:
            print(",".join(alive) + " are still alive")
            return True
            
        return False

    def stop(self):
        if self.options.binance.enabled:
            self.binance.join()

        if self.options.hwinfo.enabled:
            self.hwinfo.join()

        if self.options.nicehash.enabled:
            self.nh.join()