#!/usr/bin/env python3
"""Capture screenshots of each Coldstar TUI page as SVG and PNG"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from coldstar_tui import (
    HeroView, FeaturesView, ArchitectureView, FairScoreView,
    ComparisonView, VaultView, DAOView, FlashUSBView,
    PAGES, PAGE_LABELS
)
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

VIEWS = [
    ("home", "Home", HeroView),
    ("features", "Features", FeaturesView),
    ("architecture", "Architecture", ArchitectureView),
    ("fairscore", "FairScore", FairScoreView),
    ("comparison", "Comparison", ComparisonView),
    ("vault", "Vault", VaultView),
    ("dao", "DAO", DAOView),
    ("flash", "Flash USB", FlashUSBView),
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots", "tui")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def make_header():
    """Simulate the Textual header bar"""
    return Text.from_markup(
        "[on #243040] [/][on #243040] ⭘       "
        "              [bold]Coldstar[/] [dim]— Air-Gapped Solana Vault[/]"
        "                         [/]"
    )


def make_sidebar(active_page: str):
    """Simulate the sidebar navigation"""
    lines = [
        "",
        "  [bold cyan]COLDSTAR[/]",
        "  [dim]Dashboard[/]",
        "",
    ]
    for i, (key, label, _) in enumerate(VIEWS):
        if key == active_page:
            lines.append(f"  [bold cyan]▸ {label}[/]")
        else:
            lines.append(f"  [dim]  {label}[/]")
    lines.append("")
    return Panel(
        Text.from_markup("\n".join(lines)),
        border_style="#2a2a3a",
        width=22,
        padding=(0, 0),
    )


def make_footer():
    """Simulate the Textual footer"""
    return Text.from_markup(
        "[on #243040]  [bold]1[/] Home  [bold]2[/] Features  [bold]3[/] Architecture  "
        "[bold]4[/] FairScore  [bold]5[/] Comparison  [bold]6[/] Vault  "
        "[bold]7[/] DAO  [bold]8[/] Flash USB  [bold]q[/] Quit  [/]"
    )


def capture_page(page_key: str, page_label: str, view_cls):
    """Render a full TUI frame for one page"""
    console = Console(
        width=120,
        record=True,
        force_terminal=True,
        color_system="truecolor",
    )

    # Header
    console.print(make_header())

    # Sidebar + Content side by side
    sidebar = make_sidebar(page_key)
    view = view_cls()
    content = view.render()

    layout = Table.grid(padding=0)
    layout.add_column(width=24)
    layout.add_column()
    layout.add_row(sidebar, content)
    console.print(layout)

    # Footer
    console.print(make_footer())

    # Save SVG
    svg_path = os.path.join(OUTPUT_DIR, f"tui-{page_key}.svg")
    svg = console.export_svg(title=f"Coldstar TUI — {page_label}")
    with open(svg_path, "w") as f:
        f.write(svg)
    print(f"  Saved: {svg_path}")

    return svg_path


def main():
    print("Capturing Coldstar TUI screenshots...\n")

    for page_key, page_label, view_cls in VIEWS:
        print(f"  [{page_key}] {page_label}...")
        capture_page(page_key, page_label, view_cls)

    print(f"\nDone! {len(VIEWS)} screenshots saved to {OUTPUT_DIR}/")
    print("SVG files can be opened in any browser or converted to PNG with:")
    print(f"  for f in {OUTPUT_DIR}/*.svg; do")
    print('    /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\')
    print('      --headless --screenshot="${{f%.svg}}.png" --window-size=1400,900 "$f"')
    print("  done")


if __name__ == "__main__":
    main()
