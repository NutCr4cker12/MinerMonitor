from Config import Config
from src import (
    Program,
    HWiNFOEXE,
    GUI,
    is_admin
)


def get_programs(options):
    admin = is_admin()
    plugins = []

    plugins.append(HWiNFOEXE(options.hwinfoExe, admin))
    plugins.append(Program(options.afterburner, admin))
    plugins.append(Program(options.aisuite, admin))
    plugins.append(Program(options.nicehash, admin))
    return plugins

def get_monitors(options):
    return []

def run_gui(plugins, monitors):
    GUI.start(plugins)

def clean_up(plugins, monitors):
    for p in plugins:
        for thread in p.timer_threads.values():
            print(f"Stopping {p.name} thread")
            thread.cancel()

if __name__ == "__main__":
    options = Config(production=False)
    plugins = get_programs(options)
    monitors = get_monitors(options)

    run_gui(plugins, monitors)
    clean_up(plugins, monitors)