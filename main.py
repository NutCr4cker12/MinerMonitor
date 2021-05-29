import atexit
import time
from Config import Config
from src import (
    MonitorManager,
    Program,
    GUI,
    run_as_admin
)


def at_exit():
    print("Exiting...")

def run_gui():
    options = Config()

    plugins = []
    plugins.append(Program(options.hwinfoExe))
    plugins.append(Program(options.afterburner))

    GUI.start(plugins)


if __name__ == "__main__":
    atexit.register(at_exit)
    run_gui()
