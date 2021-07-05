import requests
import json
import time
import datetime
from collections import defaultdict
from src import force_stop

def run_monitor(options, queue, _):
    sensors = options.sensors
    gpus = options.GPUS

    data = defaultdict(lambda : [])
    for gpu in gpus:
        data[gpu] = defaultdict(lambda : [])

    # Collect 1 minute avgs
    for _ in range(int(60 / 5)):
        data = get_data(data, sensors, gpus)
        time.sleep(5)

    # Init payload with empty data
    payload = {
        "source": "hwinfo",
        "time": datetime.datetime.utcnow(),
        "data": {}
    }

    # Generate avgs into payload data
    for key, value in data.items():
        if key in gpus:
            payload["data"][key] = {}
            for k, v in data[key].items():
                payload["data"][key][k] = (sum(v) * 1.0) / (len(v) * 1.0)  # TODO possible 0 division, shouldnt happen but...
        else:
            payload["data"][key] = (sum(value) * 1.0) / (len(value) * 1.0)

    queue.put(payload)

    if force_stop():
        return

    run_monitor(options, queue, None)

def get_data(data, sensors, gpus):
    r = requests.get("http://localhost:55555")
    current_sensors = json.loads(r.text)

    for sensor in current_sensors:
        name = sensor["SensorName"]
        sclass = sensor["SensorClass"]

        for s in sensors:
            if s["class"] in sclass and s["name"] == name and ("unit" not in s or s["unit"] == sensor["SensorUnit"]):
                sensor_value = float(sensor["SensorValue"].replace(",", "."))

                was_gpu = False
                for gpu in gpus:
                    if gpu in s["saveAs"]:
                        was_gpu = True
                        save_as = s["saveAs"].split(f"{gpu}_")[1]

                        # Group all fans into one
                        if "Fan" in s["name"]:
                            save_as = save_as[:-1]

                        data[gpu][save_as].append(sensor_value)
                        break
                
                if not was_gpu:
                    data[s["saveAs"]].append(sensor_value)
    return data