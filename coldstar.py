#!/usr/bin/env python3
"""
Coldstar — Air-Gapped Cold Wallet
Chain selector: routes to Solana or Base CLI.
"""

import sys
from src.ui import console, select_menu_option, print_info


def main():
    # Allow direct chain selection via args
    if "--base" in sys.argv or "-b" in sys.argv:
        from base_cli import main as base_main
        base_main()
        return

    if "--solana" in sys.argv or "-s" in sys.argv:
        from main import main as solana_main
        solana_main()
        return

    # Interactive chain picker
    console.print()
    console.print("[bold white]COLDSTAR[/] — Air-Gapped Cold Wallet", justify="center")
    console.print("[dim]Select your chain:[/dim]", justify="center")
    console.print()

    choice = select_menu_option(
        [
            "1. Solana (Ed25519)",
            "2. Base / Coinbase L2 (secp256k1)",
        ],
        "Which chain?",
    )

    if not choice:
        sys.exit(0)

    num = choice.split(".")[0].strip()

    if num == "1":
        from main import main as solana_main
        solana_main()
    elif num == "2":
        from base_cli import main as base_main
        base_main()


if __name__ == "__main__":
    main()
