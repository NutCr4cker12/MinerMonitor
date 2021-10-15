import logging
import ctypes
import ctypes.wintypes
import numpy as np
import win32gui
import win32ui
import win32con

import sys
if sys.platform != 'win32':
    raise Exception('The _window_win module should only be loaded on a Windows system.')

SetWindowPos = ctypes.windll.user32.SetWindowPos
# Flags for SetWindowPos:
SWP_NOMOVE = ctypes.c_uint(0x0002)
SWP_NOSIZE = ctypes.c_uint(0x0001)

ShowWindow = ctypes.windll.user32.ShowWindow
# Flags for ShowWindow:
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9

SwitchToThisWindow = ctypes.windll.user32.SwitchToThisWindow
SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
CloseWindow = ctypes.windll.user32.CloseWindow
GetWindowRect = ctypes.windll.user32.GetWindowRect
GetClientRect = ctypes.windll.user32.GetClientRect
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible


class _Rect(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long)]


class Window(object):

    def __init__(self, hwnd):
        self._hwnd = hwnd         # Window handle
        self.scrape_method = "windows"
        self.title = self.get_title()
        self.pyHwnd = win32gui.FindWindow(None, self.title)

    def set_position(self, x, y, width, height):
        """Set window top-left corner position and size"""
        SetWindowPos(self._hwnd, None, x, y, width, height, ctypes.c_uint(0))

    def move(self, x, y):
        """Move window top-left corner to position"""
        SetWindowPos(self._hwnd, None, x, y, 0, 0, SWP_NOSIZE)

    def resize(self, width, height):
        """Change window size"""
        SetWindowPos(self._hwnd, None, 0, 0, width, height, SWP_NOMOVE)

    def isVisible(self):
        return IsWindowVisible(self._hwnd)

    def maximize(self):
        ShowWindow(self._hwnd, SW_MAXIMIZE)

    def set_foreground(self):
        SetForegroundWindow(self._hwnd)

    def minimize(self):
        ShowWindow(self._hwnd, SW_MINIMIZE)

    def restore(self):
        ShowWindow(self._hwnd, SW_RESTORE)

    def close(self):
        CloseWindow(self._hwnd)

    def get_hwnd(self):
        return self._hwnd

    def pid(self):
        pid = ctypes.c_ulong()
        res = GetWindowThreadProcessId(self._hwnd, ctypes.byref(pid))
        if isinstance(res, int):
            return res
        return res.value

    def get_title(self):
        length = GetWindowTextLength(self._hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(self._hwnd, buff, length + 1)
        return buff.value

    def get_position(self, include_title=True):
        """Returns tuple of 4 numbers: (x, y)s of top-left and bottom-right corners"""
        rect = _Rect()
        if include_title:
            GetWindowRect(self._hwnd, ctypes.pointer(rect))
        else:
            GetClientRect(self._hwnd, ctypes.pointer(rect))
        return rect.left, rect.top, rect.right, rect.bottom

    # def get_img_mss(self, include_titlebar):
    #     # TODO implement titlebar exclusing
    #     win32gui.SetForegroundWindow(self.pyHwnd)
    #     bbox = win32gui.GetWindowRect(self.pyHwnd)
    #     # logging.info(bbox)
    #     region = {"top": bbox[0], "left": bbox[1], "width": bbox[2], "height": bbox[3]}
    #     img = np.array(mss.mss().grab(region))
    #     return np.array(img)

    def grab_img(self, include_titlebar=False):
        if self.scrape_method == "windows":
            return self.get_img_fromBitmap(include_titlebar)
        # return self.get_img_mss(include_titlebar)

    def get_img_fromBitmap(self, include_titlebar):
        hwin = self.pyHwnd

        left, top, x2, y2 = self.get_position(include_titlebar)
        width = x2 - left + 1
        height = y2 - top + 1

        hwindc = win32gui.GetWindowDC(hwin)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, width, height)
        memdc.SelectObject(bmp)

        y_start = 0
        if not include_titlebar:
            _, y_1, _, y_2 = self.get_position()
            real_height = y_2 - y_1
            y_start = real_height - height

        memdc.BitBlt((0, 0), (width, height), srcdc, (0, y_start), win32con.SRCCOPY)

        signedIntsArray = bmp.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')

        try:
            img.shape = (height, width, 4)
        except Exception:
            self.scrape_method = 'screenshot'
            return self.get_img_mss(include_titlebar)
        finally:
            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(hwin, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())

        return img


def get_all_windows():  # https://sjohannes.wordpress.com/2012/03/23/win32-python-getting-all-window-titles/
    """Return dict: {'window title' : window handle} for all visible windows"""
    titles = {}

    def foreach_window(hwnd, lparam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            titles[buff.value] = hwnd
        return True
    EnumWindows(EnumWindowsProc(foreach_window), 0)

    return titles


def get_windows():
    """Return array: dict: {"title": title, "hwnd": window handle} for all visible windows
    """
    winds = []

    def foreach_window(hwnd, lparam):
        if IsWindowVisible(hwnd):
            try:
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                winds.append({"title": buff.value, "hwnd": hwnd})
            except Exception as e:
                logging.error(f"Eception in get_windows: {e}", exc_info=True)
        return True
    EnumWindows(EnumWindowsProc(foreach_window), 0)

    return winds


def get_windows_by_name(name):
    """Finds visible windowses and return \n
    array of Window objects

    Arguments:
        name {String} -- Name to matched, doesn't need to be exact
    """
    winds = []
    for window in get_windows():
        try:
            if name in window["title"].lower():
                winds.append(Window(window["hwnd"]))
        except Exception as e:
            logging.error(f"Exception in getting windows by name: {e}", exc_info=True)
    return winds

# UNUSED !
def get_window_by_pid(pid):
    """Finds visible windowses and return \n
    array of Window objects

    Arguments:
        name {String} -- Name to matched, doesn't need to be exact
    """
    winds = []
    for window in get_windows():
        try:
            w = Window(window["hwnd"])
            if w.pid() == pid:
                winds.append(w)
        except Exception as e:
            logging.error(f"Exception in getting windows by pid: {e}", exc_info=True)
    return winds


if __name__ == "__main__":
    titles = get_windows_by_name("hwinfo64")
    for k in titles:
        logging.info(f"{k.title}, {k.pid()}")
