#!/usr/bin/env python3
"""
Build Coldstar x FairScore demo video v2 — Realistic terminal mockups.

Uses Rich Console SVG export for pixel-perfect TUI rendering,
rsvg-convert for SVG→PNG, Pillow for macOS terminal chrome,
macOS `say` for voiceover, and ffmpeg for final assembly.
"""

import subprocess
import os
import sys
import tempfile

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.terminal_theme import TerminalTheme
from rich import box

from PIL import Image, ImageDraw, ImageFont

VIDEO_DIR = os.path.dirname(os.path.abspath(__file__))
SLIDES_DIR = os.path.join(VIDEO_DIR, "slides_v2")
AUDIO_DIR = os.path.join(VIDEO_DIR, "audio_v2")
OUTPUT = os.path.join(VIDEO_DIR, "coldstar-fairscore-demo-v2.mp4")

os.makedirs(SLIDES_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Canvas dimensions
WIDTH = 1920
HEIGHT = 1080
TITLEBAR_H = 44
PADDING = 40

# Colors
BG_COLOR = (13, 13, 13)        # #0d0d0d
TITLEBAR_COLOR = (38, 38, 38)  # #262626
TITLEBAR_TEXT = (160, 160, 160)
BRANDING_COLOR = (60, 60, 60)

# ─── Scene Definitions ───────────────────────────────────────────────

SCENES = []


def scene(title, duration, voiceover, accent="#ff00ff"):
    """Decorator to register a scene rendering function."""
    def decorator(func):
        SCENES.append({
            "title": title,
            "duration": duration,
            "voiceover": voiceover,
            "accent": accent,
            "render": func,
        })
        return func
    return decorator


# ─── Rich Rendering Helpers ──────────────────────────────────────────

def rich_to_png(render_func, out_path, console_width=100, title="coldstar — main.py"):
    """Render Rich content to PNG via SVG export."""
    c = Console(
        record=True,
        width=console_width,
        force_terminal=True,
        color_system="truecolor",
    )
    render_func(c)
    svg = c.export_svg(title=title, theme=TERMINAL_THEME)

    # Write SVG
    svg_path = out_path.replace(".png", ".svg")
    with open(svg_path, "w") as f:
        f.write(svg)

    # Convert to PNG at high DPI
    subprocess.run(
        ["rsvg-convert", "-w", "1760", "-o", out_path, svg_path],
        check=True, capture_output=True,
    )
    os.remove(svg_path)
    return out_path


# Custom dark terminal theme for Rich SVG export
TERMINAL_THEME = TerminalTheme(
    background=(13, 13, 13),
    foreground=(204, 204, 204),
    normal=[
        (13, 13, 13),       # black
        (255, 68, 68),      # red
        (68, 255, 136),     # green
        (255, 170, 0),      # yellow
        (88, 209, 235),     # blue
        (255, 0, 255),      # magenta
        (88, 209, 235),     # cyan
        (204, 204, 204),    # white
    ],
    bright=[
        (85, 85, 85),       # bright black
        (255, 102, 102),    # bright red
        (102, 255, 153),    # bright green
        (255, 204, 68),     # bright yellow
        (136, 221, 255),    # bright blue
        (255, 102, 255),    # bright magenta
        (136, 221, 255),    # bright cyan
        (255, 255, 255),    # bright white
    ],
)


def composite_terminal_frame(content_png_path, output_path, window_title="coldstar — main.py"):
    """Composite Rich-rendered content into a macOS terminal frame at 1920x1080."""
    # Create base canvas
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # Draw title bar
    draw.rectangle([0, 0, WIDTH, TITLEBAR_H], fill=TITLEBAR_COLOR)

    # Traffic light dots
    dot_y = TITLEBAR_H // 2
    dot_r = 7
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        x = 20 + i * 24
        draw.ellipse([x - dot_r, dot_y - dot_r, x + dot_r, dot_y + dot_r], fill=color)

    # Window title text
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 14)
    except (OSError, IOError):
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
        except (OSError, IOError):
            title_font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), window_title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, (TITLEBAR_H - 14) // 2), window_title,
              fill=TITLEBAR_TEXT, font=title_font)

    # Load content and crop Rich's built-in title bar to avoid double chrome
    content = Image.open(content_png_path)
    # Rich SVG export adds a full terminal chrome bar (~8% of height) — crop it off
    rich_titlebar_h = int(content.height * 0.09)
    if content.height > 200:  # safety check
        content = content.crop((0, rich_titlebar_h, content.width, content.height))

    # Scale content to fit within the frame
    max_w = WIDTH - PADDING * 2
    max_h = HEIGHT - TITLEBAR_H - PADDING * 2 - 30  # 30 for branding bar
    ratio = min(max_w / content.width, max_h / content.height, 1.0)

    if ratio < 1.0:
        new_w = int(content.width * ratio)
        new_h = int(content.height * ratio)
        content = content.resize((new_w, new_h), Image.LANCZOS)

    # Center content in the frame
    x = (WIDTH - content.width) // 2
    y = TITLEBAR_H + (max_h - content.height) // 2 + PADDING // 2
    canvas.paste(content, (x, y))

    # Bottom branding bar
    try:
        brand_font = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 13)
    except (OSError, IOError):
        brand_font = title_font
    branding = "coldstar.dev  |  X: @buildcoldstar  |  chainlabs.uno  |  FairScale Fairathon 2026"
    bbox = draw.textbbox((0, 0), branding, font=brand_font)
    bw = bbox[2] - bbox[0]
    draw.text(((WIDTH - bw) // 2, HEIGHT - 28), branding, fill=BRANDING_COLOR, font=brand_font)

    canvas.save(output_path, "PNG")
    return output_path


# ─── Scene 1: Title Card ────────────────────────────────────────────

@scene(
    "Title",
    12,
    "Coldstar is the first and only air-gapped Solana cold wallet with built-in "
    "reputation scoring. Every outbound transaction is checked against FairScale's "
    "FairScore API before it crosses the air gap. This is Coldstar times FairScore.",
    accent="#ff00ff",
)
def render_title(c):
    c.print()
    c.print()
    c.print("[bold magenta]   ╔═══════════════════════════════════════════════════╗[/]")
    c.print("[bold magenta]   ║                                                   ║[/]")
    c.print("[bold magenta]   ║[/]    [bold white]C O L D S T A R   ×   F A I R S C O R E[/]    [bold magenta]║[/]")
    c.print("[bold magenta]   ║                                                   ║[/]")
    c.print("[bold magenta]   ╚═══════════════════════════════════════════════════╝[/]")
    c.print()
    c.print("[bold white]     Reputation-Gated Air-Gapped Cold Wallet for Solana[/]")
    c.print()
    c.print("[dim]     STIE Member  •  chainlabs.uno  •  coldstar.dev[/]")
    c.print("[dim]     X: @buildcoldstar  •  Insta: @devsyrem[/]")
    c.print()
    c.print()
    c.print("[bold cyan]     FairScale Fairathon 2026  •  Colosseum Project #62[/]")
    c.print()


# ─── Scene 2: The Problem ───────────────────────────────────────────

@scene(
    "The Problem",
    15,
    "Cold wallets give you the best physical security in crypto. But they're completely "
    "blind to counterparty risk. You can carefully sign a transaction on your air-gapped "
    "device, only to send funds to a scam address. Once signed and broadcast, the funds "
    "are gone forever. The entire 1.2 billion dollar hardware wallet market has zero "
    "reputation intelligence.",
    accent="#ff4444",
)
def render_problem(c):
    c.print()
    panel = Panel(
        "[bold white]Cold wallets provide the best physical security.\n\n"
        "[bold red]But they are BLIND to counterparty risk.[/bold red]\n\n"
        "You can air-gap sign a transaction\n"
        "to a [bold red]SCAM ADDRESS[/bold red] and [bold red]lose everything[/bold red].\n\n"
        "[dim]$1.2B hardware wallet market[/dim]\n"
        "[bold red]has ZERO reputation layer.[/bold red]",
        title="[bold red]THE PROBLEM[/bold red]",
        border_style="red",
        padding=(1, 3),
        width=70,
    )
    c.print(panel)
    c.print()
    c.print("[dim red]  Every cold wallet today:[/]")
    c.print("[dim]    Ledger   → No reputation check[/]")
    c.print("[dim]    Trezor   → No reputation check[/]")
    c.print("[dim]    Keystone → No reputation check[/]")
    c.print("[bold red]    Coldstar → [bold green]FairScore gating ✓[/][/]")


# ─── Scene 3: The Solution ──────────────────────────────────────────

@scene(
    "Solution Overview",
    14,
    "Coldstar integrates FairScale's FairScore as a core gating mechanism. Before any "
    "transaction crosses the air gap for offline signing, the recipient's reputation "
    "score is checked. Bronze tier addresses, scores below 20, are hard blocked. "
    "Silver tier gets a soft warning requiring explicit confirmation. Gold, Platinum, "
    "and Diamond wallets get the green light. All checks happen before the point of "
    "no return.",
    accent="#00ff88",
)
def render_solution(c):
    c.print()
    c.print("[bold green]── THE SOLUTION: FAIRSCORE GATING ──[/]")
    c.print()
    c.print("  FairScore (0-100) checked [bold]BEFORE[/] every transaction")
    c.print()

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED,
        width=70,
        padding=(0, 1),
    )
    table.add_column("Tier", style="white", width=10)
    table.add_column("Score", width=8)
    table.add_column("Action", width=12)
    table.add_column("TX Limit", width=12)

    table.add_row("[red]Bronze[/]", "0-19", "[bold red]HARD BLOCK[/]", "[red]BLOCKED[/]")
    table.add_row("[yellow]Silver[/]", "20-39", "[bold yellow]SOFT WARNING[/]", "[yellow]10 SOL[/]")
    table.add_row("[green]Gold[/]", "40-59", "[green]PROCEED[/]", "100 SOL")
    table.add_row("[cyan]Platinum[/]", "60-79", "[cyan]PROCEED[/]", "500 SOL")
    table.add_row("[magenta]Diamond[/]", "80-100", "[magenta]PROCEED[/]", "[green]Unlimited[/]")
    c.print(table)
    c.print()
    c.print("  All checks happen [bold]BEFORE[/] the point of no return.")


# ─── Scene 4: Main Menu ─────────────────────────────────────────────

@scene(
    "Wallet Menu",
    12,
    "Here's the Coldstar command-line interface. It's a full terminal wallet with "
    "Jupiter DEX integration, Pyth price feeds, and wallet backup. Notice the F "
    "option: Check FairScore Reputation. This is where reputation becomes a first-class "
    "citizen in the wallet experience.",
    accent="#58d1eb",
)
def render_menu(c):
    c.print()
    c.print("[bold cyan]╔═══════════════════════════════════════════╗[/]")
    c.print("[bold cyan]║[/]  [bold white]COLDSTAR[/]  [dim]v1.1.0[/]  [green]●[/] Connected  [dim]devnet[/]  [bold cyan]║[/]")
    c.print("[bold cyan]╚═══════════════════════════════════════════╝[/]")
    c.print()
    c.print("[bold cyan]── WALLET STATUS ──[/]")
    c.print("  [dim]Public Key:[/]  [cyan]7xK9m...Uf4R[/]")
    c.print("  [dim]Balance:[/]     [bold green]3.2546 SOL[/]")
    c.print("  [dim]USD Value:[/]   [green]≈ $476.80 (SOL @ $146.52)[/]")
    c.print("  [dim]Reputation:[/]  [magenta][***] EXCELLENT (92/100)[/]")
    c.print()
    c.print("[bold cyan]── WALLET OPERATIONS ──[/]")
    c.print()
    c.print("  [white]1.[/] Check Balance")
    c.print("  [white]2.[/] Create Unsigned Transaction")
    c.print("  [white]3.[/] Sign on Air-Gapped Device")
    c.print("  [white]4.[/] Broadcast Signed Transaction")
    c.print("  [white]5.[/] View Token Accounts")
    c.print("  [white]6.[/] View Transaction History")
    c.print("  [white]7.[/] Backup / Restore Wallet")
    c.print("  [white]8.[/] Request Devnet Airdrop")
    c.print("  [white]9.[/] Network Status")
    c.print("  [yellow]J.[/] Jupiter Swap (Create Unsigned Swap)")
    c.print("  [bold magenta]F.[/] [bold magenta]Check FairScore Reputation[/]  [dim]← NEW[/]")
    c.print("  [dim]A.[/] Unmount USB / Switch Device")
    c.print("  [dim]0.[/] Exit")
    c.print()
    c.print("  [dim]Select an option:[/] [bold white]F[/]█")


# ─── Scene 5: FairScore Lookup — Jupiter Wallet ─────────────────────

@scene(
    "FairScore Lookup",
    15,
    "When we look up the Jupiter aggregator wallet, FairScore returns a score of "
    "34.2 out of 100. That places it in the Silver tier with three badges: "
    "L-S-T Staker, SOL Maxi, and No Instant Dumps. In Coldstar, this triggers a "
    "soft warning. The user sees the full reputation profile and must explicitly "
    "confirm before creating any transaction to this address.",
    accent="#ffaa00",
)
def render_fairscore_lookup(c):
    c.print()
    c.print("[bold cyan]── FAIRSCORE REPUTATION LOOKUP ──[/]")
    c.print()
    c.print("  [dim]Enter a Solana wallet address to check its reputation.[/]")
    c.print()
    c.print("  [dim]Address:[/] [cyan]JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN[/]")
    c.print()
    c.print("  [dim]Querying FairScale API...[/]")
    c.print()

    # Build the verbose reputation panel
    table = Table.grid(padding=(0, 1))
    table.add_column(style="dim", width=14)
    table.add_column(style="white")

    table.add_row("Address:", "[cyan]JUPyiwrYJF...sDvCN[/]")
    table.add_row("Reputation:", "[yellow](!) LOW TRUST[/]")
    table.add_row("Tier:", "Silver (2/5)")
    table.add_row("FairScore:", "34.2/100")
    table.add_row("TX Limit:", "[yellow]10 SOL max[/]")
    table.add_row("Badges:", "[cyan]LST Staker[/]  [cyan]SOL Maxi[/]  [cyan]No Instant Dumps[/]")
    table.add_row("Status:", "[yellow]New or unverified wallet - proceed with caution[/]")

    panel = Panel(
        table,
        title="[bold cyan]FairScore Reputation[/]",
        border_style="yellow",
        padding=(1, 2),
        width=70,
    )
    c.print(panel)
    c.print()
    c.print("  [dim]Show FairScore tier legend?[/] [bold white]Yes[/]")


# ─── Scene 6: Tier Legend Table ──────────────────────────────────────

@scene(
    "Tier Legend",
    13,
    "The tier system has five levels. Bronze is untrusted — transactions are hard "
    "blocked. Silver is low trust with soft warnings and a 10 SOL limit. Gold is "
    "trusted at 100 SOL. Platinum is high trust at 500 SOL. And Diamond wallets "
    "have unlimited transaction capacity. Each tier maps directly to FairScale's "
    "API response.",
    accent="#58d1eb",
)
def render_tier_legend(c):
    c.print()
    table = Table(
        title="[bold cyan]FairScore Reputation Tiers[/]",
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED,
        padding=(0, 1),
    )
    table.add_column("Tier", style="white", width=6)
    table.add_column("API Tier", style="bold", width=10)
    table.add_column("Label", style="bold", width=14)
    table.add_column("Score", width=8)
    table.add_column("Action", width=8)
    table.add_column("TX Limit", width=12)
    table.add_column("Description", style="dim")

    table.add_row("1", "[red]bronze[/]", "[red]UNTRUSTED[/]", "0-19",
                   "[red]BLOCK[/]", "[red]BLOCKED[/]",
                   "High-risk wallet")
    table.add_row("2", "[yellow]silver[/]", "[yellow]LOW TRUST[/]", "20-39",
                   "[yellow]WARN[/]", "[yellow]10 SOL[/]",
                   "Unverified wallet")
    table.add_row("3", "[green]gold[/]", "[green]TRUSTED[/]", "40-59",
                   "[green]ALLOW[/]", "100 SOL",
                   "Verified on-chain")
    table.add_row("4", "[cyan]platinum[/]", "[cyan]HIGH TRUST[/]", "60-79",
                   "[cyan]ALLOW[/]", "500 SOL",
                   "Strong reputation")
    table.add_row("5", "[magenta]diamond[/]", "[magenta]EXCELLENT[/]", "80-100",
                   "[magenta]ALLOW[/]", "[green]Unlimited[/]",
                   "Top-tier entity")

    c.print(table)
    c.print()


# ─── Scene 7: Bronze BLOCK ──────────────────────────────────────────

@scene(
    "Bronze Block",
    16,
    "Now watch what happens when we try to send SOL to a bronze-tier wallet. "
    "Coldstar queries the FairScore API and gets back a score of 12.3 — that's "
    "untrusted, bronze tier. The transaction is immediately hard blocked. You "
    "physically cannot send funds to this address. The rich terminal panel shows "
    "the untrusted status, the score, and the blocked transaction limit. "
    "This is the core value proposition: protecting your funds before the point "
    "of no return.",
    accent="#ff4444",
)
def render_bronze_block(c):
    c.print()
    c.print("[bold cyan]── CREATE UNSIGNED TRANSACTION ──[/]")
    c.print()
    c.print("  [dim]From:[/]  [cyan]7xK9m...Uf4R[/]  [dim](3.2546 SOL)[/]")
    c.print("  [dim]To:[/]    [cyan]5xGhR2fK9mNpvTqW8Lk3jY6bCdZ4eA7nH...Tf8Y[/]")
    c.print()
    c.print("[bold cyan]── FAIRSCORE REPUTATION CHECK ──[/]")
    c.print("  [dim]Checking reputation for[/] [cyan]5xGhR2fK9m...Tf8Y[/]")
    c.print()

    # Reputation panel
    table = Table.grid(padding=(0, 1))
    table.add_column(style="dim", width=14)
    table.add_column(style="white")

    table.add_row("Address:", "[cyan]5xGhR2fK9m...Tf8Y[/]")
    table.add_row("Reputation:", "[bold red]!!! UNTRUSTED[/]")
    table.add_row("Tier:", "Bronze (1/5)")
    table.add_row("FairScore:", "12.3/100")
    table.add_row("TX Limit:", "[bold red]BLOCKED[/]")
    table.add_row("Status:", "[red]High-risk wallet - likely sybil or malicious[/]")

    panel = Panel(
        table,
        title="[bold cyan]FairScore Reputation[/]",
        border_style="red",
        padding=(1, 2),
        width=70,
    )
    c.print(panel)
    c.print()
    c.print("  [bold red]✗ TRANSACTION BLOCKED[/]")
    c.print("  [red]Recipient has UNTRUSTED reputation (FairScore: 12.3, Tier: bronze)[/]")
    c.print("  [yellow]⚠ Coldstar will not create transactions to untrusted wallets.[/]")


# ─── Scene 8: Silver Warning ────────────────────────────────────────

@scene(
    "Silver Warning",
    14,
    "For silver-tier wallets, Coldstar takes a softer approach. Instead of a hard "
    "block, you see a warning with the full reputation profile. The wallet scored "
    "34.2, silver tier. You must explicitly confirm before Coldstar will create "
    "the transaction. This gives you informed consent — you see the risk before "
    "committing.",
    accent="#ffaa00",
)
def render_silver_warn(c):
    c.print()
    c.print("[bold cyan]── FAIRSCORE REPUTATION CHECK ──[/]")
    c.print("  [dim]Checking reputation for[/] [cyan]JUPyiwrYJF...sDvCN[/]")
    c.print()

    table = Table.grid(padding=(0, 1))
    table.add_column(style="dim", width=14)
    table.add_column(style="white")

    table.add_row("Address:", "[cyan]JUPyiwrYJF...sDvCN[/]")
    table.add_row("Reputation:", "[yellow](!) LOW TRUST[/]")
    table.add_row("Tier:", "Silver (2/5)")
    table.add_row("FairScore:", "34.2/100")
    table.add_row("TX Limit:", "[yellow]10 SOL max[/]")
    table.add_row("Badges:", "[cyan]LST Staker[/]  [cyan]SOL Maxi[/]")

    panel = Panel(
        table,
        title="[bold cyan]FairScore Reputation[/]",
        border_style="yellow",
        padding=(1, 2),
        width=70,
    )
    c.print(panel)
    c.print()
    c.print("  [bold yellow]⚠ WARNING: Recipient has LOW TRUST reputation[/]")
    c.print("  [yellow]⚠ FairScore: 34.2/100 — proceed with caution[/]")
    c.print()
    c.print("  [dim]Continue with this recipient?[/] [bold yellow][y/N]:[/] [bold white]y[/]█")
    c.print()
    c.print("  [green]✓ Continuing — enter transaction details[/]")
    c.print()
    c.print("  [dim]Enter amount to send (SOL):[/] [bold white]2.5[/]")


# ─── Scene 9: Vault Dashboard ───────────────────────────────────────

@scene(
    "Vault Dashboard",
    15,
    "The vault dashboard is a full terminal UI built with Textual. In the portfolio "
    "panel on the left, notice the reputation column — the Rep column. Each token's "
    "issuer has a reputation indicator. SOL and USDC show triple-star excellent. "
    "Bitcoin shows double-plus high trust. Raydium shows plus for trusted. "
    "Unknown tokens show the warning icon. And the flagged token at the bottom "
    "shows triple-bang untrusted. Reputation is embedded in the portfolio view itself.",
    accent="#58d1eb",
)
def render_dashboard(c):
    c.print()
    c.print("[bold cyan]COLDSTAR[/] • Vault: [yellow]usb-03[/] • [green]OFFLINE SIGNING[/] • RPC: [cyan]mainnet[/]")
    c.print("[dim]Last sync [cyan]2m ago[/dim] • [yellow]0[/] warnings • Total [bold green]$12,431[/bold green] • 24h [green]+1.8%[/green]")
    c.print()

    # Portfolio panel with reputation column
    port_table = Table.grid(padding=(0, 1))
    port_table.add_column("", width=3)   # icon
    port_table.add_column("", width=8)   # symbol
    port_table.add_column("", justify="right", width=12)  # amount
    port_table.add_column("", justify="right", width=10)  # value
    port_table.add_column("", justify="center", width=6)  # rep

    port_table.add_row("[magenta]◎[/]", "[bold white]SOL[/]", "3.2546", "[green]476.80[/]", "[magenta][***][/]")
    port_table.add_row("[cyan]>◉[/]", "[bold white]USDC[/]", "1,025.0000", "[green]1,025.00[/]", "[magenta][***][/]")
    port_table.add_row("[yellow]฿[/]", "[white]BTC[/]", "0.0125", "[green]600.50[/]", "[cyan][++][/]")
    port_table.add_row("[yellow]⚡[/]", "[white]RAY[/]", "500.0000", "[green]85.00[/]", "[green][+][/]")
    port_table.add_row("[cyan]◆[/]", "[white]XYZ[/]", "10.0000", "[red]0.00 F[/]", "[yellow](!)[/]")
    port_table.add_row("[red]⚠[/]", "[red]Unknown[/]", "10.0000", "[red]0.00 F[/]", "[red]!!![/]")

    portfolio_panel = Panel(
        port_table,
        title="[bold]Portfolio[/]",
        border_style="cyan",
        padding=(1, 1),
    )

    # Token details panel
    detail_content = (
        "[dim]Mint:[/] [cyan]EPjFW...DeF2[/] • Decimals: [yellow]6[/] • [green]✓ Verified[/]\n\n"
        "- [green]Received[/] 500.00 USDC    [dim]30m ago[/]\n"
        "- [yellow]Sent[/] 250.00 USDC        [dim]2h ago[/]\n"
        "- [green]Received[/] 775.00 USDC    [dim]1d ago[/]\n\n"
        "[bold yellow]Risk Notes:[/]\n"
        "• Transfer-hook enabled\n"
        "• Direct transfer • Swap then send"
    )
    detail_panel = Panel(
        detail_content,
        title="[bold]USDC Details[/]",
        border_style="cyan",
        padding=(1, 1),
    )

    # Send panel
    send_content = (
        "To:     [cyan]4xp...Tf8Y[/] [dim]v[/]\n\n"
        "Amount: [bold white]100.00[/]  [dim][a max] [25% 50% 75% 100%][/]\n\n"
        "Fee:    [bold green][Standard][/]  [dim]Fast  Custom[/]\n"
        "        [dim]~0.00005 SOL • 3.15 SOL left[/]\n\n"
        "[bold]Review:[/]\n"
        "  [bold]USDC[/] [white]100.00[/]\n"
        "  [bold]To:[/]  [cyan]4xp...Tf8Y[/]\n\n"
        "[bold green][ENTER] Send[/] • [dim][x] Cancel[/]"
    )
    send_panel = Panel(
        send_content,
        title="[bold]Send USDC[/]",
        border_style="cyan",
        padding=(1, 1),
    )

    # Layout: print all three panels (Rich doesn't do columns easily in record mode)
    c.print(portfolio_panel)
    c.print()

    # Show details and send side by side as text
    detail_table = Table.grid(padding=(0, 2))
    detail_table.add_column(width=45)
    detail_table.add_column(width=45)
    detail_table.add_row(detail_panel, send_panel)
    c.print(detail_table)


# ─── Scene 10: Architecture ─────────────────────────────────────────

@scene(
    "Architecture",
    14,
    "Here's the architecture. The online device handles all FairScore API calls, "
    "Jupiter swaps, and Pyth price feeds. Transactions are transferred via QR code "
    "to the air-gapped USB device running Alpine Linux. The offline device signs "
    "with Ed25519 and returns the signature via QR. FairScore metadata is embedded "
    "in the QR payload so users can verify reputation on the offline screen before "
    "signing.",
    accent="#58d1eb",
)
def render_architecture(c):
    c.print()
    c.print("[bold cyan]── ARCHITECTURE ──[/]")
    c.print()
    c.print("  [bold white]ONLINE DEVICE[/]                        [bold white]AIR-GAPPED USB[/]")
    c.print("  [cyan]┌──────────────────────┐[/]  [magenta]QR[/]   [cyan]┌──────────────────────┐[/]")
    c.print("  [cyan]│[/] [green]FairScore API[/]        [cyan]│[/] ───→ [cyan]│[/] [yellow]Alpine Linux[/]         [cyan]│[/]")
    c.print("  [cyan]│[/] [green]Jupiter DEX[/]          [cyan]│[/]      [cyan]│[/] [yellow]Ed25519 Signing[/]      [cyan]│[/]")
    c.print("  [cyan]│[/] [green]Pyth Oracles[/]         [cyan]│[/] ←─── [cyan]│[/] [yellow]Key Storage[/]          [cyan]│[/]")
    c.print("  [cyan]│[/] [green]Rich Terminal UI[/]      [cyan]│[/]  [magenta]QR[/]   [cyan]│[/] [red]Offline Only[/]          [cyan]│[/]")
    c.print("  [cyan]└──────────┬───────────┘[/]      [cyan]└──────────────────────┘[/]")
    c.print("             [cyan]│[/]")
    c.print("       [bold cyan]Solana Mainnet[/]")
    c.print()
    c.print("  [bold magenta]FairScore flow:[/]")
    c.print("  [dim]1.[/] User enters recipient address")
    c.print("  [dim]2.[/] Online device queries FairScale API")
    c.print("  [dim]3.[/] Score embedded in QR payload")
    c.print("  [dim]4.[/] Offline device displays score for verification")
    c.print("  [dim]5.[/] User confirms → signs → returns signature via QR")


# ─── Scene 11: 6 Integration Points ─────────────────────────────────

@scene(
    "Integration Points",
    16,
    "Coldstar has six distinct FairScore integration points. Transaction gating "
    "blocks or warns before the air gap. Dynamic transfer limits scale with "
    "reputation. DAO governance weights votes by FairScore. Jupiter swap screening "
    "checks token contracts. The vault dashboard shows reputation badges inline. "
    "And MCP agent gates create an autonomy gradient where AI agents get permissions "
    "based on wallet reputation. FairScore is not decorative. It's a core gating "
    "mechanism that determines whether transactions can proceed.",
    accent="#7B2FBE",
)
def render_integration_points(c):
    c.print()
    c.print("[bold magenta]── 6 FAIRSCORE INTEGRATION POINTS ──[/]")
    c.print()

    points = [
        ("1", "Transaction Gating", "Block/warn before air-gap crossing", "red"),
        ("2", "Dynamic Limits", "Reputation-scaled SOL amounts per tier", "yellow"),
        ("3", "DAO Governance", "Vote weight multiplied by FairScore", "green"),
        ("4", "Jupiter Screening", "Token contract reputation before swap", "cyan"),
        ("5", "Dashboard Badges", "Reputation icons in portfolio panel", "magenta"),
        ("6", "MCP Agent Gates", "AI agent autonomy gradient by tier", "blue"),
    ]

    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED,
        padding=(0, 2),
        width=80,
    )
    table.add_column("#", style="white", width=3)
    table.add_column("Integration", style="bold white", width=22)
    table.add_column("Description", style="dim")

    for num, name, desc, color in points:
        table.add_row(num, f"[{color}]{name}[/]", desc)

    c.print(table)
    c.print()
    c.print("  [bold white]FairScore is NOT decorative.[/]")
    c.print("  [bold magenta]It is a CORE GATING MECHANISM.[/]")
    c.print()
    c.print("  [dim]Implementation:[/] [cyan]src/fairscore_integration.py[/] [dim](341 lines)[/]")
    c.print("  [dim]Config:[/]         [cyan]config.py[/] [dim](FAIRSCORE_ENABLED, MIN_TIER)[/]")
    c.print("  [dim]Gating:[/]         [cyan]main.py[/] [dim](7 edit points in transaction flow)[/]")


