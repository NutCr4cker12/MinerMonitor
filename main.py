import logging
from Config import Config
from src import (
    Program, HWiNFOEXE, HWiNFORemoteMonitor,        # Programs
    Mongo,                                          # Database    
    GUI, is_admin                                   # Utils and GUI
)
from src.Monitors import (                          # Monitors
    MonitorRunner,
    run_hwinfo_monitor,
    run_nh_monitor, pre_run_nh,
    run_binance_monitor, pre_run_binance
)

# Init logger, only once!
logging.basicConfig(
    level=logging.INFO,
    format=f"[%(asctime)s][%(name)s][%(levelname)s][%(process)d] - %(message)s",
    datefmt="%d.%m.%y-%H:%M:%S"
)


def get_programs(options):
    admin = is_admin()
    plugins = []

    plugins.append(HWiNFOEXE(options.programs.hwinfoExe, admin))
    plugins.append(HWiNFORemoteMonitor(options.programs.hwinfoRemoteMonitor, admin))
    plugins.append(Program(options.programs.afterburner, admin))
    plugins.append(Program(options.programs.aisuite, admin))
    plugins.append(Program(options.programs.nicehash, admin))
    return plugins

def get_monitors(options, database):
    monitors = []

    monitors.append(MonitorRunner(options.monitors.hwinfo, database, options.mongo, None, run_hwinfo_monitor))
    monitors.append(MonitorRunner(options.monitors.binance, database, options.mongo, pre_run_binance, run_binance_monitor))
    monitors.append(MonitorRunner(options.monitors.nicehash, database, options.mongo, pre_run_nh, run_nh_monitor))

    return monitors

def run_gui(plugins, monitors):
    GUI.start(plugins, monitors)

def clean_up(plugins, monitors):
    for p in plugins:
        for thread in p.timer_threads.values():
            logging.info(f"Stopping {p.name} thread")
            thread.cancel()

    for m in monitors:
        if m.running:
            m.kill()

if __name__ == "__main__":
    options = Config(production=False)

    database = Mongo(options.mongo)
    database.start()

    plugins = get_programs(options)
    monitors = get_monitors(options, database)

    run_gui(plugins, monitors)

    database.stop()
    clean_up(plugins, monitors)