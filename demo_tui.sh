#!/bin/bash
# Quick demo script for Coldstar TUI interfaces

echo "Coldstar Terminal UI Demo"
echo "========================="
echo ""
echo "Choose a demo:"
echo "1) Flash USB Interface"
echo "2) Vault Dashboard"
echo "3) Interactive Launcher"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "Launching Flash USB Interface..."
        python3 flash_usb_tui.py
        ;;
    2)
        echo "Launching Vault Dashboard..."
        python3 vault_dashboard_tui.py
        ;;
    3)
        echo "Launching Interactive Launcher..."
        python3 launch_tui.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
