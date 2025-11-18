import subprocess
import sys
from rich.console import Console
from lib import control
from lib import logger

class Sword:

    def __init__(self):
        self.adb_path = "./tools/adb"
        self.console = Console()
        self.log = logger.Log()
        self.control = control.AdbRunner()

    def run_command(self, command):
        try:
            result = subprocess.run(
                command,                 # command
                shell=True,           # getoutput pake shell=True by default
                capture_output=True,  # biar bisa ambil output
                text=True,            # decode ke string
                timeout=15            # timeout 15 detik
            )
            return result.stdout
        except Exception as e:
            self.log.error(f"Error running command: {e}")
            return False

    def adb(self,status):
        if status == "start":
            self.run_command(f"{self.adb_path} start-server")
            self.log.info("ADB Started")

        if status == "stop":
            self.run_command(f"{self.adb_path} kill-server")
            self.log.info("ADB stopped")

    def connect(self,ip,port=5555):
        self.log.info(f"Connecting to {ip}:{port}")
        conn = self.run_command(f"{self.adb_path} connect {ip}:{port}")
        if "connected" in str(conn).lower():
            self.log.info(f"Connected to {ip}:{port}")
            self.spawn_control()
        else:
            self.log.error(f"Unable to connect to {ip}:{port}")

    
    def spawn_control(self):
        self.log.info("Checking device connection...")
        devices = subprocess.getoutput("adb devices").splitlines()
        if len(devices) < 2 or "device" not in devices[1]:
            self.log.error("No connected device found!")
        else:
            self.log.info("Device connected!")
            self.control.get_device_info()
            self.control.show_menu()

    def run(self,ip):
        self.connect(ip)
        self.adb("stop")

if __name__ == "__main__":
    app = Sword()
    app.run(sys.argv[1])