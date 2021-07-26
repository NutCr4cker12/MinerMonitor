import requests
import json
import time
import datetime
from collections import defaultdict
from src import force_stop

def run_monitor(options, queue, _):
    sensors = options.sensors
    gpus = options.GPUS

    while not force_stop():
        
        data = defaultdict(lambda : [])
        for gpu in gpus:
            data[gpu] = defaultdict(lambda : [])

        # Collect 1 minute avgs
        for _ in range(6):
            data = get_data(data, sensors, gpus)
            time.sleep(10)

        # Init payload with empty data
        payload = {
            "source": "hwinfo",
            "data": {
                "time": datetime.datetime.utcnow()
            }
        }

        # Generate avgs into payload data
        has_data = False
        for key, value in data.items():
            if key in gpus:
                payload["data"][key] = {}
                for k, v in data[key].items():
                    if len(v) > 0:
                        payload["data"][key][k] = (sum(v) * 1.0) / (len(v) * 1.0)
                        has_data = True
            else:
                if len(value) > 0:
                    payload["data"][key] = (sum(value) * 1.0) / (len(value) * 1.0)
                    has_data = True

        if has_data:
            queue.put(payload)

def get_data(data, sensors, gpus):
    try:
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
    except Exception as e:
        print("Exception in HWINFO monitoring: ", e)
    return data