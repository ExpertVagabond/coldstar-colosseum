#!/usr/bin/env python3
"""
Coldstar QR Sign - Air-gapped transaction signing with QR code transfer

Usage:
    python3 qr_sign.py                    # Interactive QR signing mode
    python3 qr_sign.py --show-wallet      # Display wallet QR code
    python3 qr_sign.py --help             # Show help

B - Love U 3000
"""

import sys
import json
import base64
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.hash import Hash
    from solders.system_program import transfer, TransferParams
    from solders.transaction import Transaction
    from solders.message import Message
    HAS_SOLDERS = True
except ImportError:
    HAS_SOLDERS = False
    print("Warning: solders library not installed")

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


# Colors for terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Print Coldstar banner"""
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                            ║
║     ✦  {Colors.BOLD}COLDSTAR QR SIGN{Colors.RESET}{Colors.CYAN}                               ║
║     Air-Gapped Transaction Signing                         ║
║                                                            ║
╚══════════════════════════════════════════════════════════╝{Colors.RESET}
""")


def generate_ascii_qr(data: str) -> str:
    """Generate ASCII QR code"""
    if not HAS_QRCODE:
        return f"[QR library not installed]\n\nData:\n{data}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1
    )
    qr.add_data(data)
    qr.make(fit=True)

    lines = []
    for row in qr.modules:
        line = ""
        for cell in row:
            line += "██" if cell else "  "
        lines.append(line)

    return "\n".join(lines)


def find_wallet():
    """Find wallet keypair file"""
    search_paths = [
        Path("/wallet/keypair.json"),
        Path("./wallet/keypair.json"),
        Path("./local_wallet/keypair.json"),
        Path.home() / "coldstar" / "wallet" / "keypair.json",
    ]

    for path in search_paths:
        if path.exists():
            return path

    return None


def load_keypair(path: Path) -> Keypair:
    """Load keypair from file"""
    with open(path, 'r') as f:
        secret_list = json.load(f)
    return Keypair.from_bytes(bytes(secret_list))


def show_wallet_qr(keypair: Keypair):
    """Display wallet public key as QR code"""
    pubkey = str(keypair.pubkey())

    print(f"\n{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}  WALLET PUBLIC KEY - Scan to receive SOL{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")

    print(generate_ascii_qr(pubkey))

    print(f"\n{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    print(f"  Address: {Colors.GREEN}{pubkey}{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")


def sign_transaction(keypair: Keypair, tx_data: dict) -> bytes:
    """Sign a transaction with the keypair"""
    from_pk = Pubkey.from_string(tx_data['from'])
    to_pk = Pubkey.from_string(tx_data['to'])
    blockhash = Hash.from_string(tx_data['blockhash'])
    lamports = int(tx_data['lamports'])

    transfer_ix = transfer(TransferParams(
        from_pubkey=from_pk,
        to_pubkey=to_pk,
        lamports=lamports
    ))

    message = Message.new_with_blockhash([transfer_ix], from_pk, blockhash)
    tx = Transaction.new_unsigned(message)
    tx.sign([keypair], blockhash)

    return bytes(tx)


def interactive_sign():
    """Interactive signing workflow"""
    print_banner()

    # Check dependencies
    if not HAS_SOLDERS:
        print(f"{Colors.RED}Error: solders library required{Colors.RESET}")
        print("Install with: pip install solders solana")
        sys.exit(1)

    # Find wallet
    wallet_path = find_wallet()
    if not wallet_path:
        print(f"{Colors.RED}Error: No wallet found{Colors.RESET}")
        print("\nSearched locations:")
        print("  - /wallet/keypair.json")
        print("  - ./wallet/keypair.json")
        print("  - ./local_wallet/keypair.json")
        sys.exit(1)

    # Load keypair
    try:
        keypair = load_keypair(wallet_path)
        pubkey = str(keypair.pubkey())
        print(f"{Colors.GREEN}✓ Wallet loaded:{Colors.RESET} {pubkey[:16]}...{pubkey[-8:]}")
    except Exception as e:
        print(f"{Colors.RED}Error loading wallet: {e}{Colors.RESET}")
        sys.exit(1)

    # Get transaction input
    print(f"\n{Colors.YELLOW}Paste the unsigned transaction JSON:{Colors.RESET}")
    print(f"{Colors.CYAN}(from companion app - paste all at once, then press Enter twice){Colors.RESET}")
    print("─" * 60)

    lines = []
    try:
        while True:
            line = input()
            if line == "" and lines:
                break
            lines.append(line)
    except EOFError:
        pass

    input_data = "\n".join(lines).strip()

    if not input_data:
        print(f"{Colors.RED}No transaction data provided{Colors.RESET}")
        sys.exit(1)

    # Parse transaction
    try:
        tx_data = json.loads(input_data)
    except json.JSONDecodeError:
        # Try base64 decode
        try:
            decoded = base64.b64decode(input_data).decode()
            tx_data = json.loads(decoded)
        except Exception:
            print(f"{Colors.RED}Error: Could not parse transaction data{Colors.RESET}")
            sys.exit(1)

    if tx_data.get("type") != "unsigned_transaction":
        print(f"{Colors.RED}Error: Invalid transaction format{Colors.RESET}")
        sys.exit(1)

    # Display transaction details
    print(f"\n{Colors.PURPLE}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}  TRANSACTION DETAILS - VERIFY CAREFULLY!{Colors.RESET}")
    print(f"{Colors.PURPLE}{'═' * 60}{Colors.RESET}")
    print(f"  From:    {Colors.CYAN}{tx_data.get('from', 'Unknown')}{Colors.RESET}")
    print(f"  To:      {Colors.CYAN}{tx_data.get('to', 'Unknown')}{Colors.RESET}")
    print(f"  Amount:  {Colors.GREEN}{tx_data.get('amount_sol', 0)} SOL{Colors.RESET}")
    print(f"  Network: {tx_data.get('network', 'Unknown')}")
    print(f"{Colors.PURPLE}{'═' * 60}{Colors.RESET}\n")

    # Confirm
    confirm = input(f"{Colors.YELLOW}Type 'SIGN' to sign this transaction: {Colors.RESET}").strip()

    if confirm != "SIGN":
        print(f"\n{Colors.YELLOW}Signing cancelled{Colors.RESET}")
        sys.exit(0)

    # Sign transaction
    try:
        signed_bytes = sign_transaction(keypair, tx_data)
        print(f"\n{Colors.GREEN}✓ Transaction SIGNED successfully!{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Error signing transaction: {e}{Colors.RESET}")
        sys.exit(1)

    # Create signed transaction data
    signed_data = {
        "type": "signed_transaction",
        "version": "1.0",
        "data": base64.b64encode(signed_bytes).decode('utf-8')
    }

    # Display QR code
    print(f"\n{Colors.GREEN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}  SIGNED TRANSACTION - SCAN TO BROADCAST{Colors.RESET}")
    print(f"{Colors.GREEN}{'═' * 60}{Colors.RESET}\n")

    qr_data = json.dumps(signed_data, separators=(',', ':'))
    print(generate_ascii_qr(qr_data))

    print(f"\n{Colors.GREEN}{'═' * 60}{Colors.RESET}")

    # Save to file
    outbox = Path("./outbox")
    outbox.mkdir(exist_ok=True)
    output_file = outbox / f"signed_tx_{int(time.time())}.json"

    with open(output_file, 'w') as f:
        json.dump(signed_data, f, indent=2)

    print(f"\n{Colors.GREEN}✓ Saved to: {output_file}{Colors.RESET}")
    print(f"\n{Colors.CYAN}Next steps:{Colors.RESET}")
    print("  1. Scan the QR code with your companion app, OR")
    print(f"  2. Copy {output_file} to your online device")
    print("  3. Broadcast from the companion app")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--show-wallet":
            if not HAS_SOLDERS:
                print("Error: solders library required")
                sys.exit(1)

            wallet_path = find_wallet()
            if wallet_path:
                keypair = load_keypair(wallet_path)
                show_wallet_qr(keypair)
            else:
                print("No wallet found")
            sys.exit(0)

        elif sys.argv[1] == "--help":
            print(__doc__)
            sys.exit(0)

    interactive_sign()


if __name__ == "__main__":
    main()
