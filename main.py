from Config import Config
from src import MonitorManager

if __name__ == "__main__":
    options = Config()
    manager = MonitorManager(options, "db")

    manager.start()
    print("Managers started")
    manager.stop()
    print("Managers stopped")