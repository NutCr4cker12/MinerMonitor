import requests
import json
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import time
from threading import Thread, Timer
from .MonitorBase import MonitorBase

def get_price(symbol: str = "BTCEUR", startTime: dt.datetime = dt.datetime.utcnow() - dt.timedelta(hours=1), endTime : dt.datetime = dt.datetime.utcnow(), interval = "1h"):
    url = "https://api.binance.com/api/v3/aggTrades"

    startTime = str(int(startTime.timestamp() * 1000))
    endTime = str(int(endTime.timestamp() * 1000))

    req_params = {
        "symbol": symbol,
        "startTime": startTime,
        "endTime": endTime,
    }

    r = requests.get(url, params = req_params)
    df = pd.DataFrame(json.loads(r.text))
    df["price"] = df["p"].apply(lambda x: float(x))
    return df["price"].mean()
    

class BinanceMonitor(Thread):

    def __init__(self, options, db):
        Thread.__init__(self, name="Binance")
        self.db = db
        self.interval = options.interval * 60
        self._running = True

    def run(self):
        while self._running:
            timer = Timer(self.interval, self.get_data)
            timer.start()
            timer.join()

    def kill(self):
        self._running = False

    def get_data(self):
        print(f"Thread {self.name} : {self.index} \n")

    def post_data(self):
        raise NotImplementedError
