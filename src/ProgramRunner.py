import subprocess

class Program:

    def __init__(self, options):
        self.name = options.name
        self.running = False # TODO add generic program running check for these
        self.cmd = options.cmd
        self.process = None

    def start(self):
        if self.process is not None:
            self.stop()

        self.process = subprocess.Popen(self.cmd)
        self.running = True

    def stop(self):
        if self.process is None:
            print(f"{self.name}: canno't stop whats not running!")
            self.running = False
            return

        self.process.kill()
        self.running = False

    