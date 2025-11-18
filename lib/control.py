import os
import subprocess
import time
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

try:
    from lib import logger as user_logger
    def get_logger():
        return user_logger.Log()
except Exception:
    console = Console()
    class _FallbackLogger:
        def info(self, m): console.print(f"[cyan][INFO][/cyan] {m}")
        def error(self, m): console.print(f"[red][ERROR][/red] {m}")
        def warn(self, m): console.print(f"[yellow][WARN][/yellow] {m}")
    def get_logger():
        return _FallbackLogger()


class AdbRunner:
    def __init__(self, adb_path: str = "./tools/adb", timeout: Optional[int] = 20):
        self.scrcpy_path = "./tools/scrcpy"
        self.adb_path = adb_path
        self.timeout = timeout
        self.log = get_logger()
        self.console = Console()

        if not os.path.exists(self.adb_path):
            self.log.warn(f"ADB binary not found at '{self.adb_path}'. Falling back to 'adb' in PATH.")
            self.adb_path = "adb"

    def run_command(self, command: str, timeout: Optional[int] = None, install=False) -> Optional[str]:
        timeout = timeout or self.timeout
        if install:
            cmd_list = [self.adb_path, "install", command]
        else:
            cmd_list = [self.adb_path, "shell", command]
        try:
            completed = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            stdout = (completed.stdout or "").strip()
            stderr = (completed.stderr or "").strip()

            if completed.returncode != 0:
                self.log.error(f"Command failed: {stderr or stdout}")
                return None
            return stdout
        except Exception as e:
            self.log.error(f"Error running command: {e}")
            return None

    # ---------- ADB COMMANDS ----------
    def back(self): self.run_command("input keyevent KEYCODE_BACK")
    def home(self): self.run_command("input keyevent KEYCODE_HOME")
    def menu(self): self.run_command("input keyevent 82")
    def volume_up(self): self.run_command("input keyevent 24")
    def volume_down(self): self.run_command("input keyevent 25")
    def open_settings(self): self.run_command("am start -a android.settings.SETTINGS")

    def install(self):
        apk = Prompt.ask("[bold cyan]APK Path[/bold cyan]", default="lib/evilscreen.apk")
        self.run_command(f'{apk}', install=True)

    def open_url(self):
        url = Prompt.ask("[bold cyan]Enter URL to open[/bold cyan]", default="https://google.com")
        self.run_command(f'am start -a android.intent.action.VIEW -d "{url}"')

    def clear_logcat(self):
        self.console.print("[bold cyan]Clearing logcat...[/bold cyan]")
        subprocess.getoutput(f"{self.adb_path} logcat -c")

    def screenshot(self):
        self.console.print("[bold cyan]Taking screenshot...[/bold cyan]")
        self.run_command("screencap -p /sdcard/screenshot.png")
        subprocess.run([self.adb_path, "pull", "/sdcard/screenshot.png", "./screenshot.png"])
        self.console.print("[green]Screenshot saved as ./screenshot.png[/green]")

    def get_imei(self):
        self.console.print("[bold cyan]Getting IMEI...[/bold cyan]")
        imei = self.run_command("dumpsys iphonesubinfo | grep 'Device ID'")
        self.console.print(f"[green]{imei or 'Unknown'}[/green]")

    def set_battery_level(self):
        level = Prompt.ask("[bold cyan]Enter battery level (0–100)[/bold cyan]", default="100")
        self.run_command(f"dumpsys battery set level {level}")
        self.console.print(f"[green]Battery level set to {level}%[/green]")

    def set_battery_status(self):
        status = Prompt.ask("[bold cyan]Enter status (1=unknown, 2=charging, 3=discharging, 4=not charging, 5=full)[/bold cyan]", default="2")
        self.run_command(f"dumpsys battery set status {status}")
        self.console.print(f"[green]Battery status set to {status}[/green]")

    def reset_battery(self):
        self.console.print("[bold cyan]Resetting battery stats...[/bold cyan]")
        self.run_command("dumpsys battery reset")
        self.console.print("[green]Battery reset done.[/green]")

    def mirror(self):
        self.log.info("Starting scrcpy for mirroring...")
        os.system(f"xterm -e {self.scrcpy_path} &")

    # ---------- DEVICE INFO ----------
    def get_device_info(self):
        info = {
            "Serial": self.run_command("getprop ro.serialno"),
            "Model": self.run_command("getprop ro.product.model"),
            "Brand": self.run_command("getprop ro.product.brand"),
            "Android": self.run_command("getprop ro.build.version.release"),
            "Device": self.run_command("getprop ro.product.device"),
        }

        self.console.print("\n[bold bright_white]------------- Device Info -------------[/bold bright_white]")
        for k, v in info.items():
            self.console.print(f"[cyan]{k:<9}[/cyan]: [white]{v or '-'}[/white]")
        self.console.print("[bold bright_white]---------------------------------------[/bold bright_white]\n")

        return info

    # ---------- MENU ----------
    def show_menu(self):
        menu = {
            "1": ("Back", self.back),
            "2": ("Home", self.home),
            "3": ("Menu", self.menu),
            "4": ("Open URL", self.open_url),
            "5": ("Open Settings", self.open_settings),
            "6": ("Volume Up", self.volume_up),
            "7": ("Volume Down", self.volume_down),
            "8": ("Install APK", self.install),
            "9": ("Clear Logcat", self.clear_logcat),
            "10": ("Screenshot", self.screenshot),
            "11": ("Get IMEI", self.get_imei),
            "12": ("Set Battery Level", self.set_battery_level),
            "13": ("Set Battery Status", self.set_battery_status),
            "14": ("Reset Battery", self.reset_battery),
            "15": ("Mirroring Device",self.mirror),
            "0": ("Exit", None)
        }

        while True:
            self.console.print("[bold magenta]ADB Menu Options[/bold magenta] (Type linux command to run custom command like 'whoami')\n")

            # tampil dua kolom biar rapih
            items = list(menu.items())
            mid = len(items) // 2
            for i in range(mid):
                left = items[i]
                right = items[i + mid] if i + mid < len(items) else None

                left_txt = f"[bold green][{left[0]}][/bold green] {left[1][0]:<25}"
                right_txt = f"[bold green][{right[0]}][/bold green] {right[1][0]}" if right else ""
                self.console.print(left_txt + " " * 3 + right_txt)

            choice = self.console.input("\n[bold yellow]Select menu (type 0 for exit) >> [/bold yellow]").strip()
            if choice not in menu:
                self.console.print(f"[cyan]→ Running Custom Command: {choice}[/cyan]")
                self.console.print(self.run_command(choice))
                print("\n")
                time.sleep(1)
                continue

            label, action = menu[choice]
            if choice == "0":
                self.console.print("[bold red]Exiting...[/bold red]")
                break

            self.console.print(f"[cyan]→ Running: {label}[/cyan]")
            action()
            self.console.print("[dim]Done![/dim]\n")
            time.sleep(0.3)



    
