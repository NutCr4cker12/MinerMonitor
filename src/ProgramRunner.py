import subprocess
import time
import os
import pyautogui
import threading
from queue import Queue, Empty
# sys.path.append(os.getcwd())

from src.Utils.windows_utils import get_windows_by_name
from src.Utils.image_utils import get_image_position
from src.Utils.util_funcs import force_stop

def get_single_window(name):
    windows = get_windows_by_name(name)
    if len(windows) == 0:
        return None

    if len(windows) == 1:
        return windows[0]

    shortest_name = 999999
    w = None
    for wind in windows:
        title_len = len(wind.title) - len(name)
        if title_len >= 0 and title_len < shortest_name:
            shortest_name = title_len
            w = wind

    return w


def check_running_process(name):
    processes = subprocess.Popen(['tasklist'], stdout=subprocess.PIPE)
    output, errors = processes.communicate()

    if errors:
        return (False, None)

    pids = []
    for outline in output.splitlines():
        line = str(outline).lower()
        if name.lower() in line:
            try:
                splitted = line.split(".exe")[1].strip().split(" ")[0]
                pid = int(splitted)
                pids.append(pid)
            except Exception:
                pass
                
    return (len(pids) > 0, pids)

class Program:

    def __init__(self, options, is_admin):
        self.name = options.name
        self.cmd = options.cmd
        self.windowTitle = options.windowTitle
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
            pid = self.window.pid()
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
        self.window = get_single_window(self.windowTitle.lower())
        self.running = self.window is not None

        if "hwinfo" in self.name.lower() and self.window is not None:
            pid = self.window.pid()
            print("HWINFOEXE started with pid: ", pid)

        self.answer_callback()
        return self.window

    def answer_callback(self):
        if callable(self.update_callback):
            try:
                self.update_callback()
            except Exception:
                pass

    def _timed_thread(self, timeout: int, func: callable, name: str):
        if name in self.timer_threads:
            self.timer_threads[name].cancel()

        t = threading.Timer(timeout, func)
        t.start()
        self.timer_threads[name] = t

def _enqueue_proc_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line.decode("utf-8"))
    out.close()

class HWiNFORemoteMonitor(Program):

    def __init__(self, options, is_admin):
        super().__init__(options, is_admin)
        self.proc = None
        self.proc_queue = None
        self.proc_read_thread = None
        self.running = False

    def start(self):
        self.stop()

        self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        self.proc_queue = Queue()
        self.proc_read_thread = threading.Thread(target=_enqueue_proc_output, args=(self.proc.stdout, self.proc_queue, ))
        self.proc_read_thread.daemon = True
        self.proc_read_thread.start()

        start = time.time()
        hwinfo_enabled = False
        web_server_running = False
        error_line = ""
        while time.time() - start < 5:
            try:
                line = self.proc_queue.get_nowait()
            except Empty:
                pass
            else:
                if "An error occured" in line:
                    error_line = line
                    break
                if "Web server running" in line:
                    web_server_running = True
                elif "HWiNFO process found! Enabling HWiNFO" in line:
                    hwinfo_enabled = True

                if hwinfo_enabled and web_server_running:
                    break
        
        if hwinfo_enabled and web_server_running:
            print(f"{self.name} started!")
            self.update_status()
            super()._timed_thread(1, self.listen_hwinfo_restart, "listen_hwinfo_restart")
            return
        
        print(f"{self.name} failed to start due to error: {error_line}")
        self.stop()
        time.sleep(5)
        self.start()

    def listen_hwinfo_restart(self):
        while self.proc is not None and self.proc_read_thread is not None and self.proc_queue is not None:
            try:
                line = self.proc_queue.get_nowait()
            except Empty:
                pass
            else:
                if "An error occured" in line:
                    print(f"{self.name} detected error in remote monitor, restarting...")
                    self.stop()
                    time.sleep(5)
                    self.start()
                    return
            time.sleep(2)
        print(f"{self.name} hwinfo restart listener exited without noticing error")
    

    def stop(self):
        if self.proc is None:
            return

        self.proc.terminate()
        self.proc = None

        if self.proc_read_thread is None:
            self.update_status()    
            return

        self.proc_read_thread.join()
        self.proc_read_thread = None
        self.update_status()

    def set_foreground(self):
        self.update_status()

    def update_status(self):
        self.running = self.proc is not None
        super().answer_callback()



class HWiNFOEXE(Program):

    def __init__(self, options, is_admin):
        super().__init__(options, is_admin)
        self._window = None

    def start(self):
        super().start()

        # Wait for the process to start
        self._click_run()

    def wait_for_image(self, image_name : str, wait_time : float):
        # Wait for the process to start
        for _ in range(20):
            x, y = get_image_position(image_name)
            if x is not None and y is not None:
                return (x, y)
            time.sleep(wait_time)

        raise Exception(f"Wasn't able to find image position {image_name}")

    def _click_run(self):
        orig_x, orig_y = pyautogui.position()

        x, y = self.wait_for_image("settings.PNG", 0.5)
        pyautogui.click(x=x, y=y)

        time.sleep(0.5)
        x, y = get_image_position("shared_unchecked.PNG", thershold=0.95)
        is_unchecked = x is not None and y is not None
        if is_unchecked:
            pyautogui.click(x=x, y=y)

        time.sleep(0.5)
        x, y = self.wait_for_image("ok.PNG", 0.1)
        pyautogui.click(x=x, y=y)

        x, y = self.wait_for_image("run.PNG", 0.5)
        pyautogui.click(x=x, y=y)
        
        pyautogui.moveTo(x=orig_x, y=orig_y)

        super()._timed_thread(2, super()._get_window, "get_window")
        super()._timed_thread(11 * 60 * 60, self._restart_program, "restart_program")

    def _restart_program(self):
        if self._dont_restart():
            return

        print(f"Restarting {self.name}")
        self.stop()
        time.sleep(2)
        
        print(f"Starting {self.name}...")
        self.start()

    def stop(self):
        running, pids = check_running_process(self.windowTitle)
        if running:
            for pid in pids:
                print("HWINFO was acutally running with pid: ", pid)
            
            if len(pids) == 1:
                os.kill(pids[0], 9)
                super()._timed_thread(1, self._get_window, "get_window")
        else:
            print("Cant stop HWINFO, didn't find the pid!")

    def _dont_restart(self):
        return force_stop()
    

if __name__ == "__main__":
    name = "msiafterburner"
    found, ps = check_running_process(name)

    print("Tasks:")
    if not found:
        print("No task found!")
    else:
        for p in ps:
            print(p)

    print("---")
    print("Windows:")
    w = get_single_window(name)
    
    if w is None:
        print("No windows found !!!")
    else:
        print(w.title)
        w.set_foreground()