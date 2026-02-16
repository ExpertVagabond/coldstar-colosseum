# Coldstar - Air-Gapped Solana Cold Wallet

<p align="center">
  <img src="https://img.shields.io/badge/Solana-14F195?style=for-the-badge&logo=solana&logoColor=white" alt="Solana"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License"/>
</p>

A Python-based cold wallet that turns any USB drive into a hardware wallet. Your private keys **never** touch the internet.

## Features

- **Air-Gap Security** - Private keys generated and stored on offline devices only
- **USB Cold Wallet** - Flash any USB drive with minimal Alpine Linux OS (~50MB)
- **QR Code Transfer** - Easy transaction transfer via QR codes (no file copying needed)
- **Companion App** - Mobile-friendly PWA for creating transactions online
- **SPL Token Support** - Transfer USDC, USDT, BONK, JUP, and any SPL token
- **SOL Transfers** - Create, sign, and broadcast SOL transactions
- **Devnet Airdrop** - Test on devnet before using mainnet
- **🎨 NEW: Beautiful Terminal UI** - Modern TUI with progress bars, multi-panel layouts, and keyboard shortcuts

## 🎨 New Terminal UI

Coldstar now includes beautiful terminal interfaces for a modern CLI experience:

### Flash USB Interface
```bash
python flash_usb_tui.py
```
- Real-time progress visualization
- Step-by-step flashing (Format → Write → Encrypt → Verify)
- Hardware ID display
- Safety controls with keyboard shortcuts

### Vault Dashboard
```bash
python vault_dashboard_tui.py
```
- Three-panel layout: Portfolio | Token Details | Send
- Real-time balance tracking
- Transaction history
- Risk warnings for tokens
- Interactive send interface

**Quick Launch:**
```bash
python launch_tui.py  # Interactive menu
```

See [TUI_GUIDE.md](TUI_GUIDE.md) for full documentation.

## Quick Start

### 1. Install Dependencies

```bash
pip install rich questionary solana solders pynacl httpx aiofiles base58 qrcode textual
```

Or use the project file:
```bash
pip install -e .
```

### 2. Clone & Run

```bash
git clone https://github.com/ExpertVagabond/coldstar-colosseum.git
cd coldstar-colosseum
python main.py
```

### 3. Launch Companion App (Optional)

```bash
cd companion-app
python3 -m http.server 8080
# Open http://localhost:8080 on your phone or browser
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ONLINE DEVICE                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Companion App (PWA)                       │    │
│  │  • Check balance           • Create unsigned TX    │    │
│  │  • View token holdings     • Generate QR codes     │    │
│  │  • Broadcast signed TX     • SPL token support     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                    QR Code / USB Transfer
                              │
┌─────────────────────────────────────────────────────────────┐
│                  OFFLINE DEVICE (Air-Gapped)                │
│  ┌────────────────────────────────────────────────────┐    │
│  │              USB Cold Wallet                        │    │
│  │  • Generate keypair        • Sign transactions     │    │
│  │  • Store private key       • Display QR codes      │    │
│  │  • ZERO network access     • Alpine Linux (~50MB)  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Main CLI Menu

```
1. Detect USB Devices         - Scan connected USB drives
2. Flash Cold Wallet OS       - Create bootable offline wallet USB
3. Generate New Wallet        - Create Solana keypair (local)
4. View Wallet Information    - Check balance and address
5. Create Unsigned TX         - Build SOL transfer transaction
6. Sign Transaction (Offline) - Sign with private key
7. Broadcast Signed TX        - Send to Solana network
8. Request Devnet Airdrop     - Get test SOL
9. Network Status             - Check RPC connection
```

### QR Code Signing Workflow

```bash
# On air-gapped device - show wallet QR
python3 qr_sign.py --show-wallet

# On air-gapped device - sign transaction with QR output
python3 qr_sign.py
```

### Companion App Features

| Tab | Function |
|-----|----------|
| **Wallet** | Enter address, check SOL balance |
| **SOL** | Create unsigned SOL transfers with QR output |
| **Tokens** | View SPL tokens, create token transfers |
| **Send** | Upload signed TX file, broadcast to network |
| **More** | Network settings, devnet airdrops |

## Directory Structure

```
coldstar/
├── main.py                 # Main CLI application
├── qr_sign.py              # QR-based offline signing
├── flash_usb.py            # USB flashing tool
├── config.py               # Network configuration
├── src/
│   ├── wallet.py           # Keypair management
│   ├── transaction.py      # Transaction creation/signing
│   ├── network.py          # Solana RPC client
│   ├── token_transfer.py   # SPL token support
│   ├── qr_transfer.py      # QR code generation
│   ├── usb.py              # USB device detection
│   ├── iso_builder.py      # Bootable ISO creation
│   └── ui.py               # Terminal UI components
├── companion-app/          # Web companion app (PWA)
│   ├── index.html          # Main app
│   ├── manifest.json       # PWA manifest
│   └── sw.js               # Service worker
├── local_wallet/           # Local wallet storage
│   ├── keypair.json        # Private key (KEEP SECURE!)
│   └── pubkey.txt          # Public address
├── inbox/                  # Unsigned transactions
├── outbox/                 # Signed transactions
└── whitepaper.md           # Technical documentation
```

## Security Model

### Air-Gap Principles

1. **Private keys never touch networked computers**
   - Generated on offline device
   - Stored on USB only
   - Used only for signing on air-gapped machine

2. **Network isolation on USB**
   - Alpine Linux with all network drivers blacklisted
   - No WiFi, Ethernet, or Bluetooth
   - Firewall drops all traffic

3. **Manual transaction transfer**
   - QR codes for small transactions
   - File copy via USB for larger data
   - No automatic sync

### Threat Mitigation

| Threat | Mitigation |
|--------|------------|
| Malware on host PC | Keys never on host |
| Network attacks | Air-gap isolation |
| Transaction tampering | Verify on offline screen |
| USB compromise | Read-only filesystem |

## SPL Token Support

Supported tokens with auto-detected decimals:

| Token | Mint Address | Decimals |
|-------|--------------|----------|
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 6 |
| USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | 6 |
| BONK | `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263` | 5 |
| JUP | `JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN` | 6 |
| RAY | `4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R` | 6 |

Custom tokens supported via mint address.

## Network Configuration

```python
# config.py - Switch networks

# Mainnet
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# Devnet (default - for testing)
SOLANA_RPC_URL = "https://api.devnet.solana.com"

# Testnet
SOLANA_RPC_URL = "https://api.testnet.solana.com"
```

## Requirements

- **Python**: 3.11+
- **OS**: macOS, Linux, or Windows
- **USB**: 4GB+ drive (for cold wallet)
- **Root/Admin**: Required for USB operations

## Demo Videos

Check out our demo videos:
- [Remotion explainer video](./demos/)
- [Interactive HTML walkthrough](./demos/)
- [Manim educational animation](./demos/)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

## Security Disclosure

Found a vulnerability? [Open a Security Advisory](https://github.com/ExpertVagabond/coldstar-colosseum/security/advisories/new)

## License

MIT License - See [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Your keys, your responsibility. Open source, open trust.</strong>
  <br><br>
  Made with ✦ by <a href="https://github.com/ExpertVagabond/coldstar-colosseum">Coldstar Contributors</a>
</p>
