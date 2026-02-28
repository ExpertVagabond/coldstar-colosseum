"""
EVM Network Operations - RPC communication with Base (Coinbase L2)

Supports Base mainnet and Sepolia testnet via standard JSON-RPC.

B - Love U 3000
"""

from typing import Optional
import httpx

from config import (
    BASE_RPC_URL, BASE_TESTNET_RPC_URL,
    BASE_CHAIN_ID, BASE_TESTNET_CHAIN_ID,
    WEI_PER_ETH,
)
from src.ui import print_success, print_error, print_info, print_warning


class BaseNetwork:
    """JSON-RPC client for Base (Coinbase L2)."""

    def __init__(self, rpc_url: str = None, testnet: bool = False):
        if rpc_url:
            self.rpc_url = rpc_url
        else:
            self.rpc_url = BASE_TESTNET_RPC_URL if testnet else BASE_RPC_URL
        self.chain_id = BASE_TESTNET_CHAIN_ID if testnet else BASE_CHAIN_ID
        self.testnet = testnet
        self.client = httpx.Client(timeout=30.0)
        self._request_id = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    # ── Low-level RPC ───────────────────────────────────────

    def _make_rpc_request(self, method: str, params: list = None) -> dict:
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or [],
        }
        response = self.client.post(
            self.rpc_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    # ── Balance ─────────────────────────────────────────────

    def get_balance(self, address: str) -> Optional[float]:
        """Get ETH balance in ETH (not wei)."""
        try:
            result = self._make_rpc_request("eth_getBalance", [address, "latest"])
            if "error" in result:
                print_error(f"RPC Error: {result['error']['message']}")
                return None
            wei = int(result["result"], 16)
            return wei / WEI_PER_ETH
        except Exception as e:
            print_error(f"Error getting balance: {e}")
            return None

    def get_balance_wei(self, address: str) -> Optional[int]:
        """Get raw balance in wei."""
        try:
            result = self._make_rpc_request("eth_getBalance", [address, "latest"])
            if "error" in result:
                return None
            return int(result["result"], 16)
        except Exception:
            return None

    # ── Gas ─────────────────────────────────────────────────

    def get_gas_price(self) -> Optional[int]:
        """Get current gas price in wei."""
        try:
            result = self._make_rpc_request("eth_gasPrice")
            if "error" in result:
                return None
            return int(result["result"], 16)
        except Exception:
            return None

    def get_max_priority_fee(self) -> Optional[int]:
        """Get suggested max priority fee (tip) for EIP-1559."""
        try:
            result = self._make_rpc_request("eth_maxPriorityFeePerGas")
            if "error" in result:
                return None
            return int(result["result"], 16)
        except Exception:
            return None

    def get_base_fee(self) -> Optional[int]:
        """Get current base fee from latest block."""
        try:
            result = self._make_rpc_request("eth_getBlockByNumber", ["latest", False])
            if "error" in result or not result.get("result"):
                return None
            return int(result["result"]["baseFeePerGas"], 16)
        except Exception:
            return None

    def estimate_gas(self, tx_params: dict) -> Optional[int]:
        """Estimate gas for a transaction."""
        try:
            result = self._make_rpc_request("eth_estimateGas", [tx_params])
            if "error" in result:
                print_error(f"Gas estimation error: {result['error']['message']}")
                return None
            return int(result["result"], 16)
        except Exception as e:
            print_error(f"Gas estimation failed: {e}")
            return None

    # ── Nonce ───────────────────────────────────────────────

    def get_nonce(self, address: str) -> Optional[int]:
        """Get the transaction count (nonce) for an address."""
        try:
            result = self._make_rpc_request("eth_getTransactionCount", [address, "latest"])
            if "error" in result:
                return None
            return int(result["result"], 16)
        except Exception:
            return None

    # ── Transaction ─────────────────────────────────────────

    def send_raw_transaction(self, signed_tx_hex: str) -> Optional[str]:
        """Broadcast a signed transaction. Returns tx hash."""
        try:
            if not signed_tx_hex.startswith("0x"):
                signed_tx_hex = "0x" + signed_tx_hex
            result = self._make_rpc_request("eth_sendRawTransaction", [signed_tx_hex])
            if "error" in result:
                print_error(f"Transaction failed: {result['error']['message']}")
                return None
            tx_hash = result.get("result")
            if tx_hash:
                print_success("Transaction sent successfully!")
                print_info(f"Tx hash: {tx_hash}")
            return tx_hash
        except Exception as e:
            print_error(f"Error sending transaction: {e}")
            return None

    def get_transaction_receipt(self, tx_hash: str) -> Optional[dict]:
        """Get transaction receipt (None if pending)."""
        try:
            result = self._make_rpc_request("eth_getTransactionReceipt", [tx_hash])
            if "error" in result:
                return None
            return result.get("result")
        except Exception:
            return None

    def wait_for_receipt(self, tx_hash: str, max_retries: int = 60) -> Optional[dict]:
        """Wait for transaction confirmation."""
        import time
        for _ in range(max_retries):
            receipt = self.get_transaction_receipt(tx_hash)
            if receipt:
                status = int(receipt.get("status", "0x0"), 16)
                if status == 1:
                    print_success("Transaction confirmed!")
                    return receipt
                else:
                    print_error("Transaction reverted!")
                    return receipt
            time.sleep(1)
        print_warning("Transaction not confirmed within timeout")
        return None

    # ── ERC-20 ──────────────────────────────────────────────

    def get_erc20_balance(self, token_address: str, wallet_address: str) -> Optional[int]:
        """Get ERC-20 token balance (raw units)."""
        # balanceOf(address) selector: 0x70a08231
        padded_addr = wallet_address[2:].lower().zfill(64)
        data = "0x70a08231" + padded_addr
        try:
            result = self._make_rpc_request("eth_call", [
                {"to": token_address, "data": data},
                "latest"
            ])
            if "error" in result:
                return None
            return int(result["result"], 16)
        except Exception:
            return None

    # ── Chain info ──────────────────────────────────────────

    def get_block_number(self) -> Optional[int]:
        try:
            result = self._make_rpc_request("eth_blockNumber")
            if "error" in result:
                return None
            return int(result["result"], 16)
        except Exception:
            return None

    def is_connected(self) -> bool:
        try:
            result = self._make_rpc_request("eth_chainId")
            chain_id = int(result.get("result", "0x0"), 16)
            return chain_id == self.chain_id
        except Exception:
            return False

    def get_network_info(self) -> dict:
        try:
            chain_result = self._make_rpc_request("eth_chainId")
            block_result = self._make_rpc_request("eth_blockNumber")
            gas_result = self._make_rpc_request("eth_gasPrice")

            chain_id = int(chain_result.get("result", "0x0"), 16)
            block = int(block_result.get("result", "0x0"), 16)
            gas_price = int(gas_result.get("result", "0x0"), 16)

            return {
                "chain": "Base" + (" Sepolia" if self.testnet else ""),
                "chain_id": chain_id,
                "block_number": block,
                "gas_price_gwei": gas_price / 10**9,
                "rpc_url": self.rpc_url,
            }
        except Exception:
            return {"error": "Could not fetch network info"}

    def get_transaction_history(self, address: str, limit: int = 10) -> Optional[list]:
        """Base doesn't have a native tx history RPC. Returns None (use explorer API)."""
        print_warning("Base RPC does not support transaction history directly.")
        print_info("Use BaseScan API or companion app for history.")
        return None

    # ── Explorer links ──────────────────────────────────────

    def explorer_url(self, tx_hash: str) -> str:
        if self.testnet:
            return f"https://sepolia.basescan.org/tx/{tx_hash}"
        return f"https://basescan.org/tx/{tx_hash}"

    def explorer_address_url(self, address: str) -> str:
        if self.testnet:
            return f"https://sepolia.basescan.org/address/{address}"
        return f"https://basescan.org/address/{address}"

    # ── Cleanup ─────────────────────────────────────────────

    def close(self):
        self.client.close()
