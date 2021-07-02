from Config import Config
from src import (
    Program, HWiNFOEXE, HWiNFORemoteMonitor,        # Programs
    HWinfoMonitor, BinanceMonitor, NiceHashMonitor, # Monitors
    Mongo,                                          # Database    
    GUI, is_admin                                   # Utils and GUI
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

    q = database.queue
    monitors.append(HWinfoMonitor(options.monitors.hwinfo, q))
    monitors.append(BinanceMonitor(options.monitors.binance, database))
    monitors.append(NiceHashMonitor(options.monitors.nicehash, database))

    return monitors

def run_gui(plugins, monitors):
    GUI.start(plugins, monitors)

def clean_up(plugins, monitors):
    for p in plugins:
        for thread in p.timer_threads.values():
            print(f"Stopping {p.name} thread")
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