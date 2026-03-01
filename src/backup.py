"""
Wallet Backup & Restore Module

Provides secure backup options:
- BIP39 Mnemonic seed phrase (12/24 words)
- Encrypted JSON export
- Paper wallet generation (QR codes)

B - Love U 3000
"""

import json
import base64
import gc
import hashlib
import secrets
import os
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime

from solders.keypair import Keypair

from src.ui import print_success, print_error, print_info, print_warning

try:
    from mnemonic import Mnemonic
    HAS_MNEMONIC = True
except ImportError:
    HAS_MNEMONIC = False

try:
    from nacl.secret import SecretBox
    from nacl.utils import random as nacl_random
    HAS_NACL = True
except ImportError:
    HAS_NACL = False

try:
    from argon2.low_level import hash_secret_raw, Type as Argon2Type
    HAS_ARGON2 = True
except ImportError:
    HAS_ARGON2 = False

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


# BIP39 English wordlist (first 100 words for demo, full list has 2048)
# In production, use the full wordlist from mnemonic library
WORDLIST_SAMPLE = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
    "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
    "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
    "adapt", "add", "addict", "address", "adjust", "admit", "adult", "advance",
    "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
    "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album",
]


class WalletBackup:
    """Secure wallet backup and restore operations"""

    def __init__(self):
        self.mnemonic_available = HAS_MNEMONIC
        self.encryption_available = HAS_NACL
        self.qr_available = HAS_QRCODE

    def generate_mnemonic(self, strength: int = 128) -> Optional[str]:
        """Generate a BIP39 mnemonic seed phrase

        Args:
            strength: 128 for 12 words, 256 for 24 words
        """
        if not self.mnemonic_available:
            print_warning("mnemonic library not installed. Install with: pip install mnemonic")
            # Fallback: generate simple word-based backup
            return self._generate_simple_mnemonic(12 if strength == 128 else 24)

        try:
            mnemo = Mnemonic("english")
            words = mnemo.generate(strength=strength)
            return words
        except Exception as e:
            print_error(f"Failed to generate mnemonic: {e}")
            return None

    def _generate_simple_mnemonic(self, word_count: int) -> str:
        """Fallback mnemonic generation using random bytes"""
        # Generate random entropy
        entropy = secrets.token_bytes(word_count * 2)

        # Convert to word indices (simplified)
        words = []
        for i in range(word_count):
            idx = int.from_bytes(entropy[i*2:i*2+2], 'big') % len(WORDLIST_SAMPLE)
            words.append(WORDLIST_SAMPLE[idx])

        return " ".join(words)

    def mnemonic_to_keypair(self, mnemonic: str, passphrase: str = "") -> Optional[Keypair]:
        """Derive Solana keypair from mnemonic"""
        if not self.mnemonic_available:
            print_error("mnemonic library required for recovery")
            return None

        try:
            mnemo = Mnemonic("english")

            # Validate mnemonic
            if not mnemo.check(mnemonic):
                print_error("Invalid mnemonic phrase")
                return None

            # Derive seed
            seed = mnemo.to_seed(mnemonic, passphrase)

            # Use first 32 bytes for Ed25519 keypair
            keypair = Keypair.from_seed(seed[:32])
            return keypair

        except Exception as e:
            print_error(f"Failed to derive keypair: {e}")
            return None

    def export_encrypted(self, keypair: Keypair, password: str) -> Optional[dict]:
        """Export keypair as encrypted JSON"""
        if not self.encryption_available:
            print_warning("nacl library not installed. Using base64 encoding (NOT SECURE!)")
            return self._export_base64(keypair)

        try:
            # Derive encryption key from password using Argon2id (preferred) or PBKDF2 (fallback)
            salt = nacl_random(32)  # 256-bit salt

            if HAS_ARGON2:
                # Argon2id: 256 MB memory, 4 iterations, 4 parallelism
                key = hash_secret_raw(
                    secret=password.encode(),
                    salt=salt,
                    time_cost=4,
                    memory_cost=262144,  # 256 MB
                    parallelism=4,
                    hash_len=32,
                    type=Argon2Type.ID,
                )
                kdf_algo = "argon2id"
            else:
                # Fallback: PBKDF2 with 600k iterations (OWASP 2024 minimum)
                key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000, dklen=32)
                kdf_algo = "pbkdf2_sha256_600k"

            # Encrypt keypair bytes
            box = SecretBox(key)
            nonce = nacl_random(24)
            encrypted = box.encrypt(bytes(keypair), nonce)

            # Zeroize key material
            password_bytes = password.encode()
            del key
            del password_bytes
            gc.collect()

            return {
                "version": "2.0",
                "type": "encrypted_keypair",
                "algorithm": "nacl_secretbox",
                "kdf": kdf_algo,
                "salt": base64.b64encode(salt).decode(),
                "nonce": base64.b64encode(nonce).decode(),
                "ciphertext": base64.b64encode(encrypted.ciphertext).decode(),
                "pubkey": str(keypair.pubkey()),
                "created_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            print_error(f"Encryption failed: {e}")
            return None

    def _export_base64(self, keypair: Keypair) -> dict:
        """Fallback: export as base64 (NOT SECURE - for testing only)"""
        return {
            "version": "1.0",
            "type": "base64_keypair",
            "algorithm": "none",
            "data": base64.b64encode(bytes(keypair)).decode(),
            "pubkey": str(keypair.pubkey()),
            "warning": "NOT ENCRYPTED - FOR TESTING ONLY",
            "created_at": datetime.utcnow().isoformat()
        }

    def import_encrypted(self, encrypted_data: dict, password: str) -> Optional[Keypair]:
        """Import keypair from encrypted JSON"""
        if encrypted_data.get("type") == "base64_keypair":
            # Handle unencrypted fallback
            try:
                key_bytes = base64.b64decode(encrypted_data["data"])
                return Keypair.from_bytes(key_bytes)
            except Exception as e:
                print_error(f"Failed to decode keypair: {e}")
                return None

        if not self.encryption_available:
            print_error("nacl library required for decryption")
            return None

        try:
            salt = base64.b64decode(encrypted_data["salt"])
            nonce = base64.b64decode(encrypted_data["nonce"])
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])

            # Derive key using the appropriate KDF
            kdf = encrypted_data.get("kdf", "pbkdf2_sha256_100k")
            if kdf == "argon2id" and HAS_ARGON2:
                key = hash_secret_raw(
                    secret=password.encode(),
                    salt=salt,
                    time_cost=4,
                    memory_cost=262144,
                    parallelism=4,
                    hash_len=32,
                    type=Argon2Type.ID,
                )
            elif kdf == "pbkdf2_sha256_600k":
                key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000, dklen=32)
            else:
                # Legacy: 100k iterations
                key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)

            # Decrypt
            box = SecretBox(key)
            decrypted = box.decrypt(ciphertext, nonce)

            # Cleanup
            del key
            gc.collect()

            return Keypair.from_bytes(decrypted)

        except Exception as e:
            print_error(f"Decryption failed: {e}")
            return None

    def create_paper_wallet(self, keypair: Keypair, output_dir: str = ".") -> Optional[str]:
        """Create a paper wallet with QR codes"""
        if not self.qr_available:
            print_error("qrcode library required. Install with: pip install qrcode")
            return None

        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            pubkey = str(keypair.pubkey())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"paper_wallet_{pubkey[:8]}_{timestamp}.html"
            filepath = output_path / filename

            # Generate QR codes
            pubkey_qr = qrcode.make(pubkey)
            secret_qr = qrcode.make(base64.b64encode(bytes(keypair)).decode())

            # Save QR images temporarily
            import io
            import base64 as b64

            pubkey_buffer = io.BytesIO()
            pubkey_qr.save(pubkey_buffer, format='PNG')
            pubkey_b64 = b64.b64encode(pubkey_buffer.getvalue()).decode()

            secret_buffer = io.BytesIO()
            secret_qr.save(secret_buffer, format='PNG')
            secret_b64 = b64.b64encode(secret_buffer.getvalue()).decode()

            # Generate HTML paper wallet
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Coldstar Paper Wallet</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            background: #fff;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #000;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            border: 2px solid #000;
        }}
        .qr-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .qr-container img {{
            max-width: 250px;
        }}
        .address {{
            word-break: break-all;
            font-size: 14px;
            background: #f0f0f0;
            padding: 10px;
            margin: 10px 0;
        }}
        .warning {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        .fold-line {{
            border-top: 2px dashed #ccc;
            margin: 40px 0;
            text-align: center;
        }}
        .fold-line::before {{
            content: '✂ FOLD HERE - KEEP PRIVATE KEY HIDDEN ✂';
            background: #fff;
            padding: 0 20px;
            position: relative;
            top: -12px;
            color: #999;
        }}
        @media print {{
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>COLDSTAR PAPER WALLET</h1>
        <p>Solana Cold Storage</p>
        <p style="font-size: 12px;">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
    </div>

    <div class="section">
        <h2>PUBLIC ADDRESS (Share this to receive SOL)</h2>
        <div class="qr-container">
            <img src="data:image/png;base64,{pubkey_b64}" alt="Public Key QR">
        </div>
        <div class="address">{pubkey}</div>
    </div>

    <div class="fold-line"></div>

    <div class="section" style="background: #ffe6e6;">
        <h2>PRIVATE KEY (NEVER SHARE!)</h2>
        <div class="warning">
            <strong>WARNING:</strong> Anyone with this key can steal all your funds!
            Keep this hidden, secure, and never photograph or share it.
        </div>
        <div class="qr-container">
            <img src="data:image/png;base64,{secret_b64}" alt="Private Key QR">
        </div>
        <div class="address" style="font-size: 10px;">
            {base64.b64encode(bytes(keypair)).decode()}
        </div>
    </div>

    <div class="section no-print">
        <h3>Instructions:</h3>
        <ol>
            <li>Print this page on a secure, offline printer</li>
            <li>Fold along the dashed line to hide the private key</li>
            <li>Store in a fireproof safe or safety deposit box</li>
            <li>Consider making multiple copies stored in different locations</li>
            <li>Delete this file securely after printing</li>
        </ol>
    </div>

    <p style="text-align: center; margin-top: 40px; color: #999;">
        Generated by Coldstar | github.com/ExpertVagabond/coldstar-colosseum
    </p>
</body>
</html>"""

            with open(filepath, 'w') as f:
                f.write(html_content)

            print_success(f"Paper wallet created: {filepath}")
            return str(filepath)

        except Exception as e:
            print_error(f"Failed to create paper wallet: {e}")
            return None

    def backup_to_file(self, keypair: Keypair, path: str, password: Optional[str] = None) -> bool:
        """Backup keypair to file (encrypted if password provided)"""
        try:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            if password:
                data = self.export_encrypted(keypair, password)
            else:
                data = {
                    "version": "1.0",
                    "type": "plaintext_keypair",
                    "keypair": list(bytes(keypair)),
                    "pubkey": str(keypair.pubkey()),
                    "created_at": datetime.utcnow().isoformat()
                }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            os.chmod(filepath, 0o600)  # Read/write owner only

            print_success(f"Wallet backed up to: {filepath}")
            if not password:
                print_warning("No password provided - backup is NOT encrypted!")

            return True

        except Exception as e:
            print_error(f"Backup failed: {e}")
            return False

    def restore_from_file(self, path: str, password: Optional[str] = None) -> Optional[Keypair]:
        """Restore keypair from backup file"""
        try:
            filepath = Path(path)
            if not filepath.exists():
                print_error(f"Backup file not found: {path}")
                return None

            with open(filepath, 'r') as f:
                data = json.load(f)

            if data.get("type") == "encrypted_keypair":
                if not password:
                    print_error("Password required for encrypted backup")
                    return None
                return self.import_encrypted(data, password)

            elif data.get("type") in ["plaintext_keypair", "base64_keypair"]:
                if "keypair" in data:
                    return Keypair.from_bytes(bytes(data["keypair"]))
                elif "data" in data:
                    return Keypair.from_bytes(base64.b64decode(data["data"]))

            print_error("Unknown backup format")
            return None

        except Exception as e:
            print_error(f"Restore failed: {e}")
            return None


def interactive_backup():
    """Interactive backup workflow"""
    from src.wallet import WalletManager

    print("\n" + "=" * 60)
    print("  COLDSTAR WALLET BACKUP")
    print("=" * 60 + "\n")

    backup = WalletBackup()
    wallet = WalletManager()

    # Find wallet
    wallet_path = Path("./local_wallet/keypair.json")
    if not wallet_path.exists():
        wallet_path = Path("/wallet/keypair.json")

    if not wallet_path.exists():
        print_error("No wallet found to backup")
        return

    import gc

    # Load encrypted wallet container
    container = wallet.load_encrypted_container(str(wallet_path))
    if not container:
        print_error("Failed to load wallet. Legacy unencrypted wallets must be upgraded first.")
        return

    # Get pubkey for display (without decrypting)
    pubkey = wallet.get_public_key()
    if not pubkey:
        pubkey_path = wallet_path.parent / "pubkey.txt"
        if pubkey_path.exists():
            pubkey = pubkey_path.read_text().strip()
    print(f"Wallet: {(pubkey or 'unknown')[:16]}...")

    print("\nBackup Options:")
    print("  1. Create paper wallet (printable HTML)")
    print("  2. Export encrypted backup")
    print("  3. Export plaintext backup (NOT SECURE)")
    print("  4. Cancel")

    choice = input("\nSelect option: ").strip()

    if choice not in ("1", "2", "3"):
        print("Cancelled")
        return

    # Decrypt keypair via Rust signer (needed for all backup operations)
    from getpass import getpass
    wallet_password = getpass("Enter wallet password: ")
    if not wallet_password:
        print_error("Password required")
        return

    keypair = None
    try:
        if wallet.rust_signer:
            normalized = wallet._normalize_container_format(container)
            private_key = wallet.rust_signer.decrypt_private_key(
                normalized, wallet_password
            )
            if not private_key or len(private_key) != 32:
                print_error("Invalid password or corrupted wallet")
                return
            from solders.keypair import Keypair
            keypair = Keypair.from_bytes(bytes(private_key))
            del private_key
        else:
            print_error("Rust signer required for wallet decryption")
            return

        if choice == "1":
            path = backup.create_paper_wallet(keypair, "./backups")
            if path:
                print_info(f"Open {path} in your browser to print")

        elif choice == "2":
            password = input("Enter encryption password for backup: ").strip()
            if len(password) < 8:
                print_error("Password must be at least 8 characters")
                return
            confirm = input("Confirm password: ").strip()
            if password != confirm:
                print_error("Passwords don't match")
                return

            backup.backup_to_file(keypair, "./backups/wallet_backup.json", password)

        elif choice == "3":
            confirm = input("WARNING: Plaintext backup is NOT SECURE. Type 'INSECURE' to confirm: ")
            if confirm == "INSECURE":
                backup.backup_to_file(keypair, "./backups/wallet_plaintext.json")
    finally:
        if keypair is not None:
            del keypair
        gc.collect()


if __name__ == "__main__":
    interactive_backup()
