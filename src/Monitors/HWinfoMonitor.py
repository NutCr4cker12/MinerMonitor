import requests
import json
import subprocess
import time
from collections import defaultdict
from threading import Thread, Timer

class HWinfoMonitor(Thread):

    def __init__(self, options, db):
        Thread.__init__(self, name="HWinfo", daemon=False)
        self.options = options
        self.db = db
        self.sensors = options.sensors
        self.monitor_process = None
        
    def run(self):
        # TODO Check for existing program first ?
        print("Starting HWinfoMonitor...")
        self.monitor_process = subprocess.Popen(self.options.monitorCmd)
        # TODO Check for if the process has acutally started, started with error etc...

        print("Starting HWinfoMonitor started...")
        for _ in range(2):
            # if not self.monitor_process.poll():
            #     self.monitor_process.kill()
            #     raise Exception("HWinfoMonitor process was exited during running!")
            timer = Timer(self.options.fetchInterval, self.get_data)
            timer.start()
            timer.join()
        self.monitor_process.kill()

    def get_data(self):
        r = requests.get("http://localhost:55555")
        sensors = json.loads(r.text)

        data = {}

        for sensor in sensors:
            name = sensor["SensorName"]
            sclass = sensor["SensorClass"]

            for s in self.sensors:
                if s["class"] in sclass and s["name"] == name:
                    data[s["saveAs"]] = float(sensor["SensorValue"].replace(",", "."))
                    if "GPUPower" in s["saveAs"]:
                        print(json.dumps(sensor, indent=2))

        print(json.dumps(data, indent=2))
        # self.post_data(data)

    def post_data(self, data):
        with open("dummy_data.txt", "a+") as file:
            file.writelines(json.dumps(data, indent=2))
            file.write("At least I'm writing")