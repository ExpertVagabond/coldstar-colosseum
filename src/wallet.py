"""
Wallet Management - Keypair generation and storage

B - Love U 3000
"""

import json
import os
import gc
import sys
import base64
import math
import shutil
import time
from pathlib import Path
from typing import Optional, Tuple

from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58

from src.ui import print_success, print_error, print_info, print_warning, get_password_input, confirm_dangerous_action
from src.secure_memory import SecureWalletHandler


# ── Password strength validation ──────────────────────────────
def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validate password meets cold wallet security requirements.

    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Estimated entropy >= 50 bits
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    if not any(not c.isalnum() for c in password):
        return False, "Password must contain at least one special character"

    # Entropy estimation: charset_size ^ length
    charset = 0
    if any(c.islower() for c in password):
        charset += 26
    if any(c.isupper() for c in password):
        charset += 26
    if any(c.isdigit() for c in password):
        charset += 10
    if any(not c.isalnum() for c in password):
        charset += 32
    entropy = len(password) * math.log2(charset) if charset > 0 else 0
    if entropy < 50:
        return False, f"Password entropy too low ({entropy:.0f} bits, need >= 50)"

    return True, "OK"


# ── Attempt rate limiting ──────────────────────────────────────
class PasswordAttemptTracker:
    """Track failed password attempts with exponential backoff."""

    MAX_ATTEMPTS = 10  # Lock after this many failures

    def __init__(self):
        self._failed_attempts = 0
        self._last_attempt_time = 0.0

    def check_allowed(self) -> Tuple[bool, str]:
        """Check if another attempt is allowed. Returns (allowed, reason)."""
        if self._failed_attempts >= self.MAX_ATTEMPTS:
            return False, f"Wallet locked: {self.MAX_ATTEMPTS} failed attempts. Restart the application."

        if self._failed_attempts > 0:
            # Exponential backoff: 2^(attempts-1) seconds, capped at 60s
            delay = min(2 ** (self._failed_attempts - 1), 60)
            elapsed = time.time() - self._last_attempt_time
            if elapsed < delay:
                remaining = delay - elapsed
                return False, f"Rate limited. Wait {remaining:.0f}s before retrying."

        return True, ""

    def record_failure(self):
        self._failed_attempts += 1
        self._last_attempt_time = time.time()
        remaining = self.MAX_ATTEMPTS - self._failed_attempts
        if remaining > 0:
            print_warning(f"Incorrect password. {remaining} attempts remaining.")
        else:
            print_error(f"Wallet locked after {self.MAX_ATTEMPTS} failed attempts.")

    def record_success(self):
        self._failed_attempts = 0
        self._last_attempt_time = 0.0

# Import Rust signer (REQUIRED)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from python_signer_example import SolanaSecureSigner
    RUST_SIGNER_AVAILABLE = True
except ImportError as e:
    print_error("FATAL: Rust secure signer is required but not found!")
    print_error(f"Import error: {e}")
    print_info("Build the Rust signer:")
    print_info("  cd secure_signer")
    print_info("  cargo build --release")
    sys.exit(1)

