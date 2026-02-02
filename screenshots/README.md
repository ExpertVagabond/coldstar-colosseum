# Coldstar TUI Screenshots & Previews

This directory contains various visualizations of the Coldstar terminal user interfaces.

## 📁 Files

### Static HTML Previews
- **flash_usb_preview.html** - Static preview of the Flash USB interface
- **vault_dashboard_preview.html** - Static preview of the Vault Dashboard

### Animated Previews
- **flash_usb_animated.html** - Fully animated Flash USB flashing process (20 second animation)
  - Shows progress bars filling in real-time
  - Steps completing one by one
  - Overall progress updating
  - Click "Replay" button to watch again

## 🎬 How to View

### Option 1: Open in Browser (Recommended)
```bash
# From the coldstar directory
open screenshots/flash_usb_preview.html
open screenshots/vault_dashboard_preview.html
open screenshots/flash_usb_animated.html
```

Or simply double-click the HTML files in Finder.

### Option 2: View Live TUI
For the REAL interactive experience with working keyboard shortcuts:

```bash
# Flash USB interface
python3 flash_usb_tui.py

# Vault Dashboard
python3 vault_dashboard_tui.py

# Interactive launcher
python3 launch_tui.py
```

## 📸 Creating Your Own Screenshots

### macOS
1. Run the TUI in Terminal:
   ```bash
   python3 flash_usb_tui.py
   ```

2. Press `Cmd + Shift + 4` then `Space`

3. Click on the Terminal window to capture

### Linux
```bash
# Using GNOME
gnome-screenshot -w

# Using scrot
scrot -u
```

### Windows
```bash
# Using Windows Terminal
# Press Ctrl + Shift + S for screenshot
```

## 🎨 Features Shown

### Flash USB Interface
- ✅ Blue header with title
- 🔒 Yellow-bordered device info panel
- 📊 4-step progress visualization:
  - Step 1: Formatting (complete)
  - Step 2: Writing (in progress with animated bar)
  - Step 3: Encrypting (pending)
  - Step 4: Verifying (pending)
- 🔐 Hardware ID display
- ⚡ Overall progress bar
- ⚠️ Safety warnings
- ⌨️ Keyboard shortcuts (ESC, X, E)

### Vault Dashboard
- 📊 Three-panel layout:
  - **Left**: Portfolio with token balances
  - **Middle**: Token details & transaction history
  - **Right**: Send interface with amount/fee selection
- 🔝 Status bar showing:
  - Vault name (usb-03)
  - Mode (OFFLINE SIGNING)
  - Network (mainnet)
  - Last sync time
  - Total portfolio value ($12,431)
  - 24h change (+1.8%)
- ⚠️ Risk warnings for tokens
- 💰 Fee estimation
- ⌨️ Keyboard navigation hints

## 🛠️ Technical Details

### Technologies Used
- **Textual** - Modern Python TUI framework
- **Rich** - Terminal text styling
- **HTML/CSS** - For static previews
- **CSS Animations** - For animated previews

### File Sizes
- Static HTML: ~5-10 KB each
- Animated HTML: ~10-15 KB

### Browser Compatibility
All HTML previews work in:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

## 📝 Regenerating Screenshots

To regenerate all screenshots:

```bash
# Static previews
python3 create_screenshots.py

# Animated preview
python3 create_animated_preview.py
```

## 🎯 Next Steps

Want to customize the UI? Edit:
- `flash_usb_tui.py` - Flash USB interface code
- `vault_dashboard_tui.py` - Vault dashboard code

Want different colors or layouts? Modify the `CSS` property in each App class.

## 📄 License

MIT License - Same as Coldstar project
