import subprocess
import time
import os
import pyautogui
import threading

from src.Utils.windows_utils import get_windows_by_name
from src.Utils.image_utils import get_image_position

def get_single_window(name):
    windows = get_windows_by_name(name)
    if len(windows) == 0:
        return None
    return windows[0]

def check_running_process(name):
    processes = subprocess.Popen(['tasklist'], stdout=subprocess.PIPE)
    output, errors = processes.communicate()

    if errors:
        return (False, None)

    for outline in output.splitlines():
        line = str(outline).lower()
        if name.lower() in line:
            try:
                splitted = line.split(".exe")[1].strip().split(" ")[0]
                pid = int(splitted)
                return (True, pid)
            except Exception:
                pass
                
    return (False, None)

class Program:

    def __init__(self, options, is_admin):
        self.name = options.name
        self.cmd = options.cmd
        self.procName = options.processName
        self.runAsAdmin = options.runAsAdmin
        self.update_callback = None
        self.timer_threads = {}

        self.is_admin = is_admin
        self.window = self._get_window()

    def start(self):
        if self.window is not None:
            self.stop()

        cmd = f"powershell.exe -command start-process {self.cmd} -Verb runAs" if self.runAsAdmin and not self.is_admin else self.cmd
        subprocess.Popen(cmd)
        self._timed_thread(1, self._get_window, "get_window")

    def stop(self):
        if self._get_window() is not None:
            _, pid = check_running_process(self.name.lower().replace(".exe", ""))
            os.kill(pid, 9)
            self._timed_thread(1, self._get_window, "get_window")
            return

        print(f"{self.name}: canno't stop whats not running!")

    def set_foreground(self):
        if self._get_window() is None:
            print(f"Cannot set {self.name} foreground - there's no window!")
            return
        self.window.set_foreground()

    def update_status(self):
        self._get_window()

    def _get_window(self):
        self.window = get_single_window(self.name.lower().replace(".exe", ""))
        self.running = self.window is not None
        if callable(self.update_callback):
            try:
                self.update_callback()
            except Exception:
                pass

        return self.window

    def _timed_thread(self, timeout: int, func: callable, name: str):
        if name in self.timer_threads:
            self.timer_threads[name].cancel()

        t = threading.Timer(timeout, func)
        t.start()
        self.timer_threads[name] = t


class HWiNFOEXE(Program):

    def __init__(self, options, is_admin):
        super().__init__(options, is_admin)
        self._window = None

    def start(self):
        super().start()

        # Wait for the process to start
        for _ in range(20):
            x, y = get_image_position("run.PNG")
            if x is not None and y is not None:
                self._click_run(x, y)
                return
            time.sleep(0.5)
        
        raise Exception("Wasn't able to find image position")

    def _click_run(self, x, y):
        orig_x, orig_y = pyautogui.position()
        pyautogui.click(x=x, y=y)
        pyautogui.moveTo(x=orig_x, y=orig_y)

        super()._timed_thread(2, super()._get_window, "get_window")
        super()._timed_thread(11 * 60 * 60, self._restart_program, "restart_program")

    def _restart_program(self):
        if self._dont_restart():
            return

        print(f"Restarting {self.name}")
        super().stop()
        time.sleep(2)
        
        print(f"Starting {self.name}...")
        self.start()

    def _dont_restart(self):
        with open("stopTestRun.txt", "r") as file:
            if "stop" in file.readline():
                print("Stopping restart due to txt file!")
                return True
        return False
    