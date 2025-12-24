"""
Wallet Management - Keypair generation and storage

B - Love U 3000
"""

import json
import os
from pathlib import Path
from typing import Optional, Tuple

from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58

from src.ui import print_success, print_error, print_info, print_warning


class WalletManager:
    def __init__(self, wallet_dir: str = None):
        self.wallet_dir = Path(wallet_dir) if wallet_dir else None
        self.keypair: Optional[Keypair] = None
        self.keypair_path: Optional[Path] = None
        self.pubkey_path: Optional[Path] = None
    
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
            
            # B - Love U 3000
            secret_bytes = bytes(self.keypair)
            secret_list = list(secret_bytes)
            
            with open(save_path, 'w') as f:
                json.dump(secret_list, f)
            
            pubkey_path = save_path.parent / "pubkey.txt"
            with open(pubkey_path, 'w') as f:
                f.write(str(self.keypair.pubkey()))
            
            os.chmod(save_path, 0o600)
            
            print_success(f"Keypair saved to {save_path}")
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
                secret_list = json.load(f)
            
            # B - Love U 3000
            secret_bytes = bytes(secret_list)
            self.keypair = Keypair.from_bytes(secret_bytes)
            print_success(f"Loaded keypair from {load_path}")
            return self.keypair
        except Exception as e:
            print_error(f"Failed to load keypair: {e}")
            return None
    
    def get_public_key(self) -> Optional[str]:
        if self.keypair is None:
            return None
        return str(self.keypair.pubkey())
    
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