# ─── Scene 12: Live API Demo ────────────────────────────────────────

@scene(
    "Live API",
    14,
    "Here's a real API response from FairScale. We query the score endpoint with the "
    "Jupiter aggregator wallet address. The response includes the fairscore of 34.2, "
    "the silver tier, and three reputation badges. In Coldstar, this raw response is "
    "parsed, cached for 5 minutes, and displayed in the rich terminal panel you saw "
    "earlier.",
    accent="#ffaa00",
)
def render_live_api(c):
    c.print()
    c.print("[bold cyan]── LIVE API RESPONSE ──[/]")
    c.print()
    c.print("  [dim]$[/] [white]curl -H 'fairkey: zpka_***' \\[/]")
    c.print("  [white]  'https://api2.fairscale.xyz/score?wallet=JUPyiwrY...'[/]")
    c.print()

    api_content = (
        '[white]{[/]\n'
        '  [cyan]"wallet"[/]: [green]"JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"[/],\n'
        '  [cyan]"fairscore"[/]: [yellow]34.2[/],\n'
        '  [cyan]"tier"[/]: [green]"silver"[/],\n'
        '  [cyan]"badges"[/]: [\n'
        '    { [cyan]"label"[/]: [green]"LST Staker"[/] },\n'
        '    { [cyan]"label"[/]: [green]"SOL Maxi"[/] },\n'
        '    { [cyan]"label"[/]: [green]"No Instant Dumps"[/] }\n'
        '  ],\n'
        '  [cyan]"features"[/]: {\n'
        '    [cyan]"hasStaking"[/]: [yellow]true[/],\n'
        '    [cyan]"hasDeFi"[/]: [yellow]true[/],\n'
        '    [cyan]"hasNFTs"[/]: [yellow]false[/]\n'
        '  }\n'
        '[white]}[/]'
    )

    panel = Panel(
        api_content,
        title="[bold]GET /score?wallet=JUP...[/]",
        border_style="yellow",
        padding=(1, 2),
        width=70,
    )
    c.print(panel)
    c.print()
    c.print("  [dim]Coldstar action:[/] [bold yellow]⚠ WARNING — Confirm to proceed[/]")


