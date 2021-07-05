import datetime as dt
import time
from pymongo import DESCENDING
from src import create_client, force_stop
from .Api import create_client as create_api_client

def pre_run(db_options):
    db = create_client(db_options.connectionString)
    collection = db["nicehash"]

    cursor = collection.find().limit(1).sort("created", DESCENDING)
    return list(cursor)[0]

def seconds_till_next_payout(timestamp:  dt) -> float:
    next_assumed_payout = timestamp + dt.timedelta(hours=4)
    now = dt.datetime.utcnow()
    if next_assumed_payout > now:
        time_difference = next_assumed_payout - now
        time_diff_seconds = time_difference.total_seconds() + 5
    else:
        time_diff_seconds = 0.1
    
    return time_diff_seconds

def run_monitor(options, queue, latest_document):
    api = create_api_client(options.api)

    # Fill up the data up to date
    latest_time = latest_document["created"] + dt.timedelta(hours=1)

    # If the monitor is started so that the latest time is already fetced, wait for next assumed payout
    would_sleep = seconds_till_next_payout(latest_time)
    if would_sleep > 1:
        time.sleep(would_sleep)
        if force_stop():
            return
        return run_monitor(options, queue, latest_document)

    payouts_before_this = api.get_payouts(latest_time, dt.datetime.utcnow())

    timestamps = []
    payload = {
        "source": "nicehash",
        "data": []
    }

    # cleanup data
    for payout in payouts_before_this["list"]:
        timestamp = dt.datetime.fromtimestamp(payout["created"] / 1000)
        timestamps.append(timestamp)

        payout["created"] = timestamp
        payout["currency"] = payout["currency"]["description"]
        payout["amount"] = float(payout["amount"])
        payout["feeAmount"] = float(payout["feeAmount"])

        if "accountType" in payout: 
            del payout["accountType"]
        if "metadata" in payout: 
            del payout["metadata"]

        payload["data"].append(payout)

    queue.put(payload)

    new_latest_time = max(timestamps)
    new_latest_document = { "created": new_latest_time }
    sleep_time = seconds_till_next_payout(new_latest_document)
    time.sleep(sleep_time)

    if force_stop():
        return

    run_monitor(options, queue, new_latest_document)