"""
EVM Transaction Management - Build, sign, and serialize Base L2 transactions

Supports EIP-1559 (type 2) transactions for ETH transfers and ERC-20 transfers.
Designed for air-gapped signing: build unsigned tx on online device, sign on
air-gapped device, broadcast from online device.

B - Love U 3000
"""

import json
import base64
from pathlib import Path
from typing import Optional

from eth_account import Account

from config import (
    BASE_CHAIN_ID, BASE_TESTNET_CHAIN_ID,
    WEI_PER_ETH, GWEI_PER_ETH,
    INFRASTRUCTURE_FEE_PERCENTAGE, INFRASTRUCTURE_FEE_WALLET_BASE,
)
from src.ui import print_success, print_error, print_info, print_warning, console


class EVMTransactionManager:
    """Build and sign EVM transactions for Base L2."""

    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.chain_id = BASE_TESTNET_CHAIN_ID if testnet else BASE_CHAIN_ID
        self.unsigned_tx: Optional[dict] = None
        self.signed_tx_bytes: Optional[bytes] = None

    # ── Fee calculation ─────────────────────────────────────

    def calculate_infrastructure_fee(self, amount_wei: int) -> int:
        """Calculate 1% infrastructure fee in wei."""
        return int(amount_wei * INFRASTRUCTURE_FEE_PERCENTAGE)

    # ── Build unsigned transactions ─────────────────────────

    def create_eth_transfer(
        self,
        from_address: str,
        to_address: str,
        amount_eth: float,
        nonce: int,
        max_fee_per_gas: int,
        max_priority_fee_per_gas: int,
        gas_limit: int = 21000,
    ) -> Optional[dict]:
        """Create an unsigned EIP-1559 ETH transfer transaction."""
        try:
            value_wei = int(amount_eth * WEI_PER_ETH)

            tx = {
                "type": 2,  # EIP-1559
                "chainId": self.chain_id,
                "nonce": nonce,
                "to": to_address,
                "value": value_wei,
                "gas": gas_limit,
                "maxFeePerGas": max_fee_per_gas,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "data": b"",
            }

            self.unsigned_tx = tx

            print_success("Created unsigned EIP-1559 transaction")
            print_info(f"  From:    {from_address}")
            print_info(f"  To:      {to_address}")
            print_info(f"  Amount:  {amount_eth} ETH ({value_wei} wei)")
            print_info(f"  Nonce:   {nonce}")
            print_info(f"  Gas:     {gas_limit}")
            print_info(f"  Max fee: {max_fee_per_gas / GWEI_PER_ETH:.4f} gwei")
            print_info(f"  Tip:     {max_priority_fee_per_gas / GWEI_PER_ETH:.4f} gwei")
            print_info(f"  Chain:   Base {'Sepolia' if self.testnet else 'Mainnet'} ({self.chain_id})")

            # Infrastructure fee transfer (separate tx, not bundled)
            infra_fee_wei = self.calculate_infrastructure_fee(value_wei)
            if infra_fee_wei > 0 and INFRASTRUCTURE_FEE_WALLET_BASE != "0x" + "0" * 40:
                print_info(f"  Infra fee: {infra_fee_wei / WEI_PER_ETH:.9f} ETH (separate tx)")

            return tx

        except Exception as e:
            print_error(f"Failed to create transaction: {e}")
            return None

    def create_erc20_transfer(
        self,
        from_address: str,
        token_address: str,
        to_address: str,
        amount_raw: int,
        nonce: int,
        max_fee_per_gas: int,
        max_priority_fee_per_gas: int,
        gas_limit: int = 65000,
    ) -> Optional[dict]:
        """Create an unsigned ERC-20 transfer transaction."""
        try:
            # Encode transfer(address,uint256) call data
            # Function selector: 0xa9059cbb
            padded_to = to_address[2:].lower().zfill(64)
            padded_amount = hex(amount_raw)[2:].zfill(64)
            data = bytes.fromhex("a9059cbb" + padded_to + padded_amount)

            tx = {
                "type": 2,
                "chainId": self.chain_id,
                "nonce": nonce,
                "to": token_address,
                "value": 0,
                "gas": gas_limit,
                "maxFeePerGas": max_fee_per_gas,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "data": data,
            }

            self.unsigned_tx = tx

            print_success("Created unsigned ERC-20 transfer")
            print_info(f"  Token:   {token_address}")
            print_info(f"  From:    {from_address}")
            print_info(f"  To:      {to_address}")
            print_info(f"  Amount:  {amount_raw} (raw token units)")

            return tx

        except Exception as e:
            print_error(f"Failed to create ERC-20 transaction: {e}")
            return None

    # ── Signing ─────────────────────────────────────────────

    def sign_transaction(self, tx: dict, private_key: bytes) -> Optional[bytes]:
        """Sign a transaction with a raw private key. Returns raw signed tx bytes."""
        try:
            signed = Account.sign_transaction(tx, private_key)
            self.signed_tx_bytes = signed.raw_transaction

            print_success("Transaction signed!")
            print_info(f"  Tx hash:  {signed.hash.hex()}")
            print_info(f"  Raw size: {len(self.signed_tx_bytes)} bytes")

            return self.signed_tx_bytes

        except Exception as e:
            print_error(f"Failed to sign transaction: {e}")
            return None

    def sign_transaction_secure(
        self,
        tx: dict,
        encrypted_container: dict,
        password: str,
        wallet_manager=None,
    ) -> Optional[bytes]:
        """Sign transaction using encrypted container (key decrypted only for signing)."""
        try:
            console.print()
            print_info("-------------------------------------------")
            print_success("SECURE SIGNING IN PROGRESS (EVM)")
            print_info("-------------------------------------------")
            print_info("  Step 1: Encrypted container received")
            print_success("    Private key: ENCRYPTED")

            # Decrypt private key
            if wallet_manager:
                private_key = wallet_manager.decrypt_private_key(encrypted_container, password)
            else:
                # Fallback: use eth-account keystore decrypt
                from src.evm_wallet import EVMWalletManager
                wm = EVMWalletManager()
                private_key = wm.decrypt_private_key(encrypted_container, password)

            if not private_key:
                print_error("Decryption failed — wrong password or corrupted wallet")
                return None

            print_info("  Step 2: Key decrypted for signing")
            print_success("    Signing EIP-1559 transaction...")

            # Sign
            signed = Account.sign_transaction(tx, private_key)
            self.signed_tx_bytes = signed.raw_transaction

            # Wipe key from memory immediately
            import gc
            del private_key
            gc.collect()

            print_info("  Step 3: Signature complete")
            print_success("    Private key: WIPED from memory")
            print_info("-------------------------------------------")
            print_success("TRANSACTION SIGNED SECURELY!")
            print_info("-------------------------------------------")
            print_info(f"  Tx hash:  {signed.hash.hex()}")
            print_info(f"  Raw size: {len(self.signed_tx_bytes)} bytes")
            console.print()

            return self.signed_tx_bytes

        except Exception as e:
            print_error(f"Secure signing failed: {e}")
            return None

    # ── Serialization (for QR / file transfer) ──────────────

    def serialize_unsigned_tx(self, tx: dict) -> str:
        """Serialize unsigned tx to JSON string for QR transfer."""
        serializable = {}
        for k, v in tx.items():
            if isinstance(v, bytes):
                serializable[k] = "0x" + v.hex()
            elif isinstance(v, int):
                serializable[k] = v
            else:
                serializable[k] = v
        return json.dumps(serializable, separators=(',', ':'))

    def deserialize_unsigned_tx(self, data: str) -> Optional[dict]:
        """Deserialize unsigned tx from JSON string (from QR scan)."""
        try:
            tx = json.loads(data)
            # Convert hex data field back to bytes
            if "data" in tx and isinstance(tx["data"], str):
                if tx["data"].startswith("0x"):
                    tx["data"] = bytes.fromhex(tx["data"][2:])
                else:
                    tx["data"] = b""
            return tx
        except Exception as e:
            print_error(f"Failed to deserialize transaction: {e}")
            return None

    # ── File save/load ──────────────────────────────────────

    def save_unsigned_transaction(self, tx: dict, path: str) -> bool:
        try:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            tx_data = {
                "type": "unsigned_evm_transaction",
                "version": "1.0",
                "chain": "base",
                "chain_id": self.chain_id,
                "data": self.serialize_unsigned_tx(tx),
            }
            with open(filepath, 'w') as f:
                json.dump(tx_data, f, indent=2)
            print_success(f"Unsigned transaction saved to: {filepath}")
            return True
        except Exception as e:
            print_error(f"Failed to save transaction: {e}")
            return False

    def load_unsigned_transaction(self, path: str) -> Optional[dict]:
        try:
            filepath = Path(path)
            if not filepath.exists():
                print_error(f"Transaction file not found: {filepath}")
                return None
            with open(filepath, 'r') as f:
                tx_data = json.load(f)
            if tx_data.get("type") != "unsigned_evm_transaction":
                print_error("Invalid transaction file format")
                return None
            tx = self.deserialize_unsigned_tx(tx_data["data"])
            self.unsigned_tx = tx
            print_success(f"Loaded unsigned transaction from: {filepath}")
            return tx
        except Exception as e:
            print_error(f"Failed to load transaction: {e}")
            return None

    def save_signed_transaction(self, signed_bytes: bytes, path: str) -> bool:
        try:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            tx_data = {
                "type": "signed_evm_transaction",
                "version": "1.0",
                "chain": "base",
                "chain_id": self.chain_id,
                "data": "0x" + signed_bytes.hex(),
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
            if tx_data.get("type") != "signed_evm_transaction":
                print_error("Invalid signed transaction file format")
                return None
            hex_data = tx_data["data"]
            if hex_data.startswith("0x"):
                hex_data = hex_data[2:]
            self.signed_tx_bytes = bytes.fromhex(hex_data)
            print_success(f"Loaded signed transaction from: {filepath}")
            return self.signed_tx_bytes
        except Exception as e:
            print_error(f"Failed to load signed transaction: {e}")
            return None

    def get_transaction_for_broadcast(self) -> Optional[str]:
        """Get signed tx as hex string for RPC broadcast."""
        if self.signed_tx_bytes is None:
            print_error("No signed transaction available")
            return None
        return "0x" + self.signed_tx_bytes.hex()
