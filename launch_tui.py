#!/usr/bin/env python3
"""
Coldstar TUI Launcher
Choose which terminal interface to launch
"""

import sys
from questionary import select


def main():
    """Launch TUI selector"""
    choice = select(
        "Which Coldstar interface would you like to launch?",
        choices=[
            "Coldstar Dashboard (Full UI)",
            "Flash USB Cold Wallet",
            "Vault Dashboard",
            "Exit"
        ]
    ).ask()

    if choice == "Coldstar Dashboard (Full UI)":
        from coldstar_tui import run_dashboard
        run_dashboard()

    elif choice == "Flash USB Cold Wallet":
        from flash_usb_tui import run_flash_ui
        run_flash_ui()

    elif choice == "Vault Dashboard":
        from vault_dashboard_tui import run_vault_dashboard
        run_vault_dashboard()

    elif choice == "Exit":
        print("Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
