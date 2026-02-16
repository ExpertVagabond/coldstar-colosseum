#!/usr/bin/env python3
"""
Coldstar Dashboard TUI
Terminal-native version of coldstar.dev — features, architecture, FairScore, vault, and USB tools.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Footer, Header, Button, ListView, ListItem, Label
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import Screen
from rich.console import RenderableType
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.layout import Layout
from rich import box


# ── Data ────────────────────────────────────────────────────────────────────

FEATURES = [
    ("RAM-Only Keys", "Private keys exist only in volatile memory. Power off = keys gone. No disk, no trace, no recovery attack surface.", "cyan"),
    ("Disposable Hardware", "Any $5-10 USB becomes a hardware wallet. No proprietary chips, no vendor lock-in, no supply chain trust.", "green"),
    ("CLI-First Design", "Built for developers and power users. Rich terminal UI, scriptable operations, full automation support.", "yellow"),
    ("Open Source (MIT)", "100% transparent Python codebase. Every line auditable. Reproducible builds. Community-verified security.", "magenta"),
    ("AES-256 Encryption", "Military-grade encryption for key storage. Paired with Ed25519 signatures and NaCl constant-time crypto.", "red"),
    ("No Vendor Lock-in", "Works with commodity hardware. No firmware updates from a company that might get acquired or shut down.", "blue"),
]

DAO_FEATURES = [
    ("Multi-Sig Governance", "3-of-5 threshold signing for DAO treasury operations. Air-gapped vote collection.", "cyan"),
    ("FairScore Weighted", "Vote power scales with on-chain reputation. Higher trust = more governance influence.", "green"),
    ("Proposal System", "Create, vote, and execute proposals entirely from the terminal. Full audit trail.", "yellow"),
    ("Treasury Management", "Manage DAO funds with the same air-gap security as personal wallets.", "magenta"),
]

PORTFOLIO = [
    {"symbol": "SOL", "icon": "◎", "amount": 3.2546, "value": 476.80, "color": "magenta", "change": "+2.4%"},
    {"symbol": "USDC", "icon": "◉", "amount": 1025.00, "value": 1025.00, "color": "cyan", "change": "+0.0%"},
    {"symbol": "BTC", "icon": "฿", "amount": 0.0125, "value": 600.50, "color": "yellow", "change": "+1.2%"},
    {"symbol": "RAY", "icon": "⚡", "amount": 500.0, "value": 85.00, "color": "yellow", "change": "-3.1%"},
    {"symbol": "JUP", "icon": "♃", "amount": 250.0, "value": 312.50, "color": "green", "change": "+5.7%"},
    {"symbol": "BONK", "icon": "🐕", "amount": 5000000, "value": 125.00, "color": "red", "change": "-1.8%"},
]

COMPARISON = [
    ("", "Coldstar", "Ledger", "Phantom", "Paper"),
    ("Air-Gap Signing", "Yes", "Partial", "No", "No"),
    ("Open Source", "100%", "Partial", "No", "N/A"),
    ("Cost", "$5-10", "$79-149", "Free", "Free"),
    ("DeFi Integration", "Jupiter/Pyth", "Limited", "Full", "None"),
    ("Reputation Layer", "FairScore", "None", "None", "None"),
    ("DAO Governance", "Built-in", "None", "None", "None"),
    ("Vendor Lock-in", "None", "High", "Medium", "None"),
]

ARCHITECTURE_ART = """
[bold cyan]ONLINE DEVICE[/]                         [bold green]AIR-GAPPED USB[/]
┌───────────────────────┐    QR     ┌───────────────────────┐
│                       │ ────────► │                       │
│  [cyan]FairScore API[/]        │           │  [green]Alpine Linux 3.19[/]    │
│  [cyan]Jupiter V6 DEX[/]       │           │  [green]Ed25519 Signing[/]      │
│  [cyan]Pyth Price Feeds[/]     │           │  [green]Encrypted Key Store[/]  │
│  [cyan]Rich Terminal UI[/]     │ ◄──────── │  [green]Network Blacklisted[/]  │
│                       │    QR     │                       │
└───────────┬───────────┘           └───────────────────────┘
            │
            ▼
