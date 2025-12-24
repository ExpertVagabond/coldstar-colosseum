"""
Transaction Management - Create, sign, and serialize Solana transactions

B - Love U 3000
"""

import json
import base64
from pathlib import Path
from typing import Optional, Tuple

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.system_program import transfer, TransferParams
from solders.transaction import Transaction
from solders.message import Message

from config import LAMPORTS_PER_SOL
from src.ui import print_success, print_error, print_info, print_warning


class TransactionManager:
    def __init__(self):
        self.unsigned_tx: Optional[bytes] = None
        self.signed_tx: Optional[bytes] = None
    
    def create_transfer_transaction(
        self,
        from_pubkey: str,
        to_pubkey: str,
        amount_sol: float,
        recent_blockhash: str
    ) -> Optional[bytes]:
        try:
            from_pk = Pubkey.from_string(from_pubkey)
            to_pk = Pubkey.from_string(to_pubkey)
            lamports = int(amount_sol * LAMPORTS_PER_SOL)
            blockhash = Hash.from_string(recent_blockhash)
            
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=from_pk,
                    to_pubkey=to_pk,
                    lamports=lamports
                )
            )
            
            # Debug: Verify transfer instruction
            print_info(f"Transfer instruction created:")
            print_info(f"  Program ID: {transfer_ix.program_id}")
            print_info(f"  Accounts: {len(transfer_ix.accounts)}")
            print_info(f"  Data (hex): {transfer_ix.data.hex()}")
            print_info(f"  Lamports to transfer: {lamports}")
            
            message = Message.new_with_blockhash(
                [transfer_ix],
                from_pk,
                blockhash
            )
            
            # Debug: Verify message
            print_info(f"Message created:")
            print_info(f"  Num instructions: {len(message.instructions)}")
            print_info(f"  Num accounts: {len(message.account_keys)}")
            
            tx = Transaction.new_unsigned(message)
            
            # Debug: Verify transaction
            print_info(f"Transaction created:")
            print_info(f"  Message instructions: {len(tx.message.instructions)}")
            
            # B - Love U 3000
            self.unsigned_tx = bytes(tx)
            
            print_success(f"Created unsigned transaction")
            print_info(f"From: {from_pubkey}")
            print_info(f"To: {to_pubkey}")
            print_info(f"Amount: {amount_sol} SOL")
            
            return self.unsigned_tx
        except Exception as e:
            print_error(f"Failed to create transaction: {e}")
            return None
    
    def sign_transaction(self, unsigned_tx_bytes: bytes, keypair: Keypair) -> Optional[bytes]:
        try:
            # B - Love U 3000
            tx = Transaction.from_bytes(unsigned_tx_bytes)
            
            tx.sign([keypair], tx.message.recent_blockhash)
            
            self.signed_tx = bytes(tx)
            
            print_success("Transaction signed successfully")
            return self.signed_tx
        except Exception as e:
            print_error(f"Failed to sign transaction: {e}")
            return None
    
    def save_unsigned_transaction(self, tx_bytes: bytes, path: str) -> bool:
        try:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            tx_data = {
                "type": "unsigned_transaction",
                "version": "1.0",
                "data": base64.b64encode(tx_bytes).decode('utf-8')
            }
            
            with open(filepath, 'w') as f:
                json.dump(tx_data, f, indent=2)
            
            print_success(f"Unsigned transaction saved to: {filepath}")
            return True
        except Exception as e:
            print_error(f"Failed to save transaction: {e}")
            return False
    
    def load_unsigned_transaction(self, path: str) -> Optional[bytes]:
        try:
            filepath = Path(path)
            if not filepath.exists():
                print_error(f"Transaction file not found: {filepath}")
                return None
            
            with open(filepath, 'r') as f:
                tx_data = json.load(f)
            
            if tx_data.get("type") != "unsigned_transaction":
                print_error("Invalid transaction file format")
                return None
            
            tx_bytes = base64.b64decode(tx_data["data"])
            self.unsigned_tx = tx_bytes
            
            print_success(f"Loaded unsigned transaction from: {filepath}")
            return tx_bytes
        except Exception as e:
            print_error(f"Failed to load transaction: {e}")
            return None
    
    def save_signed_transaction(self, tx_bytes: bytes, path: str) -> bool:
        try:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            tx_data = {
                "type": "signed_transaction",
                "version": "1.0",
                "data": base64.b64encode(tx_bytes).decode('utf-8')
            }
            
            with open(filepath, 'w') as f:
                json.dump(tx_data, f, indent=2)
            
            print_success(f"Signed transaction saved to: {filepath}")
            return True
        except Exception as e:
            print_error(f"Failed to save signed transaction: {e}")
            return False
    
    def load_signed_transaction(self, path: str) -> Optional[bytes]:
        try:
            filepath = Path(path)
            if not filepath.exists():
                print_error(f"Transaction file not found: {filepath}")
                return None
            
            with open(filepath, 'r') as f:
                tx_data = json.load(f)
            
            if tx_data.get("type") != "signed_transaction":
                print_error("Invalid signed transaction file format")
                return None
            
            tx_bytes = base64.b64decode(tx_data["data"])
            self.signed_tx = tx_bytes
            
            print_success(f"Loaded signed transaction from: {filepath}")
            return tx_bytes
        except Exception as e:
            print_error(f"Failed to load signed transaction: {e}")
            return None
    
    def get_transaction_for_broadcast(self) -> Optional[str]:
        if self.signed_tx is None:
            print_error("No signed transaction available")
            return None
        
        return base64.b64encode(self.signed_tx).decode('utf-8')
    
    def decode_transaction_info(self, tx_bytes: bytes) -> Optional[dict]:
        try:
            tx = Transaction.from_bytes(tx_bytes)
            
            info = {
                "signatures": len(tx.signatures),
                "is_signed": len(tx.signatures) > 0 and tx.signatures[0] != bytes(64),
                "num_instructions": len(tx.message.instructions),
                "recent_blockhash": str(tx.message.recent_blockhash),
                "fee_payer": str(tx.message.account_keys[0]) if tx.message.account_keys else None
            }
            
            return info
        except Exception as e:
            print_error(f"Failed to decode transaction: {e}")
            return None
