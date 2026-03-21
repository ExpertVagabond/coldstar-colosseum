#!/usr/bin/env python3
"""
Coldstar — Air-Gapped Cold Wallet
Chain selector: routes to Solana or Base CLI.
"""

import re
import sys

# ── Security: constants & validation ──────────────────────────────────
ALLOWED_FLAGS = {"--base", "-b", "--solana", "-s", "--help", "-h"}
MAX_ARGS = 10


def sanitize_error(err: Exception) -> str:
    """Sanitize error messages to prevent information leakage."""
    msg = str(err)
    msg = re.sub(r"/[^\s]+/", "[path]/", msg)
    msg = re.sub(r"(key|secret|seed|mnemonic)\s*[:=]\s*\S+", r"\1=[REDACTED]", msg, flags=re.IGNORECASE)
    return msg[:200]


def validate_args(argv: list[str]) -> None:
    """Validate CLI arguments against allowlist."""
    if len(argv) > MAX_ARGS:
        raise ValueError(f"Too many arguments (max {MAX_ARGS})")
    for arg in argv[1:]:
        if arg.startswith("-") and arg not in ALLOWED_FLAGS:
            raise ValueError(f"Unknown flag: {arg}")


from src.ui import console, select_menu_option, print_info


def main():
    try:
        validate_args(sys.argv)
    except ValueError as e:
        print(f"Error: {sanitize_error(e)}")
        sys.exit(1)

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
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {sanitize_error(e)}")
        sys.exit(1)
