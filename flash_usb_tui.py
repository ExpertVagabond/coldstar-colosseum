#!/usr/bin/env python3
"""
Coldstar USB Flashing Terminal UI
Beautiful TUI for flashing USB drives with the cold wallet vault
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, ProgressBar, Footer
from textual.binding import Binding
from rich.console import RenderableType
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.table import Table
import asyncio
from typing import Optional


class USBInfoBox(Static):
    """Display target USB device information"""

    def __init__(self, device_name: str, device_path: str, device_info: str):
        super().__init__()
        self.device_name = device_name
        self.device_path = device_path
        self.device_info = device_info

    def render(self) -> RenderableType:
        content = Table.grid(padding=(0, 2))
        content.add_column(style="bold cyan", no_wrap=True)
        content.add_column()

        # Lock icon and device name
        content.add_row("🔒", f"[bold white]{self.device_name}[/] [dim]{self.device_path}[/]")
        content.add_row("⋮", f"[dim]{self.device_info}[/]")

        return Panel(
            content,
            title="[bold yellow]TARGET USB VAULT[/]",
            border_style="yellow",
            padding=(1, 2)
        )


class FlashStep(Static):
    """Individual flashing step with progress"""

    def __init__(self, step_num: int, total_steps: int, description: str, status: str = "pending"):
        super().__init__()
        self.step_num = step_num
        self.total_steps = total_steps
        self.description = description
        self.status = status  # pending, active, done
        self.progress = 0

    def render(self) -> RenderableType:
        # Status icon
        if self.status == "done":
            icon = "[green]✓[/]"
            desc_style = "dim green"
            suffix = "[green]Done[/]"
        elif self.status == "active":
            icon = "[yellow]├[/]"
            desc_style = "bold white"
            # Progress bar
            bar_width = 50
            filled = int(bar_width * self.progress / 100)
            bar = "█" * filled
            suffix = f"[green]{bar}[/] {self.progress}%"
        else:
            icon = "[dim]├[/]"
            desc_style = "dim white"
            suffix = "·" * 80

        step_label = f"[dim]{self.step_num}[/] [white]/[/] [dim]{self.total_steps}[/]"

        # Build the line
        line = f"[dim]····[/] {icon} {step_label} [bold]{self.description}[/] "

        # Pad to align suffix
        padding = 90 - len(self.description) - 10
        line += "·" * padding + " " + suffix

        return Text.from_markup(line)

    def update_progress(self, progress: int):
        self.progress = progress
        self.refresh()

    def set_status(self, status: str):
        self.status = status
        self.refresh()


class HardwareIDDisplay(Static):
    """Display hardware ID"""

    def __init__(self, hw_id: str = ""):
        super().__init__()
        self.hw_id = hw_id

    def render(self) -> RenderableType:
        if self.hw_id:
            return Text.from_markup(f"      [dim]├────[/] Hardware ID [cyan]{self.hw_id}[/] ·" + "·" * 80)
        return Text("")


class OverallProgress(Static):
    """Overall progress bar"""

    def __init__(self):
        super().__init__()
        self.progress = 0

    def render(self) -> RenderableType:
        bar_width = 70
        filled = int(bar_width * self.progress / 100)

        # Create progress bar
        filled_bar = "█" * filled
        empty_bar = "█" * (bar_width - filled)

        progress_text = f"\n      Progress [green]{filled_bar}[/][dim]{empty_bar}[/] {self.progress}%\n"
        return Text.from_markup(progress_text)

    def update_progress(self, progress: int):
        self.progress = progress
        self.refresh()


class WarningMessage(Static):
    """Warning message"""

    def render(self) -> RenderableType:
        return Text.from_markup(
            "\n" + "─" * 50 + " [bold yellow]DO NOT REMOVE THE DRIVE[/] " + "─" * 50 + "\n"
        )


class KeyboardHints(Static):
    """Keyboard shortcut hints"""

    def render(self) -> RenderableType:
        hints = Table.grid(padding=(0, 4))
        hints.add_column(style="dim")
        hints.add_column(style="white")
        hints.add_column(style="dim")
        hints.add_column(style="white")

        hints.add_row(
            "[x]", "Abort immediately and wipe",
            "─" * 20,
            ""
        )
        hints.add_row(
            "", "",
            "[red bold][ESC][/] Abort",
            "[dim]Ctrl+C Abort immediatly[/]"
        )
        hints.add_row(
            "[e]", "Eject safely when ready",
            "─" * 20,
            ""
        )

        return hints


class FlashUSBApp(App):
    """Coldstar USB Flashing TUI Application"""

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        width: 100%;
        height: 100%;
        background: $surface;
        border: heavy white;
        padding: 1 2;
    }

    #header {
        width: 100%;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #flash-content {
        width: 100%;
        padding: 2 4;
        border: heavy $primary;
        background: $surface;
    }

    #steps-container {
        width: 100%;
        height: auto;
        padding: 1 0;
    }

    #status-message {
        width: 100%;
        content-align: center middle;
        padding: 1 0;
        color: $warning;
    }
    """

    BINDINGS = [
        Binding("escape", "abort", "Abort", priority=True),
        Binding("x", "abort_wipe", "Abort & Wipe"),
        Binding("e", "eject", "Eject Safely"),
        Binding("ctrl+c", "abort", "Abort Immediately"),
    ]

    def __init__(
        self,
        device_name: str = "KIOXIA 32GB",
        device_path: str = "/dev/sdb",
        device_info: str = "1CD6-FFFF removable • SN:L4330..."
    ):
        super().__init__()
        self.device_name = device_name
        self.device_path = device_path
        self.device_info = device_info
        self.is_flashing = False
        self.flash_complete = False

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        with Container(id="main-container"):
            yield Static("[bold]FLASH COLD WALLET USB[/]", id="header")

            with Vertical(id="flash-content"):
                # USB info box
                yield USBInfoBox(self.device_name, self.device_path, self.device_info)

                # Status message
                yield Static("[yellow]Flashing vault to USB drive...[/]", id="status-message")

                # Steps container
                with Vertical(id="steps-container"):
                    self.step1 = FlashStep(1, 4, "Formatting /dev/sdb", "done")
                    self.step2 = FlashStep(2, 4, "Writing secure vault", "active")
                    self.step3 = FlashStep(3, 4, "Encrypting master key", "pending")
                    self.step4 = FlashStep(4, 4, "Verifying integrity", "pending")

                    yield self.step1
                    yield self.step2
                    yield self.step3
                    yield self.step4

                    # Hardware ID
                    self.hw_id = HardwareIDDisplay("SFOD-Vy9X-H9xz-S3Ru")
                    yield self.hw_id

                # Overall progress
                self.overall_progress = OverallProgress()
                yield self.overall_progress

                # Warning
                yield WarningMessage()

                # Keyboard hints
                yield KeyboardHints()

    async def on_mount(self) -> None:
        """Start the flashing simulation when app mounts"""
        self.is_flashing = True
        self.set_interval(0.1, self.update_flash_progress)

    def update_flash_progress(self) -> None:
        """Simulate flashing progress"""
        if not self.is_flashing or self.flash_complete:
            return

        # Update step 2 progress (simulate)
        if self.step2.status == "active" and self.step2.progress < 100:
            self.step2.update_progress(min(100, self.step2.progress + 1))

            # Update overall progress (step 1 done = 25%, step 2 in progress)
            overall = 25 + (self.step2.progress * 0.25)
            self.overall_progress.update_progress(int(overall))

            # Move to step 3 when step 2 is done
            if self.step2.progress >= 100:
                self.step2.set_status("done")
                self.step3.set_status("active")

        # Update step 3 progress
        elif self.step3.status == "active" and self.step3.progress < 100:
            self.step3.update_progress(min(100, self.step3.progress + 2))
            overall = 50 + (self.step3.progress * 0.25)
            self.overall_progress.update_progress(int(overall))

            if self.step3.progress >= 100:
                self.step3.set_status("done")
                self.step4.set_status("active")

        # Update step 4 progress
        elif self.step4.status == "active" and self.step4.progress < 100:
            self.step4.update_progress(min(100, self.step4.progress + 3))
            overall = 75 + (self.step4.progress * 0.25)
            self.overall_progress.update_progress(int(overall))

            if self.step4.progress >= 100:
                self.step4.set_status("done")
                self.flash_complete = True
                self.query_one("#status-message", Static).update(
                    "[bold green]✓ Flash complete! Safe to eject.[/]"
                )

    def action_abort(self) -> None:
        """Abort the flashing process"""
        if self.flash_complete:
            self.exit()
        else:
            self.is_flashing = False
            self.query_one("#status-message", Static).update(
                "[bold red]⚠ Flashing aborted! Drive may be corrupted.[/]"
            )

    def action_abort_wipe(self) -> None:
        """Abort and wipe the drive"""
        self.is_flashing = False
        self.query_one("#status-message", Static).update(
            "[bold red]⚠ Aborting and wiping drive...[/]"
        )
        # In real implementation, would wipe the drive here

    def action_eject(self) -> None:
        """Safely eject the drive"""
        if self.flash_complete:
            self.query_one("#status-message", Static).update(
                "[bold green]✓ Ejecting drive safely...[/]"
            )
            self.exit()
        else:
            self.query_one("#status-message", Static).update(
                "[bold yellow]⚠ Flashing still in progress. Press ESC to abort first.[/]"
            )


def run_flash_ui(device_name: str = "KIOXIA 32GB",
                 device_path: str = "/dev/sdb",
                 device_info: str = "1CD6-FFFF removable • SN:L4330..."):
    """Launch the USB flashing TUI"""
    app = FlashUSBApp(device_name, device_path, device_info)
    app.run()


if __name__ == "__main__":
    run_flash_ui()
