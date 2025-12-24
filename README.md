# Solana Cold Wallet USB Tool

A Python-based terminal application for creating and managing Solana cold wallets on USB drives. This tool enables offline transaction signing for maximum security.

## Features

- **USB Detection & Flashing**: Detect USB devices and flash them with a minimal offline Linux OS
- **Wallet Generation**: Create Solana keypairs with Ed25519 cryptography
- **Offline Signing**: Sign transactions on air-gapped devices without network access
- **Transaction Management**: Create, sign, and broadcast SOL transfer transactions
- **Balance Checking**: Query wallet balances via Solana RPC
- **Devnet Airdrop**: Request test SOL on Devnet for testing

## Requirements

- Python 3.11+
- Windows or Linux operating system
- Root/Administrator privileges (for USB operations)

## Installation

### Step 1: Install Python Dependencies

**Before launching VS Code**, install the required Python packages by running this command in your terminal:

```bash
pip install rich questionary solana solders pynacl httpx aiofiles base58
```

### Step 2: Run in VS Code

1. Clone this repository
2. Open the project folder in VS Code
3. If you haven't installed dependencies yet, open the VS Code terminal (`` Ctrl+` ``) and run:

```bash
pip install rich questionary solana solders pynacl httpx aiofiles base58
```

4. Run the application:

```bash
python main.py
```

**Note for Linux users**: USB operations (flashing, mounting) may require root privileges:
```bash
sudo python main.py
```

## Usage

### Main Menu Options

1. **Detect USB Devices** - Scan and list connected USB drives
2. **Flash Cold Wallet OS to USB** - Create a bootable offline wallet USB
3. **Generate New Wallet (Local)** - Create a new Solana keypair locally
4. **View Wallet Information** - Check wallet public key and balance
5. **Create Unsigned Transaction** - Build a SOL transfer transaction
6. **Sign Transaction (Offline)** - Sign a transaction with your private key
7. **Broadcast Signed Transaction** - Send a signed transaction to the network
8. **Request Devnet Airdrop** - Get free test SOL on Devnet
9. **Network Status** - Check Solana RPC connection status

### Workflow: End-to-End Transaction

1. **Generate a wallet** (Option 3)
2. **Request airdrop** to fund the wallet (Option 8)
3. **Create unsigned transaction** specifying recipient and amount (Option 5)
4. **Sign the transaction** with your keypair (Option 6)
5. **Broadcast** the signed transaction to the network (Option 7)

### Cold Wallet USB Flow

For true offline signing:

1. Flash a USB with the cold wallet OS (Option 2)
2. Boot from the USB on an air-gapped machine
3. Generate wallet on the USB (keys never leave the device)
4. Copy unsigned transactions to `/inbox` on the USB
5. Sign using the `sign_tx.sh` script on the USB
6. Copy signed transactions from `/outbox` back to online host
7. Broadcast from the online host

## Directory Structure

```
.
├── main.py              # Main CLI entry point
├── config.py            # Configuration settings
├── src/
│   ├── __init__.py
│   ├── ui.py            # Terminal UI components
│   ├── wallet.py        # Wallet/keypair management
│   ├── network.py       # Solana RPC communication
│   ├── transaction.py   # Transaction creation/signing
│   ├── usb.py           # USB device detection/mounting
│   └── iso_builder.py   # Bootable ISO creation
├── local_wallet/        # Local wallet storage
│   ├── keypair.json     # Private keypair (KEEP SECURE!)
│   ├── pubkey.txt       # Public key
│   └── transactions/    # Transaction files
└── README.md
```

## Security Notes

- **Private keys** are stored in `keypair.json` - NEVER share this file
- The cold wallet USB has **no network drivers** - private keys cannot be exfiltrated
- Always verify transaction details before signing
- Use Devnet for testing before moving to Mainnet

## Network Configuration

Currently configured for **Devnet**. To switch to Mainnet, edit `config.py`:

```python
# For Mainnet
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# For Devnet (default)
SOLANA_RPC_URL = "https://api.devnet.solana.com"
```

## Known Limitations

- USB flashing requires Linux with root privileges
- No encrypted wallet storage (planned for future)
- No hardware wallet integration (planned)
- No staking support (planned)

## License

MIT License