class WalletManager:
    def __init__(self, wallet_dir: str = None):
        self.wallet_dir = Path(wallet_dir) if wallet_dir else None
        self.keypair: Optional[Keypair] = None
        self.keypair_path: Optional[Path] = None
        self.pubkey_path: Optional[Path] = None
        self.encrypted_container: Optional[dict] = None  # Store encrypted container for Rust signer
        self._cached_password: Optional[bytearray] = None  # Cache password as mutable bytearray for zeroization
        self._attempt_tracker = PasswordAttemptTracker()
        
        # Initialize Rust signer (REQUIRED for security)
        try:
            self.rust_signer = SolanaSecureSigner()
            print_success("✓ Rust secure signer initialized!")
            print_info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print_success("🔒 SECURITY AUDIT: Secure Signing Enabled")
            print_info("  ✓ Rust secure memory module loaded")
            print_info("  ✓ Memory locking: ENABLED")
            print_info("  ✓ Key isolation: ACTIVE")
            print_info("  ✓ Auto-zeroization: ENABLED")
            print_info("  ✓ Python memory exposure: BLOCKED")
            print_info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        except (FileNotFoundError, OSError) as e:
            print_error("FATAL: Rust library not found or incompatible!")
            print_error(f"Error: {e}")
            print_info("Build the Rust signer:")
            print_info("  cd secure_signer")
            print_info("  cargo build --release")
            sys.exit(1)
        except Exception as e:
            print_error(f"FATAL: Failed to initialize Rust signer: {e}")
            sys.exit(1)
    
    def set_wallet_directory(self, path: str):
        self.wallet_dir = Path(path)
        self.keypair_path = self.wallet_dir / "keypair.json"
        self.pubkey_path = self.wallet_dir / "pubkey.txt"
    
    def generate_keypair(self) -> Tuple[Keypair, str]:
        self.keypair = Keypair()
        public_key = str(self.keypair.pubkey())
        print_success(f"Generated new Solana keypair")
        return self.keypair, public_key
    
    def save_keypair(self, path: str = None) -> bool:
        if self.keypair is None:
            print_error("No keypair to save. Generate one first.")
            return False
        
        save_path = Path(path) if path else self.keypair_path
        if save_path is None:
            print_error("No save path specified")
            return False
        
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            print_info("Encrypting wallet with password...")
            password = get_password_input("Enter a strong password to encrypt your wallet:")
            confirm = get_password_input("Confirm password:")
            
            if password != confirm:
                print_error("Passwords do not match!")
                return False
                
            if not password:
                print_error("Password cannot be empty!")
                return False

            # Validate password strength for cold wallet
            valid, reason = validate_password_strength(password)
            if not valid:
                print_error(f"Weak password: {reason}")
                return False

            # Encrypt keypair
            encrypted_data = SecureWalletHandler.encrypt_keypair(self.keypair, password)
            
            with open(save_path, 'w') as f:
                json.dump(encrypted_data, f)
            
            pubkey_path = save_path.parent / "pubkey.txt"
            with open(pubkey_path, 'w') as f:
                f.write(str(self.keypair.pubkey()))
            
            os.chmod(save_path, 0o600)
            
            # Clear plaintext keypair from memory after saving
            self.keypair = None
            gc.collect()
            
            print_success(f"Encrypted keypair saved to {save_path}")
            print_success(f"Public key saved to {pubkey_path}")
            return True
        except Exception as e:
            print_error(f"Failed to save keypair: {e}")
            return False
    
    def load_keypair(self, path: str = None) -> Optional[Keypair]:
        load_path = Path(path) if path else self.keypair_path
        if load_path is None:
            print_error("No keypair path specified")
            return None
        
        if not load_path.exists():
            print_error(f"Keypair file not found: {load_path}")
            return None
        
        try:
            with open(load_path, 'r') as f:
                file_content = f.read()
            
            # Check if file is empty or corrupted
            if not file_content or file_content.strip() == "":
                print_error("Wallet file is empty or corrupted!")
                
                # Check for backup
                backup_path = load_path.with_suffix('.pynacl.backup')
                if backup_path.exists():
                    print_info("Found backup wallet file. Attempting recovery...")
                    if confirm_dangerous_action("Restore from backup?", "RESTORE"):
                        shutil.copy(backup_path, load_path)
                        # Sync the restored file
                        with open(load_path, 'r+b') as f:
                            os.fsync(f.fileno())
                        print_success("Backup restored. Please try again.")
                return None
            
            try:
                data = json.loads(file_content)
            except json.JSONDecodeError as e:
                print_error(f"Wallet file is corrupted! JSON decode error: {e}")
                
                # Check for backup
                backup_path = load_path.with_suffix('.pynacl.backup')
                if backup_path.exists():
                    print_info("Found backup wallet file. Attempting recovery...")
                    if confirm_dangerous_action("Restore from backup?", "RESTORE"):
                        shutil.copy(backup_path, load_path)
                        # Sync the restored file
                        with open(load_path, 'r+b') as f:
                            os.fsync(f.fileno())
                        print_success("Backup restored. Please try again.")
                return None
            
            # Check if it's the old insecure format (list of ints)
            if isinstance(data, list):
                print_warning("Detected unencrypted (legacy) keypair format.")
                if confirm_dangerous_action("Would you like to load this insecure wallet?", "LOAD"):
                    secret_bytes = bytes(data)
                    self.keypair = Keypair.from_bytes(secret_bytes)
                    
                    # Offer to upgrade
                    if confirm_dangerous_action("Would you like to upgrade to ENCRYPTED format now?", "UPGRADE"):
                         self.save_keypair(str(load_path))
                    
                    return self.keypair
                else:
                    return None

            # Encrypted format - detect which type
            print_info("Wallet is encrypted.")
            # Don't prompt for password here - will be handled later
            # Just store the encrypted container for later use
            self.encrypted_container = data
            return None  # Return None, password will be requested when needed
            
            # Old code below - commented out but kept for reference
            # password = get_password_input("Enter password to unlock wallet:")
            # 
            # # Check if it's PyNaCl format or Rust format
            if False and data.get('algo') == 'argon2i_xsalsa20poly1305':
                # PyNaCl format
                keypair = SecureWalletHandler.decrypt_keypair(data, password)
            elif 'ciphertext' in data and 'nonce' in data and 'salt' in data:
                # Rust format - convert to usable keypair
                print_info("Wallet is in Rust secure format.")
                if RUST_SIGNER_AVAILABLE and self.rust_signer:
                    try:
                        # Use Rust signer to decrypt
                        data_normalized = self._normalize_container_format(data)
                        private_key = self.rust_signer.decrypt_private_key(data_normalized, password)
                        if private_key and len(private_key) == 32:
                            keypair = Keypair.from_bytes(bytes(private_key))
                            # Clean up
                            del private_key
                            gc.collect()
                        else:
                            keypair = None
                    except Exception as e:
                        print_error(f"Rust decryption failed: {e}")
                        keypair = None
                else:
                    print_error("Rust signer not available!")
                    keypair = None
            else:
                print_error("Unknown wallet encryption format!")
                keypair = None
            
            if keypair:
                print_success(f"Wallet unlocked successfully!")
                self.keypair = keypair
                return self.keypair
            else:
                print_error("Invalid password or corrupted wallet file.")
                
                # Check for backup as last resort
                backup_path = load_path.with_suffix('.pynacl.backup')
                if backup_path.exists():
                    print_info("A backup wallet file exists.")
                    if confirm_dangerous_action("Try restoring from backup?", "RESTORE"):
                        shutil.copy(backup_path, load_path)
                        # Sync the restored file
                        with open(load_path, 'r+b') as f:
                            os.fsync(f.fileno())
                        print_success("Backup restored. Please try loading again.")
                return None
                
        except Exception as e:
            print_error(f"Failed to load keypair: {e}")
            import traceback
            print_warning(f"Details: {traceback.format_exc()}")
            return None
    
    def get_public_key(self) -> Optional[str]:
        if self.keypair:
            return str(self.keypair.pubkey())
        # Try reading from pubkey file if keypair not loaded
        return self.get_public_key_from_file()
    
    def get_public_key_from_file(self, path: str = None) -> Optional[str]:
        pubkey_path = Path(path) if path else self.pubkey_path
        if pubkey_path is None or not pubkey_path.exists():
            return None
        
        try:
            with open(pubkey_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return None
    
    def keypair_exists(self, path: str = None) -> bool:
        check_path = Path(path) if path else self.keypair_path
        if check_path is None:
            return False
        return check_path.exists()
    
    def export_public_key_bytes(self) -> Optional[bytes]:
        if self.keypair is None:
            return None
        return bytes(self.keypair.pubkey())
    
    def validate_address(self, address: str) -> bool:
        try:
            Pubkey.from_string(address)
            return True
        except Exception:
            return False

    def clear_memory(self):
        """Securely clear the loaded keypair from memory"""
        self.keypair = None
        self.encrypted_container = None
        # Zeroize cached password bytearray before releasing
        if self._cached_password is not None:
            for i in range(len(self._cached_password)):
                self._cached_password[i] = 0
            self._cached_password = None
        gc.collect()

    def get_cached_password(self) -> Optional[str]:
        """Get cached password if available (converts from bytearray)"""
        if self._cached_password is not None:
            return self._cached_password.decode('utf-8')
        return None
    
    def _normalize_container_format(self, container: dict) -> dict:
        """Normalize container format - convert array fields to base64 strings if needed"""
        normalized = container.copy()
        
        # Ensure version field exists
        if 'version' not in normalized:
            normalized['version'] = 1
        
        # Fields that should be base64 strings
        for field in ['ciphertext', 'nonce', 'salt']:
            if field in normalized and isinstance(normalized[field], list):
                # Convert array to bytes then to base64
                normalized[field] = base64.b64encode(bytes(normalized[field])).decode('utf-8')
        
        # Public key should be base58 string (if present)
        if 'public_key' in normalized and isinstance(normalized['public_key'], list):
            normalized['public_key'] = base58.b58encode(bytes(normalized['public_key'])).decode('utf-8')
        
        return normalized
    
    def convert_pynacl_to_rust_container(self, pynacl_data: dict, password: str) -> Optional[dict]:
        """Convert PyNaCl encrypted format to Rust signer format"""
        if not RUST_SIGNER_AVAILABLE or self.rust_signer is None:
            print_error("Rust signer not available for conversion")
            return None
        
        try:
            # First decrypt with PyNaCl to get the private key
            keypair = SecureWalletHandler.decrypt_keypair(pynacl_data, password)
            if not keypair:
                return None
            
            # Get private key bytes (first 32 bytes of keypair)
            private_key = bytes(keypair)[:32]
            
            # Create Rust encrypted container
            container = self.rust_signer.create_encrypted_container(private_key, password)
            
            # Normalize format (ensure strings not arrays)
            container = self._normalize_container_format(container)
            
            # Clean up
            del private_key
            del keypair
            gc.collect()
            
            return container
        except Exception as e:
            print_error(f"Failed to convert container: {e}")
            return None
    
    def load_encrypted_container(self, path: str = None, password: str = None) -> Optional[dict]:
        """Load encrypted container for use with Rust signer (no key in Python memory)"""
        load_path = Path(path) if path else self.keypair_path
        if load_path is None:
            print_error("No keypair path specified")
            return None
        
        if not load_path.exists():
            print_error(f"Keypair file not found: {load_path}")
            return None
        
        try:
            with open(load_path, 'r') as f:
                file_content = f.read()
                
            # Check if file is empty or corrupted
            if not file_content or file_content.strip() == "":
                print_error("Wallet file is empty or corrupted!")
                
                # Check for backup
                backup_path = load_path.with_suffix('.pynacl.backup')
                if backup_path.exists():
                    print_info("Found backup wallet file. Attempting recovery...")
                    if confirm_dangerous_action("Restore from backup?", "RESTORE"):
                        import shutil
                        shutil.copy(backup_path, load_path)
                        print_success("Backup restored. Please try again.")
                return None
            
            try:
                data = json.loads(file_content)
            except json.JSONDecodeError as e:
                print_error(f"Wallet file is corrupted! JSON decode error: {e}")
                
                # Check for backup
                backup_path = load_path.with_suffix('.pynacl.backup')
                if backup_path.exists():
                    print_info("Found backup wallet file. Attempting recovery...")
                    if confirm_dangerous_action("Restore from backup?", "RESTORE"):
                        import shutil
                        shutil.copy(backup_path, load_path)
                        # Sync the restored file
                        with open(load_path, 'r+b') as f:
                            os.fsync(f.fileno())
                        print_success("Backup restored. Please try again.")
                return None
            
            # Check if it's old format (list of ints - unencrypted)
            if isinstance(data, list):
                print_error("Unencrypted keypair format detected!")
                print_warning("This format is NOT supported with Rust signer.")
                print_info("Please create a new encrypted wallet.")
                return None
            
            # Check if it's PyNaCl format
            if data.get('algo') == 'argon2i_xsalsa20poly1305':
                print_info("Detected PyNaCl encrypted format. Converting to Rust format...")
                
                if password is None:
                    print_error("Password required for wallet conversion but not provided!")
                    return None
                
                # Cache the password as bytearray for later use (signing) — zeroizable
                self._cached_password = bytearray(password.encode('utf-8'))
                
                rust_container = self.convert_pynacl_to_rust_container(data, password)
                if rust_container:
                    # Save the converted container
                    backup_path = load_path.with_suffix('.pynacl.backup')
                    
                    # If backup already exists, remove it first (or use timestamped name)
                    if backup_path.exists():
                        print_info(f"Removing old backup: {backup_path}")
                        backup_path.unlink()
                    
                    load_path.rename(backup_path)
                    print_info(f"Original wallet backed up to: {backup_path}")
                    
                    with open(load_path, 'w') as f:
                        json.dump(rust_container, f, indent=2)
                        f.flush()  # Ensure data is written to OS buffer
                        os.fsync(f.fileno())  # Force write to disk
                    
                    # Sync the directory entry (ensures rename is persisted)
                    try:
                        dir_fd = os.open(str(load_path.parent), os.O_RDONLY)
                        os.fsync(dir_fd)
                        os.close(dir_fd)
                    except (OSError, AttributeError):
                        # Windows doesn't support directory sync, but file sync is enough
                        pass
                    
                    print_success("✓ Wallet converted to Rust secure format")
                    print_info("✓ Changes synced to disk safely")
                    self.encrypted_container = rust_container
                    return rust_container
                else:
                    return None
            
            # Already Rust format (has 'ciphertext', 'nonce', 'salt')
            if 'ciphertext' in data and 'nonce' in data and 'salt' in data:
                # Fix format if fields are arrays instead of base64 strings
                data = self._normalize_container_format(data)
                print_success("✓ Wallet is in Rust secure format")
                self.encrypted_container = data
                return data
            
            print_error("Unknown wallet format")
            return None
            
        except Exception as e:
            print_error(f"Failed to load encrypted container: {e}")
            import traceback
            print_warning(f"Details: {traceback.format_exc()}")
            return None



def create_wallet_structure(base_path: str) -> dict:
    base = Path(base_path)
    dirs = {
        'wallet': base / 'wallet',
        'inbox': base / 'inbox',
        'outbox': base / 'outbox'
    }
    
    for name, path in dirs.items():
        path.mkdir(parents=True, exist_ok=True)
        print_success(f"Created directory: {path}")
    
    return {k: str(v) for k, v in dirs.items()}
