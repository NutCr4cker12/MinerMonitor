import requests
import json
import time
import multiprocessing as mp

def run_monitor(sensors, database):
    i = 0
    while i < 10:
        data = get_data(sensors)
        payload = {
            "source": "hwinfo",
            "data": data
        }
        database.put(payload)
        # print(json.dumps(data, indent=2))
        
        i += 1
        time.sleep(10)

def get_data(sensors):
    r = requests.get("http://localhost:55555")
    current_sensors = json.loads(r.text)

    data = {}

    for sensor in current_sensors:
        name = sensor["SensorName"]
        sclass = sensor["SensorClass"]

        for s in sensors:
            if s["class"] in sclass and s["name"] == name:
                data[s["saveAs"]] = float(sensor["SensorValue"].replace(",", "."))
                # if "GPUPower" in s["saveAs"]:
                #     print(json.dumps(sensor, indent=2))
    return data

class HWinfoMonitor():

    def __init__(self, options, db):
        self.options = options
        self.db = db
        self.name = options.name
        self.defaultEnabled = options.defaultEnabled
        self.sensors = options.sensors
        self.running = False

        self.monitor_process = None

        # self.hwinfo_program = hwinfo_program
        # self.hwinfo_remote_monitor = hwinfo_remote_monitor

        # self.monitor_process = None
        # self.process_run_time = None
        # self._window = None
        
    def start(self):
        self.running = True
        self.monitor_process = mp.Process(target=run_monitor, args=(self.sensors, self.db, ))
        self.monitor_process.start()
        
    def kill(self):
        self.running = False
        self.monitor_process.terminate()
        print("Stop event set, joining...")
        self.monitor_process.join()
        print("Joined")
        self.monitor_process = None

    def post_data(self, data):
        with open("dummy_data.txt", "a+") as file:
            file.writelines(json.dumps(data, indent=2))
            file.write("At least I'm writing")