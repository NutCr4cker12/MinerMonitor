import requests
import json
import pandas as pd
import datetime as dt
import time
from pymongo import DESCENDING
from src import create_client, force_stop

ASSUMED_WEIGHT = 1
SYMBOL = "BTCEUR"
USED_WEIGHT = 0
PREV_WEIGHT = 0
REQUEST_TIME = 0

def pre_run(db_options):
    db = create_client(db_options.connectionString)
    collection = db["binance"]

    cursor = collection.find({ "symbol": "BTCEUR" }).limit(1).sort("time", DESCENDING)
    return list(cursor)[0]


def get_btc_price(start_time: dt.datetime, end_time : dt.datetime, symbol = "BTCEUR"):
    url = "https://api.binance.com/api/v3/aggTrades"

    start_time = str(int(start_time.timestamp() * 1000))
    end_time = str(int(end_time.timestamp() * 1000))

    req_params = {
        "symbol": symbol,
        "startTime": start_time,
        "endTime": end_time,
    }

    r = requests.get(url, params = req_params)
    return r


def get_price_from_request(request) -> float:
    df = pd.DataFrame(json.loads(request.text))
    df["price"] = df["p"].apply(float)
    return df["price"].mean()

def request_weight(request):
    return int(request.headers["x-mbx-used-weight-1m"])

def get_price(symbol: str = "BTCEUR", startTime: dt.datetime = dt.datetime.utcnow() - dt.timedelta(hours=1), endTime : dt.datetime = dt.datetime.utcnow()):
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
    df["price"] = df["p"].apply(float)
    return df["price"].mean()


def fill_prices_since(start_time: dt, end_time: dt = None):
    if end_time is None:
        end_time = dt.datetime.utcnow()

    next_sleep_time = 0.1
    next_time = start_time
    prices = []

    while next_time < end_time:
        next_time = start_time + dt.timedelta(hours=1)

        if next_time > end_time:
            break

        time.sleep(next_sleep_time)
        next_sleep_time = 0.1
        price_request = get_btc_price(start_time=start_time, end_time=next_time, symbol=SYMBOL)

        if price_request.status_code == 429:
            next_sleep_time = 60 * 60 # 1 hour
            # Cant parse price (??)
            continue

        if request_weight(price_request) > 1000:
            next_sleep_time = 10 # 10 seconds

        price = get_price_from_request(price_request)
        price_dict = { "time": next_time, "price": price, "symbol": SYMBOL }
        prices.append(price_dict)

        start_time = next_time
    
    return prices, next_time

def run_monitor(_, queue, latest_document):
    latest_time = latest_document["time"]

    while True:
        now = dt.datetime.utcnow()
        time_diff = (now - latest_time).total_seconds()

        # Latest price is already posted, wait for the next
        if time_diff < 60 * 60:
            time.sleep(time_diff + 5)
            if force_stop():
                return
        else:
            # Fill up the data up to date
            prices, last_time = fill_prices_since(latest_time)

            payload = {
                "source": "binance",
                "data": prices
            }

            queue.put(payload)
            latest_time = last_time

            # Check force stop every 5 minutes
            # Total sleep time == 1 hour
            for _ in range(12):
                if force_stop():
                    return
                time.sleep(5 * 60)
