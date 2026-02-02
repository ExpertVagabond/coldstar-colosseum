#!/bin/bash
# Record Coldstar TUI interfaces as animated SVGs

echo "Recording Coldstar TUI Animations..."
echo "======================================"

mkdir -p screenshots

# Record Flash USB interface
echo ""
echo "Recording Flash USB interface (10 seconds)..."
termtosvg record screenshots/flash_usb_animation.svg \
    --screen-geometry 80x24 \
    --command "python3 flash_usb_tui.py" \
    --max-frame-duration 100 &

FLASH_PID=$!
sleep 10
kill $FLASH_PID 2>/dev/null || true
wait $FLASH_PID 2>/dev/null || true

echo "✅ Created: screenshots/flash_usb_animation.svg"

# Record Vault Dashboard
echo ""
echo "Recording Vault Dashboard (10 seconds)..."
termtosvg record screenshots/vault_dashboard_animation.svg \
    --screen-geometry 120x30 \
    --command "python3 vault_dashboard_tui.py" \
    --max-frame-duration 100 &

VAULT_PID=$!
sleep 10
kill $VAULT_PID 2>/dev/null || true
wait $VAULT_PID 2>/dev/null || true

echo "✅ Created: screenshots/vault_dashboard_animation.svg"

echo ""
echo "======================================"
echo "✅ All recordings created!"
echo ""
echo "Open these files in your browser:"
echo "  - screenshots/flash_usb_animation.svg"
echo "  - screenshots/vault_dashboard_animation.svg"
