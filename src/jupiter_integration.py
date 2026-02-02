"""
Jupiter DEX Integration - Secure cold wallet swaps via air-gap
Enables creating unsigned swap transactions for QR-based signing

B - Love U 3000
"""

import json
import base64
import httpx
from pathlib import Path
from typing import Optional, Dict, Any, List
from decimal import Decimal

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import to_bytes_versioned

from src.ui import print_success, print_error, print_info, print_warning


# Jupiter API V6 endpoints
JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"
JUPITER_PRICE_API = "https://price.jup.ag/v4/price"

# Common token addresses
TOKENS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
}


class JupiterSwapManager:
    """Manages Jupiter swap operations for air-gapped cold wallets"""

    def __init__(self, slippage_bps: int = 50):
        """
        Initialize Jupiter swap manager

        Args:
            slippage_bps: Slippage tolerance in basis points (50 = 0.5%)
        """
        self.slippage_bps = slippage_bps
        self.client = httpx.Client(timeout=30.0)

    def get_token_address(self, symbol: str) -> Optional[str]:
        """Get token mint address from symbol"""
        symbol_upper = symbol.upper()
        if symbol_upper in TOKENS:
            return TOKENS[symbol_upper]
        return symbol  # Assume it's already a mint address

    def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get swap quote from Jupiter

        Args:
            input_mint: Input token mint address or symbol
            output_mint: Output token mint address or symbol
            amount: Amount in smallest unit (lamports for SOL)
            slippage_bps: Optional override for slippage

        Returns:
            Quote data or None on error
        """
        try:
            input_addr = self.get_token_address(input_mint)
            output_addr = self.get_token_address(output_mint)
            slippage = slippage_bps or self.slippage_bps

            print_info(f"Fetching quote from Jupiter...")
            print_info(f"  Input: {input_mint} ({input_addr[:8]}...)")
            print_info(f"  Output: {output_mint} ({output_addr[:8]}...)")
            print_info(f"  Amount: {amount}")

            params = {
                "inputMint": input_addr,
                "outputMint": output_addr,
                "amount": str(amount),
                "slippageBps": str(slippage),
                "onlyDirectRoutes": "false",
                "asLegacyTransaction": "false"
            }

            response = self.client.get(JUPITER_QUOTE_API, params=params)
            response.raise_for_status()

            quote = response.json()

            if "error" in quote:
                print_error(f"Jupiter API error: {quote['error']}")
                return None

            # Display quote info
            in_amount = int(quote.get("inAmount", 0))
            out_amount = int(quote.get("outAmount", 0))
            price_impact = quote.get("priceImpactPct", 0)

            print_success("Quote received!")
            print_info(f"  Input amount: {in_amount}")
            print_info(f"  Expected output: {out_amount}")
            print_info(f"  Price impact: {price_impact}%")
            print_info(f"  Route: {len(quote.get('routePlan', []))} steps")

            if float(price_impact) > 1.0:
                print_warning(f"High price impact: {price_impact}%")

            return quote

        except httpx.HTTPError as e:
            print_error(f"HTTP error fetching quote: {e}")
            return None
        except Exception as e:
            print_error(f"Failed to get quote: {e}")
            return None

    def create_swap_transaction(
        self,
        quote: Dict[str, Any],
        user_pubkey: str,
        wrap_unwrap_sol: bool = True,
        priority_fee: Optional[int] = None
    ) -> Optional[bytes]:
        """
        Create unsigned swap transaction from quote

        Args:
            quote: Quote data from get_quote()
            user_pubkey: User's public key (wallet address)
            wrap_unwrap_sol: Auto wrap/unwrap SOL
            priority_fee: Optional priority fee in lamports

        Returns:
            Unsigned transaction bytes or None on error
        """
        try:
            print_info("Creating swap transaction...")

            # Prepare swap request
            swap_request = {
                "quoteResponse": quote,
                "userPublicKey": user_pubkey,
                "wrapAndUnwrapSol": wrap_unwrap_sol,
                "dynamicComputeUnitLimit": True,
                "prioritizationFeeLamports": priority_fee or "auto"
            }

            response = self.client.post(
                JUPITER_SWAP_API,
                json=swap_request,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            swap_data = response.json()

            if "error" in swap_data:
                print_error(f"Swap API error: {swap_data['error']}")
                return None

            # Get the serialized transaction
            swap_tx_base64 = swap_data.get("swapTransaction")
            if not swap_tx_base64:
                print_error("No transaction returned from Jupiter")
                return None

            # Decode the transaction
            tx_bytes = base64.b64decode(swap_tx_base64)

            print_success("Unsigned swap transaction created!")
            print_info(f"  Transaction size: {len(tx_bytes)} bytes")

            return tx_bytes

        except httpx.HTTPError as e:
            print_error(f"HTTP error creating swap: {e}")
            return None
        except Exception as e:
            print_error(f"Failed to create swap transaction: {e}")
            return None

    def get_price(self, token_ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        Get current prices for tokens

        Args:
            token_ids: List of token mint addresses or symbols

        Returns:
            Price data or None on error
        """
        try:
            # Convert symbols to addresses
            addresses = [self.get_token_address(tid) for tid in token_ids]

            params = {
                "ids": ",".join(addresses)
            }

            response = self.client.get(JUPITER_PRICE_API, params=params)
            response.raise_for_status()

            prices = response.json()

            if "data" not in prices:
                print_error("No price data returned")
                return None

            return prices["data"]

        except Exception as e:
            print_error(f"Failed to get prices: {e}")
            return None

    def save_swap_transaction(
        self,
        tx_bytes: bytes,
        path: str,
        quote_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save unsigned swap transaction to file

        Args:
            tx_bytes: Transaction bytes
            path: File path to save to
            quote_info: Optional quote information for reference

        Returns:
            True on success
        """
        try:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            tx_data = {
                "type": "jupiter_swap_unsigned",
                "version": "1.0",
                "transaction": base64.b64encode(tx_bytes).decode('utf-8'),
                "quote_info": quote_info or {}
            }

            with open(filepath, 'w') as f:
                json.dump(tx_data, f, indent=2)

            print_success(f"Swap transaction saved to: {filepath}")
            return True

        except Exception as e:
            print_error(f"Failed to save swap transaction: {e}")
            return False

    def load_swap_transaction(self, path: str) -> Optional[tuple[bytes, Dict]]:
        """
        Load unsigned swap transaction from file

        Args:
            path: File path to load from

        Returns:
            Tuple of (transaction bytes, quote info) or None on error
        """
        try:
            filepath = Path(path)
            if not filepath.exists():
                print_error(f"Transaction file not found: {filepath}")
                return None

            with open(filepath, 'r') as f:
                tx_data = json.load(f)

            if tx_data.get("type") != "jupiter_swap_unsigned":
                print_error("Invalid Jupiter swap transaction file")
                return None

            tx_bytes = base64.b64decode(tx_data["transaction"])
            quote_info = tx_data.get("quote_info", {})

            print_success(f"Loaded swap transaction from: {filepath}")

            # Display swap details
            if quote_info:
                print_info("Swap Details:")
                print_info(f"  Input amount: {quote_info.get('inAmount', 'N/A')}")
                print_info(f"  Expected output: {quote_info.get('outAmount', 'N/A')}")
                print_info(f"  Price impact: {quote_info.get('priceImpactPct', 'N/A')}%")

            return (tx_bytes, quote_info)

        except Exception as e:
            print_error(f"Failed to load swap transaction: {e}")
            return None

    def sign_swap_transaction(
        self,
        tx_bytes: bytes,
        keypair: Keypair
    ) -> Optional[bytes]:
        """
        Sign swap transaction (for air-gapped device)

        Args:
            tx_bytes: Unsigned transaction bytes
            keypair: Keypair to sign with

        Returns:
            Signed transaction bytes or None on error
        """
        try:
            # Deserialize versioned transaction
            tx = VersionedTransaction.from_bytes(tx_bytes)

            # Sign the transaction
            tx.sign([keypair])

            # Serialize back to bytes
            signed_bytes = bytes(tx)

            print_success("Swap transaction signed successfully!")
            return signed_bytes

        except Exception as e:
            print_error(f"Failed to sign swap transaction: {e}")
            return None

    def save_signed_swap(self, tx_bytes: bytes, path: str) -> bool:
        """Save signed swap transaction"""
        try:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            tx_data = {
                "type": "jupiter_swap_signed",
                "version": "1.0",
                "transaction": base64.b64encode(tx_bytes).decode('utf-8')
            }

            with open(filepath, 'w') as f:
                json.dump(tx_data, f, indent=2)

            print_success(f"Signed swap saved to: {filepath}")
            return True

        except Exception as e:
            print_error(f"Failed to save signed swap: {e}")
            return False

    def get_swap_summary(
        self,
        input_symbol: str,
        output_symbol: str,
        input_amount: float,
        output_amount: float,
        price_impact: float,
        route_steps: int
    ) -> str:
        """Generate human-readable swap summary"""
        summary = f"""
╔══════════════════════════════════════════════════════════╗
║                    SWAP TRANSACTION                      ║
╠══════════════════════════════════════════════════════════╣
║  From:          {input_amount:.6f} {input_symbol:<30} ║
║  To:            {output_amount:.6f} {output_symbol:<30} ║
║  Price Impact:  {price_impact:.2f}%{' '*35}║
║  Route:         {route_steps} step(s){' '*34}║
╚══════════════════════════════════════════════════════════╝
        """
        return summary.strip()

    def __del__(self):
        """Cleanup HTTP client"""
        try:
            self.client.close()
        except:
            pass


def sol_to_lamports(sol: float) -> int:
    """Convert SOL to lamports"""
    return int(sol * 1_000_000_000)


def lamports_to_sol(lamports: int) -> float:
    """Convert lamports to SOL"""
    return lamports / 1_000_000_000


def tokens_to_smallest_unit(amount: float, decimals: int) -> int:
    """Convert token amount to smallest unit"""
    return int(amount * (10 ** decimals))


def smallest_unit_to_tokens(amount: int, decimals: int) -> float:
    """Convert smallest unit to token amount"""
    return amount / (10 ** decimals)
