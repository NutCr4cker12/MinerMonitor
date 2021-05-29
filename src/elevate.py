# https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin(function):
    if is_admin():
        # Code of your program here
        function()
    else:
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)

        # Also note that if you converted you python script into an executable file 
        # (using tools like py2exe, cx_freeze, pyinstaller) then you should use sys.argv[1:] 
        # instead of sys.argv in the fourth parameter.