# ─── Scene 13: Business Model + CTA ─────────────────────────────────

@scene(
    "CTA",
    12,
    "Coldstar is live at coldstar.dev. The code is open source on GitHub. "
    "Follow build coldstar on X. STIE member, chainlabs.uno. "
    "The future of cold storage is intelligent. Thank you.",
    accent="#ff00ff",
)
def render_cta(c):
    c.print()
    c.print("[bold magenta]   ╔═══════════════════════════════════════════════════╗[/]")
    c.print("[bold magenta]   ║[/]              [bold white]T R Y   C O L D S T A R[/]              [bold magenta]║[/]")
    c.print("[bold magenta]   ╚═══════════════════════════════════════════════════╝[/]")
    c.print()
    c.print("  [bold white]Live:[/]      [cyan]coldstar.dev/colosseum[/]")
    c.print()
    c.print("  [bold white]GitHub:[/]    [cyan]ExpertVagabond/coldstar-colosseum[/]")
    c.print()
    c.print("  [bold white]X:[/]         [cyan]@buildcoldstar[/]")
    c.print("  [bold white]Insta:[/]     [cyan]@devsyrem[/]")
    c.print()
    c.print("  [bold white]STIE Member[/]  •  [cyan]chainlabs.uno[/]")
    c.print()
    c.print('  [bold white italic]"The future of cold storage is intelligent."[/]')
    c.print()
    c.print("  [dim]FairScale Fairathon 2026  •  Colosseum Project #62[/]")
    c.print("  [dim]STIE Member  •  chainlabs.uno[/]")
    c.print()


