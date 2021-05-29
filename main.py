import atexit
import time
from Config import Config
from src import MonitorManager, run_as_admin

def at_exit():
    print("Exiting...")

def main():
    options = Config()
    manager = MonitorManager(options, "db")

    manager.start()
    print("Managers started.")
    print("")
    # for i in range(10):
    #     print("\t ___Manager joining in ", 10 - i)
    #     time.sleep(1)
    print("Managers stopped")
    manager.stop()

if __name__ == "__main__":
    atexit.register(at_exit)
    run_as_admin(main)