import logging
from multiprocessing import Process

class MonitorRunner:

    def __init__(self, options, database, db_options, pre_run: callable, run_monitor: callable):
        self.options = options
        self.name = options.name
        self.database = database
        self.db_options = db_options
        self.queue = database.queue
        self.pre_run = pre_run
        self.run_monitor = run_monitor

        self.running = False
        self.monitor_process = None

    def start(self):
        if self.running:
            logging.info(f"{self.options.name} monitor is already running!")
            return

        pre_run_res = None
        if self.pre_run is not None:
            pre_run_res = self.pre_run(self.db_options)

        self.running = True
        # self.run_monitor(self.options, self.queue, pre_run_res)
        self.monitor_process = Process(target=self.run_monitor, args=(self.options, self.queue, pre_run_res, ))
        self.monitor_process.start()
        logging.info(f"{self.options.name} monitor started.")

    def kill(self):
        if not self.running:
            logging.info(f"{self.options.name} monitor cannot be stop - it isn't running")
            return

        self.running = False
        self.monitor_process.terminate()
        self.monitor_process.join()
        self.monitor_process = None
        logging.info(f"{self.options.name} monitor stopped.")
        