# ─── Video Assembly Pipeline ─────────────────────────────────────────

def generate_voiceover(idx, text, duration):
    """Generate voiceover audio using macOS say command."""
    aiff_path = os.path.join(AUDIO_DIR, f"vo_{idx:02d}.aiff")
    wav_path = os.path.join(AUDIO_DIR, f"vo_{idx:02d}.wav")

    word_count = len(text.split())
    target_wpm = max(140, min(200, (word_count / (duration - 1)) * 60))
    rate = int(target_wpm * 1.1)

    subprocess.run(
        ["say", "-v", "Daniel", "-r", str(rate), "-o", aiff_path, text],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-i", aiff_path, "-ar", "44100", "-ac", "1", wav_path],
        check=True, capture_output=True,
    )
    os.remove(aiff_path)
    return wav_path


def generate_background_music(total_duration):
    """Generate faint ambient background music — warm pad with subtle movement."""
    music_path = os.path.join(AUDIO_DIR, "bgm.wav")

    # Layer multiple harmonics for a warm ambient pad:
    # A2 (110Hz) fundamental, E3 (165Hz) fifth, A1 (55Hz) sub-bass,
    # C#3 (138.6Hz) major third, A3 (220Hz) octave
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=110:duration={total_duration}",
        "-f", "lavfi", "-i", f"sine=frequency=165:duration={total_duration}",
        "-f", "lavfi", "-i", f"sine=frequency=55:duration={total_duration}",
        "-f", "lavfi", "-i", f"sine=frequency=138.6:duration={total_duration}",
        "-f", "lavfi", "-i", f"sine=frequency=220:duration={total_duration}",
        "-filter_complex",
        # Mix at very low volumes for faint ambient feel
        f"[0]volume=0.012[a];"
        f"[1]volume=0.008[b];"
        f"[2]volume=0.006[d];"
        f"[3]volume=0.005[e];"
        f"[4]volume=0.004[f];"
        f"[a][b][d][e][f]amix=inputs=5:duration=longest,"
        # Warm filtering: cut harsh highs, keep body
        f"lowpass=f=400,highpass=f=40,"
        # Gentle fade in/out
        f"afade=t=in:st=0:d=5,afade=t=out:st={total_duration-5}:d=5[out]",
        "-map", "[out]",
        "-ar", "44100", "-ac", "1",
        music_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return music_path


