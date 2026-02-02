#!/usr/bin/env python3
"""
Coldstar Vault Dashboard Terminal UI
Beautiful TUI for managing portfolio, viewing token details, and sending transactions
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Input, Button, Footer, Header
from textual.binding import Binding
from textual.reactive import reactive
from rich.console import RenderableType
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from datetime import datetime
from typing import List, Dict, Optional
import asyncio


class StatusBar(Static):
    """Top status bar showing vault info"""

    def __init__(self, vault_name: str, mode: str, network: str):
        super().__init__()
        self.vault_name = vault_name
        self.mode = mode
        self.network = network
        self.last_sync = "2m ago"
        self.warnings = 0
        self.total_value = 12431
        self.change_24h = 1.8

    def render(self) -> RenderableType:
        # Build status line
        status = f"[bold cyan]COLDSTAR[/] • Vault: [yellow]{self.vault_name}[/] • "
        status += f"[{'green' if self.mode == 'OFFLINE SIGNING' else 'yellow'}]{self.mode}[/] • "
        status += f"RPC: [cyan]{self.network}[/]"

        # Build stats line
        change_color = "green" if self.change_24h >= 0 else "red"
        change_sign = "+" if self.change_24h >= 0 else ""
        stats = f"Last sync [cyan]{self.last_sync}[/] • "
        stats += f"[yellow]{self.warnings}[/] warnings • "
        stats += f"Total [bold green]${self.total_value:,}[/] • "
        stats += f"24h [{change_color}]{change_sign}{self.change_24h}%[/]"

        return f"{status}\n{stats}"


class PortfolioPanel(Static):
    """Left panel showing portfolio tokens"""

    def __init__(self):
        super().__init__()
        self.tokens = [
            {"symbol": "SOL", "icon": "◎", "amount": 3.2546, "value": 476.80, "color": "magenta"},
            {"symbol": "USDC", "icon": "◉", "amount": 1025.00, "value": 1025.00, "color": "cyan"},
            {"symbol": "BTC", "icon": "฿", "amount": 0.0125, "value": 600.50, "color": "yellow"},
            {"symbol": "RAY", "icon": "⚡", "amount": 500.0, "value": 85.00, "color": "yellow"},
            {"symbol": "XYZ", "icon": "◆", "amount": 10.000, "value": 0.00, "color": "cyan"},
            {"symbol": "Unknown Token", "icon": "⚠", "amount": 10.000, "value": 0.00, "color": "red"},
        ]
        self.selected_index = 1  # USDC selected

    def render(self) -> RenderableType:
        table = Table.grid(padding=(0, 1))
        table.add_column("Icon", style="bold", width=3)
        table.add_column("Symbol", style="bold white", no_wrap=True)
        table.add_column("Amount", justify="right", style="white")
        table.add_column("Value", justify="right", style="green")

        for idx, token in enumerate(self.tokens):
            # Highlight selected token
            if idx == self.selected_index:
                icon = f"[{token['color']} on #1a1a1a]>{token['icon']}[/]"
                symbol = f"[bold white on #1a1a1a]{token['symbol']}[/]"
                amount = f"[white on #1a1a1a]{token['amount']:,.4f}[/]"
                value = f"[green on #1a1a1a]{token['value']:,.2f}[/]"
            else:
                icon = f"[{token['color']}]{token['icon']}[/]"
                symbol = f"[white]{token['symbol']}[/]"
                amount = f"[white]{token['amount']:,.4f}[/]"
                if token['value'] == 0.00:
                    value = f"[red]{token['value']:.2f} F[/]"
                else:
                    value = f"[green]{token['value']:,.2f}[/]"

            table.add_row(icon, symbol, amount, value)

        return Panel(
            table,
            title="[bold]Portfolio[/]",
            border_style="cyan",
            padding=(1, 1)
        )


class TokenDetailsPanel(Static):
    """Middle panel showing selected token details"""

    def __init__(self):
        super().__init__()
        self.token_symbol = "USDC"
        self.mint_address = "EPjFW...DeF2"
        self.decimals = 6
        self.verified = True

    def render(self) -> RenderableType:
        # Token info
        info_table = Table.grid(padding=(0, 1))
        info_table.add_column(style="dim white")

        info_table.add_row(
            f"Mint: [cyan]{self.mint_address}[/] • Decimals: [yellow]{self.decimals}[/] • "
            f"[green]✓ Verified SPL Token[/]" if self.verified else "[red]⚠ Unverified[/]"
        )

        # Transaction history
        tx_table = Table.grid(padding=(0, 1))
        tx_table.add_column(style="white", no_wrap=True)
        tx_table.add_column(justify="right", style="white")

        tx_table.add_row("- [green]Received[/] 500.00 USDC", "[dim]30m ago[/]")
        tx_table.add_row("- [yellow]Sent[/] 250.00 USDC", "[dim]2h ago[/]")
        tx_table.add_row("- [green]Received[/] 775.00 USDC", "[dim]1d ago[/]")

        # Risk notes
        risk_table = Table.grid(padding=(0, 1))
        risk_table.add_column(style="dim white")

        risk_table.add_row("\n[bold yellow]Risk Notes:[/]\n")
        risk_table.add_row("• Transfer-hook enabled")
        risk_table.add_row("• Direct transfer • Swap then send")

        content = Table.grid()
        content.add_row(info_table)
        content.add_row("")
        content.add_row(tx_table)
        content.add_row(risk_table)

        return Panel(
            content,
            title=f"[bold]{self.token_symbol} Details[/]",
            border_style="cyan",
            padding=(1, 1)
        )


class SendPanel(Static):
    """Right panel for sending tokens"""

    def __init__(self):
        super().__init__()
        self.token_symbol = "USDC"
        self.to_address = "4xp...Tf8Y"
        self.amount = 100.00
        self.fee_mode = "Standard"
        self.network_fee = 0.00005

    def render(self) -> RenderableType:
        content = Table.grid(padding=(0, 1))
        content.add_column(style="white", width=10)
        content.add_column(style="white")

        # To address
        content.add_row("To:", f"[cyan]{self.to_address}[/] [dim]v[/]")
        content.add_row("")

        # Amount with quick select
        content.add_row(
            "Amount:",
            f"[bold white]{self.amount:.2f}[/]  [dim][a max] [25% 50% 75% 100%][/]"
        )
        content.add_row("")

        # Fee options
        content.add_row(
            "Fee:",
            f"[bold green][{self.fee_mode}][/]  [dim]Fast  Custom[/]"
        )
        content.add_row("")
        content.add_row(
            "",
            f"[dim]Network fee ~{self.network_fee} SOL • You'll have 3.15 SOL left[/]"
        )

        # Review section
        content.add_row("")
        content.add_row("", "[bold]Review:[/]")
        content.add_row("")

        review_table = Table.grid(padding=(0, 1))
        review_table.add_column(style="dim white", width=8)
        review_table.add_column(style="white")

        review_table.add_row("-", f"[bold]USDC[/]  [white]{self.amount:.2f}[/]")
        review_table.add_row("-", f"[bold]To:[/]   [cyan]{self.to_address}[/]")
        review_table.add_row("")
        review_table.add_row("", f"Expected fee: [yellow]~{self.network_fee} SOL[/]")

        content.add_row("", review_table)
        content.add_row("")
        content.add_row("", f"Press [bold green]ENTER[/] to confirm:")
        content.add_row("")
        content.add_row("", "[bold green][ENTER] Send[/] • [dim][x] Cancel[/]")
        content.add_row("")
        content.add_row("", "[dim]Arrows navigate • a = max • 1|2|3|4 = % split[/]")

        return Panel(
            content,
            title=f"[bold]Send {self.token_symbol}[/]",
            border_style="cyan",
            padding=(1, 1)
        )


class FooterBar(Static):
    """Bottom footer with navigation hints"""

    def render(self) -> RenderableType:
        return Text.from_markup(
            "[dim]/ Search • Tab Sort • Space Multi-select[/]",
            justify="left"
        )


class VaultDashboardApp(App):
    """Coldstar Vault Dashboard TUI Application"""

    CSS = """
    Screen {
        background: $surface;
    }

    #status-bar {
        width: 100%;
        height: 3;
        padding: 0 2;
        background: $panel;
        border-bottom: heavy $primary;
    }

    #main-panels {
        width: 100%;
        height: 1fr;
        padding: 1;
    }

    #portfolio-container {
        width: 1fr;
        height: 100%;
        padding: 0 1;
    }

    #details-container {
        width: 1fr;
        height: 100%;
        padding: 0 1;
    }

    #send-container {
        width: 1fr;
        height: 100%;
        padding: 0 1;
    }

    #footer-bar {
        width: 100%;
        height: 1;
        padding: 0 2;
        background: $panel;
        border-top: heavy $primary;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("tab", "focus_next", "Next Panel"),
        Binding("shift+tab", "focus_previous", "Previous Panel"),
        Binding("/", "search", "Search"),
        Binding("r", "refresh", "Refresh"),
        Binding("s", "send", "Send"),
    ]

    def __init__(self):
        super().__init__()
        self.vault_name = "usb-03"
        self.mode = "OFFLINE SIGNING"
        self.network = "mainnet"

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        # Status bar
        yield StatusBar(self.vault_name, self.mode, self.network)

        # Main three-column layout
        with Horizontal(id="main-panels"):
            with Vertical(id="portfolio-container"):
                yield PortfolioPanel()

            with Vertical(id="details-container"):
                yield TokenDetailsPanel()

            with Vertical(id="send-container"):
                yield SendPanel()

        # Footer
        yield FooterBar()

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()

    def action_search(self) -> None:
        """Open search"""
        # Placeholder for search functionality
        pass

    def action_refresh(self) -> None:
        """Refresh data"""
        # Placeholder for refresh functionality
        pass

    def action_send(self) -> None:
        """Open send dialog"""
        # Placeholder for send functionality
        pass


def run_vault_dashboard(vault_name: str = "usb-03", network: str = "mainnet"):
    """Launch the vault dashboard TUI"""
    app = VaultDashboardApp()
    app.run()


if __name__ == "__main__":
    run_vault_dashboard()
