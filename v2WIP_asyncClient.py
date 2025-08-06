# rpg_client_rich.py

import asyncio
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout

console = Console()

class RPGClient:
    def __init__(self):
        self.reader = None
        self.writer = None
        self.messages = []
        self.timer_panel = ""  # Stores timer visual section

    async def handle_input(self):
        while True:
            msg = await asyncio.get_event_loop().run_in_executor(None, input, "")
            self.writer.write((msg + "\n").encode())
            await self.writer.drain()

    async def handle_server(self):
        buffer = ""
        while True:
            data = await self.reader.readline()
            if not data:
                self.messages.append("[red]Disconnected from server.")
                return
            line = data.decode().rstrip()

            # Capture progress bar section if present
            if line.startswith("-- Turn Timers --"):
                buffer = line + "\n"
                while True:
                    data = await self.reader.readline()
                    if not data:
                        break
                    segment = data.decode().rstrip()
                    if segment.strip() == "":
                        break
                    buffer += segment + "\n"
                self.timer_panel = buffer
            else:
                self.messages.append(line)

    def render(self) -> Panel:
        """Render combined output with Rich panels."""
        text = "\n".join(self.messages[-20:])  # Show last 20 messages
        layout = Layout()
        layout.split(
            Layout(Panel(Text(self.timer_panel), title="Timers"), name="upper", size=10),
            Layout(Panel(Text(text), title="Messages"), name="lower"),
        )
        return layout

    async def main(self):
        self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8888)
        console.print("[bold green]Connected to RPG server![/bold green]")

        # Use Rich Live updating for clean terminal UI
        with Live(console=self.console, refresh_per_second=10) as live:
            task_input = asyncio.create_task(self.handle_input())
            task_server = asyncio.create_task(self.handle_server())

            while not task_input.done() and not task_server.done():
                live.update(self.render())
                await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        client = RPGClient()
        asyncio.run(client.main())
    except KeyboardInterrupt:
        console.print("\n[bold red]Client exited.[/bold red]")