┌───────────────────────┐
│   [yellow]SOLANA NETWORK[/]       │
│  Mainnet / Devnet     │
│  RPC + Broadcasting   │
└───────────────────────┘"""

FAIRSCORE_ART = """
[bold white]FAIRSCORE REPUTATION TIERS[/]

 Tier 5  [bold magenta]Diamond[/]   ████████████████████████████████  80-100  [magenta]Full access, max limits[/]
 Tier 4  [bold cyan]Platinum[/]  ████████████████████████           60-79   [cyan]High limits, priority[/]
 Tier 3  [bold green]Gold[/]      ████████████████                   40-59   [green]Standard operations[/]
 Tier 2  [bold yellow]Silver[/]    ████████                           20-39   [yellow]Reduced limits, warnings[/]
 Tier 1  [bold red]Bronze[/]    ████                               0-19    [red]BLOCKED — hard deny[/]

[dim]FairScore checks happen BEFORE the air-gap crossing — the point of no return.[/]
[dim]Every transaction, every swap, every DAO vote is reputation-gated.[/]"""

FLASH_STEPS = [
    ("Download Alpine Linux", "Fetching minimal rootfs (~50MB)"),
    ("Create Wallet Structure", "Building /wallet, /inbox, /outbox directories"),
    ("Blacklist Network Drivers", "Disabling e1000, iwlwifi, r8169, bluetooth"),
    ("Generate Bootable ISO", "Creating GRUB bootloader + cold wallet image"),
]


# ── Widgets ─────────────────────────────────────────────────────────────────

class NavItem(Static):
    """Sidebar navigation item"""

    def __init__(self, label: str, key: str, active: bool = False) -> None:
        super().__init__()
        self.label = label
        self.key = key
        self.is_active = active

    def render(self) -> RenderableType:
        if self.is_active:
            return Text.from_markup(f"  [bold cyan]▸ {self.label}[/]")
        return Text.from_markup(f"  [dim]  {self.label}[/]")


class HeroView(Static):
    """Home / hero screen"""

    def render(self) -> RenderableType:
        lines = []
        lines.append("")
        lines.append("[bold cyan]╔═══════════════════════════════════════════════════════════════╗[/]")
        lines.append("[bold cyan]║[/]                                                               [bold cyan]║[/]")
        lines.append("[bold cyan]║[/]     [bold white]C O L D S T A R[/]                                        [bold cyan]║[/]")
        lines.append("[bold cyan]║[/]     [dim]Air-Gapped Cold Signing for Solana[/]                       [bold cyan]║[/]")
        lines.append("[bold cyan]║[/]                                                               [bold cyan]║[/]")
        lines.append("[bold cyan]╚═══════════════════════════════════════════════════════════════╝[/]")
        lines.append("")
        lines.append("  [bold white]Turn any $5 USB drive into hardware-grade security.[/]")
        lines.append("  [dim]No proprietary chips. No vendor lock-in. 100% open source.[/]")
        lines.append("")
        lines.append("  [bold cyan]━━━ Quick Stats ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
        lines.append("")

        stats = Table.grid(padding=(0, 4))
        stats.add_column(justify="center")
        stats.add_column(justify="center")
        stats.add_column(justify="center")
        stats.add_column(justify="center")
        stats.add_row(
            "[bold cyan]13K+[/]\n[dim]Lines of Python[/]",
            "[bold green]1.6K[/]\n[dim]Lines of Rust[/]",
            "[bold yellow]~50MB[/]\n[dim]Alpine Linux[/]",
            "[bold magenta]$5-10[/]\n[dim]USB Cost[/]",
        )

        content = Text.from_markup("\n".join(lines))

        grid = Table.grid(padding=1)
        grid.add_row(content)
        grid.add_row(stats)
        grid.add_row("")
        grid.add_row(Text.from_markup(
            "  [bold cyan]━━━ Ecosystem ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]"
        ))
        grid.add_row("")

        partners = Table.grid(padding=(0, 3))
        partners.add_column(justify="center")
        partners.add_column(justify="center")
        partners.add_column(justify="center")
        partners.add_column(justify="center")
        partners.add_column(justify="center")
        partners.add_row(
            "[bold magenta]◎ Solana[/]",
            "[bold cyan]⬡ Squads[/]",
            "[bold yellow]⟐ Meteora[/]",
            "[bold green]◈ Pyth[/]",
            "[bold blue]⬢ FairScale[/]",
        )
        grid.add_row(partners)
        grid.add_row("")
        grid.add_row(Text.from_markup(
            "  [dim]Press [bold]1-6[/dim] to navigate  •  [dim][bold]q[/bold] quit  •  [bold]?[/bold] help[/]"
        ))

        return grid


class FeaturesView(Static):
    """Features display"""

    def render(self) -> RenderableType:
        grid = Table.grid(padding=(1, 2))
        grid.add_column(width=45)
        grid.add_column(width=45)

        panels = []
        for name, desc, color in FEATURES:
            panel = Panel(
                f"[{color}]{desc}[/]",
                title=f"[bold {color}]{name}[/]",
                border_style=color,
                padding=(1, 2),
                width=43,
            )
            panels.append(panel)

        for i in range(0, len(panels), 2):
            left = panels[i]
            right = panels[i + 1] if i + 1 < len(panels) else ""
            grid.add_row(left, right)

        outer = Table.grid()
        outer.add_row(Text.from_markup("\n  [bold white]Security Features[/]  [dim]— What makes Coldstar different[/]\n"))
        outer.add_row(grid)

        return outer


class ArchitectureView(Static):
    """Architecture diagram"""

    def render(self) -> RenderableType:
        grid = Table.grid(padding=1)
        grid.add_row(Text.from_markup("\n  [bold white]System Architecture[/]  [dim]— Air-gap isolation model[/]\n"))
        grid.add_row(Panel(
            Text.from_markup(ARCHITECTURE_ART),
            border_style="cyan",
            padding=(1, 2),
            title="[bold]Data Flow[/]",
        ))
        grid.add_row("")
        grid.add_row(Text.from_markup(
            "  [bold white]How It Works:[/]\n"
            "  [dim]1.[/] Create unsigned transaction on [cyan]online device[/]\n"
            "  [dim]2.[/] Transfer via QR code across the [yellow]physical air gap[/]\n"
            "  [dim]3.[/] Sign with Ed25519 key on [green]offline USB[/] (network drivers blacklisted)\n"
            "  [dim]4.[/] Transfer signed TX back via QR, broadcast to [yellow]Solana[/]\n"
            "  [dim]5.[/] Private key [bold red]never touches[/] an internet-connected device"
        ))

        return grid


class FairScoreView(Static):
    """FairScore reputation system"""

    def render(self) -> RenderableType:
        grid = Table.grid(padding=1)
        grid.add_row(Text.from_markup("\n  [bold white]FairScore Integration[/]  [dim]— Reputation-gated signing[/]\n"))
        grid.add_row(Panel(
            Text.from_markup(FAIRSCORE_ART),
            border_style="green",
            padding=(1, 2),
            title="[bold]Reputation Tiers[/]",
        ))
        grid.add_row("")

        # Demo: Bronze block
        block_demo = (
            "[bold red]═══════════ FAIRSCORE REPUTATION CHECK ═══════════[/]\n"
            "Checking reputation for [cyan]5xGh...Tf8Y[/]\n\n"
            "╭──────── FairScore Reputation ────────╮\n"
            "│  Address:     [cyan]5xGh...Tf8Y[/]            │\n"
            "│  Reputation:  [bold red]!!! UNTRUSTED[/]          │\n"
            "│  Tier:        [bold red]Bronze (1/5)[/]           │\n"
            "│  FairScore:   [bold red]12.3/100[/]               │\n"
            "│  TX Limit:    [bold red]BLOCKED[/]                │\n"
            "╰──────────────────────────────────────╯\n\n"
            "[bold red]✗ TRANSACTION BLOCKED[/]\n"
            "[red]✗ FairScore 12.3, Tier: bronze — transaction denied[/]"
        )

        grid.add_row(Panel(
            Text.from_markup(block_demo),
            border_style="red",
            title="[bold red]Demo — Bronze BLOCK[/]",
            padding=(1, 2),
        ))

        return grid


class ComparisonView(Static):
    """Comparison table"""

    def render(self) -> RenderableType:
        table = Table(
            title="[bold]Cold Storage Comparison[/]",
            box=box.ROUNDED,
            border_style="cyan",
            padding=(0, 1),
            show_lines=True,
        )
        table.add_column("Feature", style="bold white", min_width=18)
        table.add_column("Coldstar", style="bold cyan", justify="center", min_width=12)
        table.add_column("Ledger", style="dim", justify="center", min_width=12)
        table.add_column("Phantom", style="dim", justify="center", min_width=12)
        table.add_column("Paper", style="dim", justify="center", min_width=12)

        for row in COMPARISON[1:]:
            feature, coldstar, ledger, phantom, paper = row
            # Color the Coldstar column green for "Yes" values
            if coldstar in ("Yes", "100%", "Built-in", "FairScore", "None", "Jupiter/Pyth"):
                coldstar_styled = f"[bold green]{coldstar}[/]"
            else:
                coldstar_styled = f"[cyan]{coldstar}[/]"
            table.add_row(feature, coldstar_styled, ledger, phantom, paper)

        grid = Table.grid(padding=1)
        grid.add_row(Text.from_markup("\n  [bold white]How We Compare[/]  [dim]— vs. existing solutions[/]\n"))
        grid.add_row(table)

        return grid


class VaultView(Static):
    """Portfolio / vault dashboard"""

    def render(self) -> RenderableType:
        # Portfolio table
        ptable = Table(
            box=box.SIMPLE_HEAVY,
            border_style="cyan",
            padding=(0, 1),
            show_edge=False,
        )
        ptable.add_column("", width=3)
        ptable.add_column("Token", style="bold white", min_width=8)
        ptable.add_column("Amount", justify="right", style="white", min_width=14)
        ptable.add_column("Value", justify="right", style="green", min_width=10)
        ptable.add_column("24h", justify="right", min_width=8)

        total = 0
        for t in PORTFOLIO:
            change_color = "green" if t["change"].startswith("+") else "red"
            ptable.add_row(
                f"[{t['color']}]{t['icon']}[/]",
                f"[{t['color']}]{t['symbol']}[/]",
                f"{t['amount']:,.4f}",
                f"${t['value']:,.2f}",
                f"[{change_color}]{t['change']}[/]",
            )
            total += t["value"]

        ptable.add_section()
        ptable.add_row("", "[bold]Total[/]", "", f"[bold green]${total:,.2f}[/]", "")

        # Transaction history
        tx_table = Table.grid(padding=(0, 1))
        tx_table.add_column(style="dim", width=10)
        tx_table.add_column(style="white")
        tx_table.add_column(justify="right", style="dim")

        tx_table.add_row("[green]Received[/]", "500.00 USDC from [cyan]4xp...Mn3R[/]", "30m ago")
        tx_table.add_row("[yellow]Sent[/]", "0.5 SOL to [cyan]7gX...kK8[/]", "2h ago")
        tx_table.add_row("[green]Received[/]", "775.00 USDC from [cyan]JUPy...vCN[/]", "1d ago")
        tx_table.add_row("[cyan]Swapped[/]", "1.0 SOL → 146.80 USDC via Jupiter", "2d ago")
        tx_table.add_row("[magenta]Voted[/]", "DAO Proposal #3 — Approve", "3d ago")

        grid = Table.grid(padding=1)
        grid.add_row(Text.from_markup("\n  [bold white]Vault Dashboard[/]  [dim]— Portfolio & transactions[/]\n"))

        # Status bar
        grid.add_row(Panel(
            Text.from_markup(
                "[bold cyan]COLDSTAR[/] • Vault: [yellow]Primary[/] • "
                "[green]OFFLINE SIGNING[/] • RPC: [cyan]mainnet-beta[/]    "
                f"Total [bold green]${total:,.2f}[/] • 24h [green]+1.8%[/]"
            ),
            border_style="cyan",
            padding=(0, 1),
        ))
        grid.add_row("")

        # Two-column layout
        cols = Table.grid(padding=(0, 2))
        cols.add_column(width=55)
        cols.add_column(width=50)

        cols.add_row(
            Panel(ptable, title="[bold]Portfolio[/]", border_style="cyan", padding=(1, 1)),
            Panel(tx_table, title="[bold]Recent Transactions[/]", border_style="green", padding=(1, 1)),
        )
        grid.add_row(cols)

        return grid


class DAOView(Static):
    """DAO governance view"""

    def render(self) -> RenderableType:
        grid = Table.grid(padding=1)
        grid.add_row(Text.from_markup("\n  [bold white]DAO Governance[/]  [dim]— Multi-sig treasury management[/]\n"))

        # Vault info
        vault_info = (
            "[bold cyan]Coldstar DAO[/]  •  [yellow]3-of-5 Multi-Sig[/]  •  Network: [cyan]devnet[/]\n\n"
            "  Address:  [cyan]Ue6Z...Xeat[/]\n"
            "  Registry: [cyan]2ueu...ViZx[/]\n"
            "  Treasury: [green]$12,431.50[/]\n\n"
            "[bold]Members:[/]\n"
            "  [green]●[/] founder.sol     [dim]FairScore: 87[/]  [magenta]Diamond[/]\n"
            "  [green]●[/] dev-lead.sol    [dim]FairScore: 72[/]  [cyan]Platinum[/]\n"
            "  [green]●[/] security.sol    [dim]FairScore: 65[/]  [cyan]Platinum[/]\n"
            "  [yellow]●[/] advisor-1.sol   [dim]FairScore: 45[/]  [green]Gold[/]\n"
            "  [yellow]●[/] advisor-2.sol   [dim]FairScore: 38[/]  [yellow]Silver[/]"
        )

        # Active proposal
        proposal = (
            "[bold white]Proposal #3:[/] Transfer 500 USDC to dev-lead.sol\n\n"
            "  Status:    [bold green]THRESHOLD REACHED[/] (3/5)\n"
            "  Votes For: [green]███████████████████████████████[/]  3\n"
            "  Against:   [red]██████████[/]                        1\n"
            "  Abstain:   [dim]██████████[/]                        1\n\n"
            "  [dim]Expires in 48h  •  Press [bold]E[/dim] to execute[/]"
        )

        cols = Table.grid(padding=(0, 2))
        cols.add_column(width=50)
        cols.add_column(width=50)
        cols.add_row(
            Panel(Text.from_markup(vault_info), title="[bold]Vault Info[/]", border_style="cyan", padding=(1, 2)),
            Panel(Text.from_markup(proposal), title="[bold]Active Proposal[/]", border_style="green", padding=(1, 2)),
        )
        grid.add_row(cols)
        grid.add_row("")

        # DAO feature cards
        feat_grid = Table.grid(padding=(0, 2))
        feat_grid.add_column(width=24)
        feat_grid.add_column(width=24)
        feat_grid.add_column(width=24)
        feat_grid.add_column(width=24)

        dao_panels = []
        for name, desc, color in DAO_FEATURES:
            dao_panels.append(Panel(
                f"[{color}]{desc}[/]",
                title=f"[bold {color}]{name}[/]",
                border_style=color,
                padding=(0, 1),
                width=23,
            ))
        feat_grid.add_row(*dao_panels)
        grid.add_row(feat_grid)

        return grid


class FlashUSBView(Static):
    """Flash USB interface"""

    def render(self) -> RenderableType:
        grid = Table.grid(padding=1)
        grid.add_row(Text.from_markup("\n  [bold white]Flash USB Cold Wallet[/]  [dim]— Create bootable vault[/]\n"))

        # Device info
        device_info = (
            "  [bold yellow]TARGET USB VAULT[/]\n\n"
            "  Device:    [bold white]Samsung USB 3.1[/] [dim]/dev/disk4[/]\n"
            "  Capacity:  [cyan]32 GB[/]\n"
            "  Hardware:  [dim]USB 3.1 Gen 1 • S/N: 04A1-B3F2[/]\n\n"
            "  [bold red]WARNING:[/] [red]All data on this device will be erased![/]"
        )

        grid.add_row(Panel(
            Text.from_markup(device_info),
            border_style="yellow",
            padding=(1, 2),
        ))
        grid.add_row("")

        # Flash steps
        steps_content = []
        for i, (name, desc) in enumerate(FLASH_STEPS):
            if i == 0:
                icon = "[green]✓[/]"
                bar = "[green]████████████████████████████████████████████████[/] 100%"
                status = "[green]Done[/]"
            elif i == 1:
                icon = "[green]✓[/]"
                bar = "[green]████████████████████████████████████████████████[/] 100%"
                status = "[green]Done[/]"
            elif i == 2:
                icon = "[yellow]▸[/]"
                bar = "[green]██████████████████████████████[/][dim]██████████████████[/] 62%"
                status = "[yellow]In Progress[/]"
            else:
                icon = "[dim]○[/]"
                bar = "[dim]················································[/]   0%"
                status = "[dim]Pending[/]"

            steps_content.append(
                f"  {icon} [bold]Step {i+1}/4[/]  {name}\n"
                f"    [dim]{desc}[/]\n"
                f"    {bar}\n"
            )

        grid.add_row(Panel(
            Text.from_markup("\n".join(steps_content)),
            title="[bold]Flash Progress[/]",
            border_style="cyan",
            padding=(1, 2),
        ))

        # Overall progress
        grid.add_row(Text.from_markup(
            "\n  [bold]Overall:[/] [green]██████████████████████████████████[/][dim]██████████████████████████[/] 56%"
        ))

        return grid


# ── App ─────────────────────────────────────────────────────────────────────

PAGES = ["home", "features", "architecture", "fairscore", "comparison", "vault", "dao", "flash"]
PAGE_LABELS = ["Home", "Features", "Architecture", "FairScore", "Comparison", "Vault", "DAO", "Flash USB"]


class ColdstarApp(App):
    """Coldstar Dashboard — Terminal UI"""

    TITLE = "Coldstar"
    SUB_TITLE = "Air-Gapped Solana Vault"

    CSS = """
    Screen {
        background: #0a0a0f;
    }

    #sidebar {
        width: 22;
        background: #111118;
        border-right: solid #2a2a3a;
        padding: 1 0;
    }

    .nav-header {
        text-align: center;
        padding: 1 0;
        margin-bottom: 1;
    }

    .nav-item {
        height: 3;
        padding: 1 0 0 0;
    }

    .nav-item:hover {
        background: #1a1a2e;
    }

    .nav-item.active {
        background: #1a1a2e;
    }

    #content {
        width: 1fr;
        padding: 0 2;
        overflow-y: auto;
    }

    #main-layout {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("1", "goto_home", "Home"),
        Binding("2", "goto_features", "Features"),
        Binding("3", "goto_arch", "Architecture"),
        Binding("4", "goto_fair", "FairScore"),
        Binding("5", "goto_compare", "Comparison"),
        Binding("6", "goto_vault", "Vault"),
        Binding("7", "goto_dao", "DAO"),
        Binding("8", "goto_flash", "Flash USB"),
        Binding("j", "next_page", "Next"),
        Binding("k", "prev_page", "Previous"),
    ]

    current_page = reactive("home")

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-layout"):
            with Vertical(id="sidebar"):
                yield Static(
                    Text.from_markup("[bold cyan]COLDSTAR[/]\n[dim]Dashboard[/]"),
                    classes="nav-header",
                )
                for i, label in enumerate(PAGE_LABELS):
                    active = "active" if i == 0 else ""
                    yield Static(
                        Text.from_markup(f"  [bold cyan]▸[/] {label}" if i == 0 else f"  [dim]  {label}[/]"),
                        classes=f"nav-item {active}",
                        id=f"nav-{PAGES[i]}",
                    )
            with ScrollableContainer(id="content"):
                yield HeroView(id="view-home")
                yield FeaturesView(id="view-features")
                yield ArchitectureView(id="view-architecture")
                yield FairScoreView(id="view-fairscore")
                yield ComparisonView(id="view-comparison")
                yield VaultView(id="view-vault")
                yield DAOView(id="view-dao")
                yield FlashUSBView(id="view-flash")
        yield Footer()

    def on_mount(self) -> None:
        self._show_page("home")

    def watch_current_page(self, page: str) -> None:
        self._show_page(page)

    def _show_page(self, page: str) -> None:
        # Hide all views
        for p in PAGES:
            widget = self.query_one(f"#view-{p}")
            widget.display = (p == page)

        # Update nav items
        for i, p in enumerate(PAGES):
            nav = self.query_one(f"#nav-{p}")
            label = PAGE_LABELS[i]
            if p == page:
                nav.update(Text.from_markup(f"  [bold cyan]▸ {label}[/]"))
                nav.add_class("active")
            else:
                nav.update(Text.from_markup(f"  [dim]  {label}[/]"))
                nav.remove_class("active")

        # Scroll to top
        content = self.query_one("#content")
        content.scroll_home(animate=False)

    def on_click(self, event) -> None:
        """Handle clicks on nav items"""
        widget = event.widget if hasattr(event, 'widget') else None
        if widget:
            wid = widget.id or ""
            if wid.startswith("nav-"):
                page = wid.replace("nav-", "")
                if page in PAGES:
                    self.current_page = page

    def action_goto_home(self) -> None:
        self.current_page = "home"

    def action_goto_features(self) -> None:
        self.current_page = "features"

    def action_goto_arch(self) -> None:
        self.current_page = "architecture"

    def action_goto_fair(self) -> None:
        self.current_page = "fairscore"

    def action_goto_compare(self) -> None:
        self.current_page = "comparison"

    def action_goto_vault(self) -> None:
        self.current_page = "vault"

    def action_goto_dao(self) -> None:
        self.current_page = "dao"

    def action_goto_flash(self) -> None:
        self.current_page = "flash"

    def action_next_page(self) -> None:
        idx = PAGES.index(self.current_page)
        self.current_page = PAGES[(idx + 1) % len(PAGES)]

    def action_prev_page(self) -> None:
        idx = PAGES.index(self.current_page)
        self.current_page = PAGES[(idx - 1) % len(PAGES)]


def run_dashboard():
    """Entry point for the dashboard TUI"""
    app = ColdstarApp()
    app.run()


if __name__ == "__main__":
    run_dashboard()