def build_video():
    """Main pipeline: render slides → voiceover → assemble."""
    print("=== Coldstar x FairScore Demo Video v2 ===")
    print(f"    {len(SCENES)} scenes, Rich terminal mockups\n")

    # Step 1: Render terminal mockup frames
    print("1/4  Rendering terminal frames...")
    slide_paths = []
    for i, scene_data in enumerate(SCENES):
        content_png = os.path.join(SLIDES_DIR, f"content_{i:02d}.png")
        final_png = os.path.join(SLIDES_DIR, f"slide_{i:02d}.png")

        rich_to_png(
            scene_data["render"],
            content_png,
            console_width=90,
            title=f"coldstar — {scene_data['title'].lower()}",
        )

        composite_terminal_frame(
            content_png, final_png,
            window_title=f"coldstar — {scene_data['title'].lower()}",
        )

        os.remove(content_png)
        slide_paths.append(final_png)
        print(f"     [{i+1}/{len(SCENES)}] {scene_data['title']}")

    # Step 2: Generate voiceovers
    print("\n2/4  Generating voiceovers...")
    vo_paths = []
    for i, scene_data in enumerate(SCENES):
        path = generate_voiceover(i, scene_data["voiceover"], scene_data["duration"])
        vo_paths.append(path)
        print(f"     [{i+1}/{len(SCENES)}] {len(scene_data['voiceover'])} chars")

    # Step 3: Background music
    total_duration = sum(s["duration"] for s in SCENES)
    print(f"\n3/4  Generating background music ({total_duration}s)...")
    bgm_path = generate_background_music(total_duration)

    # Step 4: Assemble video
    print("\n4/4  Assembling final video...")

    # Create concat file
    concat_path = os.path.join(VIDEO_DIR, "concat_v2.txt")
    with open(concat_path, "w") as f:
        for i, scene_data in enumerate(SCENES):
            f.write(f"file 'slides_v2/slide_{i:02d}.png'\n")
            f.write(f"duration {scene_data['duration']}\n")
        f.write(f"file 'slides_v2/slide_{len(SCENES)-1:02d}.png'\n")

    # Concatenate voiceovers with padding
    vo_concat_path = os.path.join(AUDIO_DIR, "vo_all.wav")
    filter_parts = []
    input_args = []
    for i, scene_data in enumerate(SCENES):
        input_args.extend(["-i", vo_paths[i]])
        filter_parts.append(f"[{i}]apad=whole_dur={scene_data['duration']}[a{i}]")

    concat_labels = "".join(f"[a{i}]" for i in range(len(SCENES)))
    filter_parts.append(f"{concat_labels}concat=n={len(SCENES)}:v=0:a=1[voall]")
    filter_str = ";".join(filter_parts)

    cmd = (
        ["ffmpeg", "-y"]
        + input_args
        + ["-filter_complex", filter_str, "-map", "[voall]",
           "-ar", "44100", "-ac", "1", vo_concat_path]
    )
    subprocess.run(cmd, check=True, capture_output=True)

    # Final assembly
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_path,
        "-i", vo_concat_path,
        "-i", bgm_path,
        "-filter_complex",
        "[1][2]amix=inputs=2:duration=first:dropout_transition=3[audio]",
        "-map", "0:v",
        "-map", "[audio]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT,
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    os.remove(concat_path)

    # Report
    duration_check = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", OUTPUT],
        capture_output=True, text=True,
    )
    final_duration = float(duration_check.stdout.strip())
    file_size = os.path.getsize(OUTPUT) / 1024 / 1024

    print(f"\n=== DONE ===")
    print(f"Output:   {OUTPUT}")
    print(f"Duration: {final_duration:.1f}s ({final_duration/60:.1f} min)")
    print(f"Size:     {file_size:.1f} MB")
    print(f"Scenes:   {len(SCENES)}")
    print(f"Quality:  CRF 20, 1920x1080, 30fps, AAC 192k")


if __name__ == "__main__":
    build_video()
