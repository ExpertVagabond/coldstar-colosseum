"""
QR Code Transfer Module - Generate QR codes for air-gapped data transfer

Enables easy transfer of:
- Unsigned transactions (from companion app to cold wallet)
- Signed transactions (from cold wallet to companion app)

B - Love U 3000
"""

import json
import base64
from pathlib import Path
from typing import Optional

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

from src.ui import print_success, print_error, print_info, print_warning


class QRTransfer:
    """Handle QR code generation and parsing for air-gapped transfers"""

    def __init__(self):
        self.qr_available = HAS_QRCODE

    def generate_ascii_qr(self, data: str, box_size: int = 1) -> Optional[str]:
        """Generate ASCII art QR code for terminal display"""
        if not self.qr_available:
            print_warning("qrcode library not installed. Install with: pip install qrcode")
            return None

        try:
            qr = qrcode.QRCode(
                version=None,  # Auto-size
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=box_size,
                border=2
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Generate ASCII representation
            lines = []
            for row in qr.modules:
                line = ""
                for cell in row:
                    if cell:
                        line += "██"
                    else:
                        line += "  "
                lines.append(line)

            return "\n".join(lines)
        except Exception as e:
            print_error(f"Failed to generate QR code: {e}")
            return None

    def display_transaction_qr(self, tx_data: dict, title: str = "SCAN THIS QR CODE"):
        """Display a transaction as an ASCII QR code in the terminal"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

        # Compress the data
        json_data = json.dumps(tx_data, separators=(',', ':'))

        # Check size - QR codes have limits
        if len(json_data) > 2000:
            print_warning("Transaction too large for QR. Using base64 encoding...")
            json_data = base64.b64encode(json_data.encode()).decode()

        ascii_qr = self.generate_ascii_qr(json_data)

        if ascii_qr:
            print(ascii_qr)
            print("\n" + "=" * 60)
            print_info(f"Data size: {len(json_data)} bytes")
        else:
            # Fallback: show base64 data
            print_info("QR generation unavailable. Copy this data manually:")
            print("-" * 60)
            print(json_data)
            print("-" * 60)

    def display_signed_tx_qr(self, signed_tx_bytes: bytes):
        """Display signed transaction as QR code"""
        tx_data = {
            "type": "signed_transaction",
            "version": "1.0",
            "data": base64.b64encode(signed_tx_bytes).decode('utf-8')
        }

        self.display_transaction_qr(tx_data, "SIGNED TRANSACTION - SCAN TO BROADCAST")

    def parse_unsigned_tx_input(self, input_data: str) -> Optional[dict]:
        """Parse unsigned transaction from QR scan or pasted data"""
        try:
            # Try direct JSON parse
            data = json.loads(input_data)

            if data.get("type") == "unsigned_transaction":
                return data
            else:
                print_error("Invalid transaction format")
                return None

        except json.JSONDecodeError:
            # Try base64 decode
            try:
                decoded = base64.b64decode(input_data).decode('utf-8')
                data = json.loads(decoded)
                if data.get("type") == "unsigned_transaction":
                    return data
            except Exception:
                pass

        print_error("Could not parse transaction data")
        return None

    def save_qr_image(self, data: str, output_path: str) -> bool:
        """Save QR code as PNG image"""
        if not self.qr_available:
            print_error("qrcode library not installed")
            return False

        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output_path)

            print_success(f"QR code saved to: {output_path}")
            return True
        except Exception as e:
            print_error(f"Failed to save QR image: {e}")
            return False


def create_qr_signing_workflow():
    """Interactive QR-based signing workflow for air-gapped device"""
    from src.wallet import WalletManager
    from src.transaction import TransactionManager

    print("\n" + "=" * 60)
    print("  COLDSTAR QR SIGNING MODE")
    print("  Air-gapped transaction signing with QR transfer")
    print("=" * 60 + "\n")

    qr = QRTransfer()
    wallet = WalletManager()
    tx_manager = TransactionManager()

    # Load wallet (encrypted container for secure signing)
    wallet_path = Path("/wallet/keypair.json")
    if not wallet_path.exists():
        wallet_path = Path("./local_wallet/keypair.json")

    if not wallet_path.exists():
        print_error("No wallet found. Generate one first.")
        return

    container = wallet.load_encrypted_container(str(wallet_path))
    if not container:
        print_error("Failed to load wallet. Legacy unencrypted wallets must be upgraded first.")
        return

    public_key = wallet.get_public_key()
    if not public_key:
        # Try reading from pubkey file
        pubkey_path = wallet_path.parent / "pubkey.txt"
        if pubkey_path.exists():
            public_key = pubkey_path.read_text().strip()
    if not public_key:
        print_error("Could not determine wallet public key")
        return
    print_info(f"Wallet loaded: {public_key[:8]}...{public_key[-8:]}")

    # Get transaction data from user
    print("\n" + "-" * 60)
    print("Paste the unsigned transaction JSON (from companion app):")
    print("(paste all at once, then press Enter twice)")
    print("-" * 60)

    lines = []
    while True:
        try:
            line = input()
            if line == "" and lines:
                break
            lines.append(line)
        except EOFError:
            break

    input_data = "\n".join(lines)

    # Parse transaction
    tx_data = qr.parse_unsigned_tx_input(input_data)

    if not tx_data:
        return

    # Display transaction details
    print("\n" + "=" * 60)
    print("  TRANSACTION DETAILS - VERIFY CAREFULLY!")
    print("=" * 60)
    print(f"  From:   {tx_data.get('from', 'Unknown')}")
    print(f"  To:     {tx_data.get('to', 'Unknown')}")
    print(f"  Amount: {tx_data.get('amount_sol', 0)} SOL")
    print(f"  Network: {tx_data.get('network', 'Unknown')}")
    print("=" * 60 + "\n")

    # Confirm signing
    confirm = input("Type 'SIGN' to sign this transaction: ").strip()

    if confirm != "SIGN":
        print_warning("Signing cancelled")
        return

    # Sign transaction securely via Rust signer
    try:
        from getpass import getpass
        from solders.pubkey import Pubkey
        from solders.hash import Hash
        from solders.system_program import transfer, TransferParams
        from solders.transaction import Transaction
        from solders.message import Message

        password = getpass("Enter wallet password to sign: ")
        if not password:
            print_error("Password required for encrypted wallet")
            return

        from_pk = Pubkey.from_string(tx_data['from'])
        to_pk = Pubkey.from_string(tx_data['to'])
        blockhash = Hash.from_string(tx_data['blockhash'])
        lamports = int(tx_data['lamports'])

        # Create transfer instruction
        transfer_ix = transfer(TransferParams(
            from_pubkey=from_pk,
            to_pubkey=to_pk,
            lamports=lamports
        ))

        # Build unsigned transaction, sign via Rust secure signer
        message = Message.new_with_blockhash([transfer_ix], from_pk, blockhash)
        tx = Transaction.new_unsigned(message)
        unsigned_bytes = bytes(tx)

        signed_bytes = tx_manager.sign_transaction_secure(unsigned_bytes, container, password)
        if not signed_bytes:
            print_error("Signing failed — wrong password or corrupted wallet")
            return

        print_success("Transaction SIGNED securely via Rust signer!")

        # Display QR code
        qr.display_signed_tx_qr(signed_bytes)

        # Also save to file
        outbox_path = Path("/outbox")
        if not outbox_path.exists():
            outbox_path = Path("./outbox")
        outbox_path.mkdir(parents=True, exist_ok=True)

        output_file = outbox_path / f"signed_tx_{int(__import__('time').time())}.json"
        tx_manager.save_signed_transaction(signed_bytes, str(output_file))

        print_info("\nNext steps:")
        print_info("1. Scan the QR code with your companion app, OR")
        print_info(f"2. Copy {output_file} to your online device")
        print_info("3. Broadcast the transaction from the companion app")

    except Exception as e:
        print_error(f"Signing failed: {e}")


if __name__ == "__main__":
    create_qr_signing_workflow()
