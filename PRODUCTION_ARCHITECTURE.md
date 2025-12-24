# Solana Cold Wallet - Production Architecture

## Overview

A browser-based Solana cold wallet system that enables secure offline transaction signing using a bootable USB device with WebSerial communication.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         WEBSITE                                 │
│  • Create/manage transactions                                   │
│  • WebSerial communication with cold wallet device              │
│  • Broadcast signed transactions to Solana network              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ WebSerial (USB connection)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USB COLD WALLET DEVICE                       │
│  • Boots Alpine Linux from USB drive                            │
│  • USB Gadget Mode exposes serial interface                     │
│  • Solana CLI for offline transaction signing                   │
│  • Private keys generated and stored locally                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## User Flow

### One-Time Setup

1. **Download ISO** - User downloads the cold wallet ISO from the website
2. **Flash to USB** - User flashes ISO to USB drive using:
   - balenaEtcher (cross-platform, easiest)
   - Rufus (Windows)
   - dd command (Linux/macOS)
   - Ventoy (multi-ISO USB, drag-and-drop)
3. **First Boot** - User boots an air-gapped PC from the USB
4. **Keypair Generation** - Private keys are generated on the air-gapped device (never touches the internet)

### Transaction Signing Session

```
┌─────────────────────────────────────────────────────────────────┐
│                        SIGNING FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Boot USB on any PC (laptop, Raspberry Pi, etc.)            │
│                              │                                  │
│                              ▼                                  │
│  2. USB Gadget Mode activates automatically                    │
│     → Device appears as a serial device to host PC             │
│                              │                                  │
│                              ▼                                  │
│  3. Connect USB device to main PC via USB cable                │
│                              │                                  │
│                              ▼                                  │
│  4. Open website in Chrome/Edge browser                        │
│     → WebSerial connects to cold wallet device                 │
│                              │                                  │
│                              ▼                                  │
│  5. Create transaction on website                              │
│     (recipient, amount, etc.)                                  │
│                              │                                  │
│                              ▼                                  │
│  6. Transaction sent to device for signing                     │
│     → Signed OFFLINE on air-gapped device                      │
│     → Signed transaction returned to browser                   │
│                              │                                  │
│                              ▼                                  │
│  7. Website broadcasts signed TX to Solana network             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### Website (Frontend)

| Feature | Description |
|---------|-------------|
| Wallet Dashboard | View balance, transaction history |
| Transaction Builder | Create SOL transfers, token transfers |
| WebSerial Interface | Connect and communicate with USB device |
| Transaction Broadcaster | Submit signed transactions to Solana RPC |
| Device Manager | Detect, connect, disconnect USB devices |

### USB ISO (Cold Wallet Device)

| Component | Description |
|-----------|-------------|
| Alpine Linux | Minimal, secure base OS (~50MB) |
| Solana CLI | Transaction signing tools |
| USB Gadget Script | Exposes device as serial interface |
| Signing Service | Listens for signing requests, returns signatures |
| Wallet Manager | Keypair generation, secure storage |

### Communication Protocol

JSON-based messages over WebSerial:

```json
// Request (Browser → Device)
{
  "action": "sign_transaction",
  "transaction": "<base64-encoded-unsigned-tx>",
  "request_id": "uuid"
}

// Response (Device → Browser)
{
  "status": "success",
  "signature": "<base64-encoded-signature>",
  "signed_transaction": "<base64-encoded-signed-tx>",
  "request_id": "uuid"
}
```

---

## Security Model

### Key Security Principles

| Principle | Implementation |
|-----------|----------------|
| **Air-gapped Key Generation** | Private keys generated on first boot of USB device, never on networked computer |
| **Offline Signing** | All transaction signing occurs on the USB-booted device without network access |
| **No Key Exposure** | Private keys never leave the USB device; only signed transactions are returned |
| **Minimal Attack Surface** | Alpine Linux is minimal (~50MB), reducing potential vulnerabilities |
| **User-Controlled** | User physically controls the USB device at all times |

### Threat Model

| Threat | Mitigation |
|--------|------------|
| Malware on host PC | Keys never exist on host; only signed TXs pass through |
| Network interception | Signing happens offline; no network during signing |
| USB device theft | Optional: Encrypt keypair with passphrase |
| Malicious website | Device validates transaction details before signing |
| Supply chain attack | Open-source ISO, reproducible builds, checksum verification |

---

## Hardware Requirements

### For USB Cold Wallet Device

| Requirement | Details |
|-------------|---------|
| USB Drive | 4GB+ recommended |
| Boot Device | Any x86_64 PC, laptop, or Raspberry Pi |
| USB OTG/Gadget Support | Required for WebSerial mode (most laptops with USB-C, all Raspberry Pi) |

### For Host PC (Running Website)

| Requirement | Details |
|-------------|---------|
| Browser | Chrome, Edge, or Opera (WebSerial support) |
| USB Port | For connecting to cold wallet device |
| Internet | For broadcasting transactions |

---

## Technology Stack

### Website
- Frontend: React/TypeScript
- WebSerial API for USB communication
- Solana Web3.js for transaction building and broadcasting

### USB ISO
- Alpine Linux (minimal footprint)
- Solana CLI tools
- Python/Shell scripts for signing service
- Linux USB Gadget framework (configfs)

---

## Future Enhancements

1. **Hardware Wallet Support** - Integrate with Ledger/Trezor as alternative signing devices
2. **Multi-signature** - Support for multi-sig wallets
3. **Token Support** - SPL token transfers, NFTs
4. **Transaction Templates** - Save and reuse common transaction patterns
5. **Mobile Support** - WebSerial on Android Chrome
6. **Encrypted Storage** - Passphrase-protected keypairs on USB

---

## Development Phases

### Phase 1: CLI Tool (Current)
- Python-based terminal application
- USB flashing and wallet management
- Basic transaction creation and signing

### Phase 2: Web Interface + Downloadable ISO
- Website for transaction management
- Downloadable cold wallet ISO
- User flashes locally with Etcher/Rufus

### Phase 3: WebSerial Integration
- USB Gadget mode in ISO
- WebSerial communication protocol
- Browser-based signing workflow

### Phase 4: Production Hardening
- Security audit
- Reproducible builds
- Code signing and checksum verification
- User documentation and guides
