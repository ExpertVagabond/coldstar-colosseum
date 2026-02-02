# Coldstar Terminal UI Guide

Beautiful terminal interfaces for Coldstar cold wallet operations.

## Installation

First, install the dependencies (including the new Textual framework):

```bash
cd coldstar
pip install -e .
```

Or install directly:

```bash
pip install textual rich questionary
```

## Quick Start

### Option 1: Interactive Launcher

```bash
python launch_tui.py
```

This will show a menu where you can choose:
- Flash USB Cold Wallet
- Vault Dashboard

### Option 2: Direct Launch

**USB Flashing Interface:**
```bash
python flash_usb_tui.py
```

**Vault Dashboard:**
```bash
python vault_dashboard_tui.py
```

## Features

### Flash USB Interface

- ✅ Step-by-step progress visualization (Formatting, Writing, Encrypting, Verifying)
- ✅ Real-time progress bars for each step
- ✅ Hardware ID display
- ✅ Overall progress tracking
- ✅ Safety controls (Abort, Eject)
- ✅ Keyboard shortcuts

**Keyboard Controls:**
- `ESC` - Abort flashing
- `x` - Abort and wipe drive
- `e` - Eject safely when complete
- `Ctrl+C` - Immediate abort

### Vault Dashboard

- ✅ Three-panel layout (Portfolio | Token Details | Send)
- ✅ Portfolio overview with SOL, USDC, and SPL tokens
- ✅ Token transaction history
- ✅ Risk warnings (transfer-hooks, etc.)
- ✅ Send interface with amount selection
- ✅ Fee estimation (Standard/Fast/Custom)
- ✅ Network status and sync info

**Keyboard Controls:**
- `Tab` / `Shift+Tab` - Navigate between panels
- `/` - Search tokens
- `r` - Refresh balances
- `s` - Quick send
- `q` - Quit

## Customization

You can customize the interfaces by modifying:

### Flash USB Interface (`flash_usb_tui.py`)

```python
# Customize device info
run_flash_ui(
    device_name="KIOXIA 32GB",
    device_path="/dev/sdb",
    device_info="1CD6-FFFF removable • SN:L4330..."
)
```

### Vault Dashboard (`vault_dashboard_tui.py`)

```python
# Customize vault settings
run_vault_dashboard(
    vault_name="usb-03",
    network="mainnet"  # or "devnet", "testnet"
)
```

## Integration with Existing Code

The TUI interfaces are designed to integrate with your existing coldstar code:

### Flash USB Integration

```python
from flash_usb_tui import FlashUSBApp

# In your flash_usb.py, replace CLI with TUI
def flash_device(device_path):
    app = FlashUSBApp(
        device_name=get_device_name(device_path),
        device_path=device_path,
        device_info=get_device_info(device_path)
    )
    app.run()
```

### Vault Dashboard Integration

```python
from vault_dashboard_tui import VaultDashboardApp
from src.wallet import load_wallet
from src.network import get_balance

# Connect to your wallet/network code
def launch_dashboard():
    wallet = load_wallet()
    app = VaultDashboardApp()
    # Pass wallet data to app
    app.run()
```

## Development

### Running in Development Mode

Enable Textual's development console for debugging:

```bash
textual console
```

In another terminal:

```bash
python flash_usb_tui.py
```

### Customizing Styles

Both interfaces use CSS-like styling through Textual. Edit the `CSS` property in each App class:

```python
class FlashUSBApp(App):
    CSS = """
    Screen {
        background: $surface;
    }
    /* Add your custom styles */
    """
```

## Screenshots

See the design mockups in the project root for reference.

## Next Steps

- [ ] Connect USB flashing UI to actual flash_usb.py logic
- [ ] Wire vault dashboard to src/wallet.py and src/network.py
- [ ] Add real-time balance updates
- [ ] Implement transaction signing flow
- [ ] Add QR code display in terminal
- [ ] Create settings panel
- [ ] Add multi-wallet support

## Troubleshooting

**TUI not displaying correctly:**
- Make sure your terminal supports 256 colors
- Use a modern terminal (iTerm2, Windows Terminal, etc.)
- Try resizing your terminal window

**Keyboard shortcuts not working:**
- Check if your terminal is capturing the keys
- Try alternative shortcuts listed in the footer

**Import errors:**
- Ensure all dependencies are installed: `pip install -e .`
- Check Python version: Python 3.11+ required

## License

MIT License - Same as Coldstar project
