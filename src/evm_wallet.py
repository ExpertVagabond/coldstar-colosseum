"""
EVM Wallet Management - secp256k1 keypair generation and encrypted storage

Supports Base (Coinbase L2) and any EVM-compatible chain.
Uses eth-account for key generation with the same Rust-encrypted container
format used by the Solana wallet (Argon2id + AES-256-GCM).

B - Love U 3000
"""

import json
import os
import gc
import sys
import base64
import secrets
from pathlib import Path
from typing import Optional, Tuple

from eth_account import Account
from eth_account.signers.local import LocalAccount

from src.ui import (
    print_success, print_error, print_info, print_warning,
    get_password_input, confirm_dangerous_action,
)
from src.secure_memory import SecureWalletHandler

# Try to import Rust signer for encrypted container management
RUST_SIGNER_AVAILABLE = False
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from python_signer_example import SolanaSecureSigner  # reuse encryption primitives
    RUST_SIGNER_AVAILABLE = True
except ImportError:
    pass  # Fall back to Python-only encryption


class EVMWalletManager:
    """Manage EVM (Base/Ethereum) wallets with air-gapped security."""

    def __init__(self, wallet_dir: str = None):
        self.wallet_dir = Path(wallet_dir) if wallet_dir else None
        self.account: Optional[LocalAccount] = None
        self.keypair_path: Optional[Path] = None
        self.address_path: Optional[Path] = None
        self.encrypted_container: Optional[dict] = None
        self._cached_password: Optional[str] = None

        # Try Rust signer for encryption (optional — Python fallback available)
        self.rust_signer = None
        if RUST_SIGNER_AVAILABLE:
            try:
                self.rust_signer = SolanaSecureSigner()
            except Exception:
                pass

    def set_wallet_directory(self, path: str):
        self.wallet_dir = Path(path)
        self.keypair_path = self.wallet_dir / "evm_keypair.json"
        self.address_path = self.wallet_dir / "evm_address.txt"

    # ── Key Generation ──────────────────────────────────────

    def generate_keypair(self) -> Tuple[LocalAccount, str]:
        """Generate a new secp256k1 keypair for EVM."""
        # Use secrets for cryptographically secure randomness
        private_key = secrets.token_bytes(32)
        self.account = Account.from_key(private_key)
        address = self.account.address
        print_success(f"Generated new EVM keypair")
        print_info(f"Address: {address}")
        # Wipe the intermediate private_key reference
        del private_key
        return self.account, address

    # ── Save / Load ─────────────────────────────────────────

    def save_keypair(self, path: str = None) -> bool:
        """Encrypt and save EVM private key to disk."""
        if self.account is None:
            print_error("No keypair to save. Generate one first.")
            return False

        save_path = Path(path) if path else self.keypair_path
        if save_path is None:
            print_error("No save path specified")
            return False

        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)

            print_info("Encrypting EVM wallet with password...")
            password = get_password_input("Enter a strong password to encrypt your wallet:")
            confirm = get_password_input("Confirm password:")

            if password != confirm:
                print_error("Passwords do not match!")
                return False
            if not password:
                print_error("Password cannot be empty!")
                return False

            # Get raw 32-byte private key
            private_key_bytes = self.account.key

            # Encrypt using Rust signer if available, else Python fallback
            if self.rust_signer:
                container = self.rust_signer.create_encrypted_container(
                    bytes(private_key_bytes), password
                )
                container = self._normalize_container_format(container)
                container["chain"] = "evm"
                container["address"] = self.account.address
            else:
                # Python-only fallback using eth-account's keystore
                container = Account.encrypt(private_key_bytes, password)
                container["chain"] = "evm"

            with open(save_path, 'w') as f:
                json.dump(container, f, indent=2)

            # Save address in plaintext for quick lookup
            address_path = save_path.parent / "evm_address.txt"
            with open(address_path, 'w') as f:
                f.write(self.account.address)

            os.chmod(save_path, 0o600)

            # Clear plaintext key from memory
            self.account = None
            gc.collect()

            print_success(f"Encrypted EVM keypair saved to {save_path}")
            print_success(f"Address saved to {address_path}")
            return True

        except Exception as e:
            print_error(f"Failed to save keypair: {e}")
            return False

    def load_keypair(self, path: str = None) -> Optional[LocalAccount]:
        """Load and decrypt EVM keypair from disk."""
        load_path = Path(path) if path else self.keypair_path
        if load_path is None or not load_path.exists():
            print_error(f"Keypair file not found: {load_path}")
            return None

        try:
            with open(load_path, 'r') as f:
                data = json.load(f)

            if not data:
                print_error("Wallet file is empty or corrupted!")
                return None

            # Store encrypted container (don't decrypt yet)
            self.encrypted_container = data
            print_info("EVM wallet loaded (encrypted).")
            return None  # Password requested at signing time

        except Exception as e:
            print_error(f"Failed to load keypair: {e}")
            return None

    def load_encrypted_container(self, path: str = None) -> Optional[dict]:
        """Load encrypted container for use with signing (no key in memory)."""
        load_path = Path(path) if path else self.keypair_path
        if load_path is None or not load_path.exists():
            print_error(f"Keypair file not found: {load_path}")
            return None

        try:
            with open(load_path, 'r') as f:
                data = json.load(f)

            if not data:
                print_error("Wallet file is empty or corrupted!")
                return None

            # Detect format
            if "ciphertext" in data and "nonce" in data and "salt" in data:
                # Rust encrypted format
                data = self._normalize_container_format(data)
                print_success("EVM wallet loaded (Rust secure format)")
            elif "crypto" in data:
                # eth-account keystore format (Python fallback)
                print_success("EVM wallet loaded (keystore format)")
            else:
                print_error("Unknown wallet format")
                return None

            self.encrypted_container = data
            return data

        except Exception as e:
            print_error(f"Failed to load encrypted container: {e}")
            return None

    # ── Address & Validation ────────────────────────────────

    def get_address(self) -> Optional[str]:
        """Get the EVM address from loaded account or file."""
        if self.account:
            return self.account.address
        return self.get_address_from_file()

    def get_address_from_file(self, path: str = None) -> Optional[str]:
        addr_path = Path(path) if path else self.address_path
        if addr_path is None or not addr_path.exists():
            # Try reading from encrypted container
            if self.encrypted_container and "address" in self.encrypted_container:
                addr = self.encrypted_container["address"]
                if not addr.startswith("0x"):
                    addr = "0x" + addr
                return addr
            return None
        try:
            with open(addr_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return None

    @staticmethod
    def validate_address(address: str) -> bool:
        """Validate an EVM address (basic checksum-aware check)."""
        if not address or not address.startswith("0x"):
            return False
        if len(address) != 42:
            return False
        try:
            int(address, 16)
            return True
        except ValueError:
            return False

    # ── Decryption (for signing) ────────────────────────────

    def decrypt_private_key(self, container: dict, password: str) -> Optional[bytes]:
        """Decrypt private key from container. Returns raw 32-byte key."""
        try:
            if "ciphertext" in container and self.rust_signer:
                # Rust format — decrypt via Rust signer
                private_key = self.rust_signer.decrypt_private_key(container, password)
                if private_key and len(private_key) == 32:
                    return bytes(private_key)
                return None
            elif "crypto" in container:
                # eth-account keystore format
                private_key = Account.decrypt(container, password)
                return private_key
            else:
                print_error("Unknown container format")
                return None
        except Exception as e:
            print_error(f"Decryption failed: {e}")
            return None

    # ── Memory Management ───────────────────────────────────

    def clear_memory(self):
        """Securely clear loaded key material from memory."""
        self.account = None
        self.encrypted_container = None
        self._cached_password = None
        gc.collect()

    # ── Helpers ──────────────────────────────────────────────

    def _normalize_container_format(self, container: dict) -> dict:
        """Normalize Rust container — convert array fields to base64 strings."""
        normalized = container.copy()
        if 'version' not in normalized:
            normalized['version'] = 1
        for field in ['ciphertext', 'nonce', 'salt']:
            if field in normalized and isinstance(normalized[field], list):
                normalized[field] = base64.b64encode(bytes(normalized[field])).decode('utf-8')
        return normalized

    def keypair_exists(self, path: str = None) -> bool:
        check_path = Path(path) if path else self.keypair_path
        return check_path is not None and check_path.exists()
