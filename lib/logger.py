from rich.console import Console
from datetime import datetime

class Log:
    def __init__(self):
        self.console = Console()

    def _time(self):
        return datetime.now().strftime("%H:%M:%S")

    def info(self, msg):
        self.console.print(f"[bold cyan][{self._time()}][/bold cyan] [bold yellow][INFO][/bold yellow] {msg}")

    def warning(self, msg):
        self.console.print(f"[bold cyan][{self._time()}][/bold cyan] [bold orange3][WARN][/bold orange3] {msg}")

    def error(self, msg):
        self.console.print(f"[bold cyan][{self._time()}][/bold cyan] [bold red][ERROR][/bold red] {msg}")

    def custom(self, level, color, msg):
        self.console.print(f"[bold {color}][{self._time()}][/bold {color}] [bold {color}][{level.upper()}][/bold {color}] {msg}")
