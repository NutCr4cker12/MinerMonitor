import logging

def force_stop() -> bool:
    with open("forceStop.txt", "r") as file:
        if "stop" in file.readline():
            logging.info("Stopping restart due to txt file!")
            return True
    return False