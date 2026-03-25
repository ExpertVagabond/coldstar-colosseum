"""
Solana Developer Platform (SDP) Integration — Enterprise stablecoin, payment,
and trading APIs for air-gapped cold wallet operations.

SDP is Solana Foundation's enterprise API platform (launched March 2026) with:
- Issuance API: Create/manage stablecoins, tokenized deposits, RWAs
- Payments API: Fiat on-ramp, off-ramp, stablecoin transfers
- Trading API: Atomic swaps, vaults, onchain FX
"""

import json
import os
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

import httpx

from config import sanitize_error
from src.ui import print_success, print_error, print_info, print_warning


# ── Configuration ────────────────────────────────────────────

SDP_API_URL = os.environ.get("SDP_API_URL", "https://api.platform.solana.com")
SDP_API_KEY = os.environ.get("SDP_API_KEY", "")
SDP_NETWORK = os.environ.get("SDP_NETWORK", "devnet")

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 1.5  # seconds, exponential backoff


# ── Data Models ──────────────────────────────────────────────

class SdpNetwork(str, Enum):
    DEVNET = "devnet"
    MAINNET = "mainnet-beta"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StablecoinInfo:
    """SDP stablecoin token details."""
    token_id: str
    name: str
    symbol: str
    decimals: int
    issuer: str
    total_supply: float = 0.0
    mint_authority: str = ""
    freeze_authority: str = ""


@dataclass
class PaymentResult:
    """Result of an on-ramp, off-ramp, or transfer operation."""
    payment_id: str
    status: PaymentStatus
    amount: float
    currency: str
    wallet: str = ""
    tx_signature: str = ""
    created_at: float = 0.0
    completed_at: float = 0.0
    fee: float = 0.0


@dataclass
class SwapQuote:
    """SDP trading swap quote."""
    quote_id: str
    from_token: str
    to_token: str
    from_amount: float
    to_amount: float
    exchange_rate: float
    price_impact: float = 0.0
    fee: float = 0.0
    expires_at: float = 0.0
    route: List[str] = field(default_factory=list)


@dataclass
class Vault:
    """SDP trading vault."""
    vault_id: str
    name: str
    owner: str
    token: str
    balance: float = 0.0
    status: str = "active"
    created_at: float = 0.0
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FxRate:
    """Foreign exchange rate."""
    from_currency: str
    to_currency: str
    rate: float
    timestamp: float = 0.0
    source: str = "sdp"


@dataclass
class FeeEstimate:
    """Fee estimation for a payment operation."""
    amount: float
    currency: str
    network_fee: float = 0.0
    platform_fee: float = 0.0
    total_fee: float = 0.0


# ── HTTP Client ──────────────────────────────────────────────

class SdpClient:
    """HTTP client for Solana Developer Platform APIs.

    Handles authentication, retries with exponential backoff,
    and structured error handling for all SDP endpoints.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        network: Optional[str] = None,
    ):
        self.base_url = (base_url or SDP_API_URL).rstrip("/")
        self.api_key = api_key or SDP_API_KEY
        self.network = network or SDP_NETWORK
        self.client = httpx.Client(timeout=30.0)

        if not self.api_key:
            print_warning("SDP_API_KEY not set. Set it via environment variable.")

    # ── Low-level request helpers ────────────────────────────

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-SDP-Network": self.network,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Execute an HTTP request with retry logic and error handling."""
        url = f"{self.base_url}{path}"

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.client.request(
                    method,
                    url,
                    headers=self._headers(),
                    params=params,
                    json=json_body,
                )

                if response.status_code == 429:
                    wait = RETRY_BACKOFF_BASE ** attempt
                    print_warning(f"Rate limited, retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
                    continue

                if response.status_code >= 500:
                    wait = RETRY_BACKOFF_BASE ** attempt
                    print_warning(f"Server error {response.status_code}, retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
                    continue

                if response.status_code == 401:
                    print_error("SDP authentication failed. Check SDP_API_KEY.")
                    return None

                if response.status_code == 403:
                    print_error("SDP access denied. Insufficient permissions.")
                    return None

                if response.status_code == 404:
                    print_error(f"SDP resource not found: {path}")
                    return None

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                if attempt < MAX_RETRIES:
                    wait = RETRY_BACKOFF_BASE ** attempt
                    print_warning(f"Request timed out, retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
                else:
                    print_error(f"Request timed out after {MAX_RETRIES} attempts")
                    return None

            except httpx.HTTPStatusError as e:
                print_error(f"HTTP error: {sanitize_error(e)}")
                return None

            except httpx.HTTPError as e:
                if attempt < MAX_RETRIES:
                    wait = RETRY_BACKOFF_BASE ** attempt
                    print_warning(f"Network error, retrying in {wait:.1f}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
                else:
                    print_error(f"Network error after {MAX_RETRIES} attempts: {sanitize_error(e)}")
                    return None

        print_error(f"Request failed after {MAX_RETRIES} attempts")
        return None

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        return self._request("GET", path, params=params)

    def _post(self, path: str, json_body: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        return self._request("POST", path, json_body=json_body)

    # ── Stablecoin Operations (Issuance API) ─────────────────

    def list_stablecoins(self) -> List[StablecoinInfo]:
        """List available stablecoins on SDP."""
        print_info("Fetching stablecoins from SDP...")

        data = self._get("/v1/issuance/stablecoins")
        if not data:
            return []

        tokens = []
        for item in data.get("stablecoins", []):
            tokens.append(StablecoinInfo(
                token_id=item.get("token_id", ""),
                name=item.get("name", ""),
                symbol=item.get("symbol", ""),
                decimals=item.get("decimals", 6),
                issuer=item.get("issuer", ""),
                total_supply=float(item.get("total_supply", 0)),
                mint_authority=item.get("mint_authority", ""),
                freeze_authority=item.get("freeze_authority", ""),
            ))

        print_success(f"Found {len(tokens)} stablecoin(s)")
        return tokens

    def get_stablecoin_info(self, token_id: str) -> Optional[StablecoinInfo]:
        """Get detailed information for a specific stablecoin."""
        print_info(f"Fetching stablecoin info: {token_id[:16]}...")

        data = self._get(f"/v1/issuance/stablecoins/{token_id}")
        if not data:
            return None

        info = StablecoinInfo(
            token_id=data.get("token_id", token_id),
            name=data.get("name", ""),
            symbol=data.get("symbol", ""),
            decimals=data.get("decimals", 6),
            issuer=data.get("issuer", ""),
            total_supply=float(data.get("total_supply", 0)),
            mint_authority=data.get("mint_authority", ""),
            freeze_authority=data.get("freeze_authority", ""),
        )

        print_success(f"Stablecoin: {info.symbol} ({info.name})")
        print_info(f"  Decimals: {info.decimals}")
        print_info(f"  Total supply: {info.total_supply:,.2f}")
        print_info(f"  Issuer: {info.issuer[:16]}...")
        return info

    def mint_stablecoin(
        self,
        token_id: str,
        amount: float,
        recipient: str,
    ) -> Optional[Dict[str, Any]]:
        """Request stablecoin minting.

        Returns the unsigned transaction bytes for air-gapped signing
        when the operation requires on-chain authorization.
        """
        print_info(f"Requesting mint: {amount} of {token_id[:16]}...")
        print_info(f"  Recipient: {recipient}")

        data = self._post("/v1/issuance/mint", json_body={
            "token_id": token_id,
            "amount": str(amount),
            "recipient": recipient,
            "network": self.network,
        })
        if not data:
            return None

        if data.get("requires_signing"):
            print_warning("Mint requires on-chain signing via air-gap")
            print_info("  Transaction data included for offline signing")
        else:
            print_success(f"Mint request submitted: {amount}")
            if data.get("tx_signature"):
                print_info(f"  Tx: {data['tx_signature'][:16]}...")

        return data

    # ── Payment Operations (Payments API) ────────────────────

    def create_onramp(
        self,
        amount: float,
        currency: str,
        wallet: str,
    ) -> Optional[PaymentResult]:
        """Create a fiat-to-crypto on-ramp payment."""
        print_info(f"Creating on-ramp: {amount} {currency} -> {wallet[:16]}...")

        data = self._post("/v1/payments/onramp", json_body={
            "amount": str(amount),
            "currency": currency.upper(),
            "wallet": wallet,
            "network": self.network,
        })
        if not data:
            return None

        result = PaymentResult(
            payment_id=data.get("payment_id", ""),
            status=PaymentStatus(data.get("status", "pending")),
            amount=float(data.get("amount", amount)),
            currency=data.get("currency", currency),
            wallet=data.get("wallet", wallet),
            tx_signature=data.get("tx_signature", ""),
            created_at=data.get("created_at", time.time()),
            fee=float(data.get("fee", 0)),
        )

        print_success(f"On-ramp created: {result.payment_id}")
        print_info(f"  Status: {result.status.value}")
        print_info(f"  Amount: {result.amount} {result.currency}")
        if result.fee > 0:
            print_info(f"  Fee: {result.fee} {result.currency}")
        return result

    def create_offramp(
        self,
        amount: float,
        currency: str,
        bank_details: Dict[str, str],
    ) -> Optional[PaymentResult]:
        """Create a crypto-to-fiat off-ramp payment."""
        print_info(f"Creating off-ramp: {amount} {currency} -> bank")

        data = self._post("/v1/payments/offramp", json_body={
            "amount": str(amount),
            "currency": currency.upper(),
            "bank_details": bank_details,
            "network": self.network,
        })
        if not data:
            return None

        result = PaymentResult(
            payment_id=data.get("payment_id", ""),
            status=PaymentStatus(data.get("status", "pending")),
            amount=float(data.get("amount", amount)),
            currency=data.get("currency", currency),
            wallet=data.get("wallet", ""),
            tx_signature=data.get("tx_signature", ""),
            created_at=data.get("created_at", time.time()),
            fee=float(data.get("fee", 0)),
        )

        print_success(f"Off-ramp created: {result.payment_id}")
        print_info(f"  Status: {result.status.value}")
        print_info(f"  Amount: {result.amount} {result.currency}")
        if result.fee > 0:
            print_info(f"  Fee: {result.fee} {result.currency}")
        return result

    def transfer_stablecoin(
        self,
        token_id: str,
        amount: float,
        from_wallet: str,
        to_wallet: str,
    ) -> Optional[PaymentResult]:
        """Transfer stablecoins between wallets via SDP."""
        print_info(f"Transferring {amount} of {token_id[:16]}...")
        print_info(f"  From: {from_wallet[:16]}...")
        print_info(f"  To:   {to_wallet[:16]}...")

        data = self._post("/v1/payments/transfer", json_body={
            "token_id": token_id,
            "amount": str(amount),
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "network": self.network,
        })
        if not data:
            return None

        result = PaymentResult(
            payment_id=data.get("payment_id", ""),
            status=PaymentStatus(data.get("status", "pending")),
            amount=float(data.get("amount", amount)),
            currency=data.get("currency", token_id),
            wallet=to_wallet,
            tx_signature=data.get("tx_signature", ""),
            created_at=data.get("created_at", time.time()),
            fee=float(data.get("fee", 0)),
        )

        print_success(f"Transfer submitted: {result.payment_id}")
        print_info(f"  Status: {result.status.value}")
        if result.tx_signature:
            print_info(f"  Tx: {result.tx_signature[:16]}...")
        return result

    def get_payment_status(self, payment_id: str) -> Optional[PaymentResult]:
        """Check the status of a payment operation."""
        print_info(f"Checking payment: {payment_id}...")

        data = self._get(f"/v1/payments/{payment_id}")
        if not data:
            return None

        result = PaymentResult(
            payment_id=data.get("payment_id", payment_id),
            status=PaymentStatus(data.get("status", "pending")),
            amount=float(data.get("amount", 0)),
            currency=data.get("currency", ""),
            wallet=data.get("wallet", ""),
            tx_signature=data.get("tx_signature", ""),
            created_at=data.get("created_at", 0),
            completed_at=data.get("completed_at", 0),
            fee=float(data.get("fee", 0)),
        )

        status_style = {
            PaymentStatus.COMPLETED: "green",
            PaymentStatus.FAILED: "red",
            PaymentStatus.CANCELLED: "yellow",
        }.get(result.status, "cyan")

        print_info(f"  Payment ID: {result.payment_id}")
        print_info(f"  Status: [{status_style}]{result.status.value}[/{status_style}]")
        print_info(f"  Amount: {result.amount} {result.currency}")
        if result.tx_signature:
            print_info(f"  Tx: {result.tx_signature[:16]}...")
        return result

    def estimate_fees(self, amount: float, currency: str) -> Optional[FeeEstimate]:
        """Estimate fees for a payment operation."""
        print_info(f"Estimating fees for {amount} {currency}...")

        data = self._get("/v1/payments/fees", params={
            "amount": str(amount),
            "currency": currency.upper(),
            "network": self.network,
        })
        if not data:
            return None

        estimate = FeeEstimate(
            amount=float(data.get("amount", amount)),
            currency=data.get("currency", currency),
            network_fee=float(data.get("network_fee", 0)),
            platform_fee=float(data.get("platform_fee", 0)),
            total_fee=float(data.get("total_fee", 0)),
        )

        print_success("Fee estimate:")
        print_info(f"  Network fee:  {estimate.network_fee:.6f} {estimate.currency}")
        print_info(f"  Platform fee: {estimate.platform_fee:.6f} {estimate.currency}")
        print_info(f"  Total fee:    {estimate.total_fee:.6f} {estimate.currency}")
        return estimate

    # ── Trading Operations (Trading API) ─────────────────────

    def get_swap_quote(
        self,
        from_token: str,
        to_token: str,
        amount: float,
    ) -> Optional[SwapQuote]:
        """Get a swap quote from SDP Trading API."""
        print_info(f"Fetching swap quote: {amount} {from_token} -> {to_token}...")

        data = self._get("/v1/trading/quote", params={
            "from_token": from_token,
            "to_token": to_token,
            "amount": str(amount),
            "network": self.network,
        })
        if not data:
            return None

        quote = SwapQuote(
            quote_id=data.get("quote_id", ""),
            from_token=data.get("from_token", from_token),
            to_token=data.get("to_token", to_token),
            from_amount=float(data.get("from_amount", amount)),
            to_amount=float(data.get("to_amount", 0)),
            exchange_rate=float(data.get("exchange_rate", 0)),
            price_impact=float(data.get("price_impact", 0)),
            fee=float(data.get("fee", 0)),
            expires_at=float(data.get("expires_at", 0)),
            route=data.get("route", []),
        )

        print_success("Swap quote received!")
        print_info(f"  Quote ID: {quote.quote_id}")
        print_info(f"  {quote.from_amount} {quote.from_token} -> {quote.to_amount} {quote.to_token}")
        print_info(f"  Rate: {quote.exchange_rate:.6f}")
        if quote.price_impact > 0:
            impact_color = "yellow" if quote.price_impact > 1.0 else "green"
            print_info(f"  Price impact: [{impact_color}]{quote.price_impact:.2f}%[/{impact_color}]")
        if quote.fee > 0:
            print_info(f"  Fee: {quote.fee:.6f}")
        if quote.route:
            print_info(f"  Route: {' -> '.join(quote.route)}")
        return quote

    def execute_swap(self, quote_id: str) -> Optional[Dict[str, Any]]:
        """Execute a swap from a previously obtained quote.

        Returns transaction data that may require signing via
        the Rust secure signer for air-gapped wallets.
        """
        print_info(f"Executing swap: {quote_id}...")

        data = self._post("/v1/trading/swap", json_body={
            "quote_id": quote_id,
            "network": self.network,
        })
        if not data:
            return None

        if data.get("requires_signing"):
            print_warning("Swap requires on-chain signing via air-gap")
            print_info("  Unsigned transaction included for Rust signer")
        elif data.get("tx_signature"):
            print_success(f"Swap executed: {data['tx_signature'][:16]}...")
        else:
            print_success("Swap submitted")

        return data

    def create_vault(self, name: str, config: Dict[str, Any]) -> Optional[Vault]:
        """Create a new trading vault."""
        print_info(f"Creating vault: {name}...")

        data = self._post("/v1/trading/vaults", json_body={
            "name": name,
            "config": config,
            "network": self.network,
        })
        if not data:
            return None

        vault = Vault(
            vault_id=data.get("vault_id", ""),
            name=data.get("name", name),
            owner=data.get("owner", ""),
            token=data.get("token", ""),
            balance=float(data.get("balance", 0)),
            status=data.get("status", "active"),
            created_at=data.get("created_at", time.time()),
            config=data.get("config", config),
        )

        print_success(f"Vault created: {vault.vault_id}")
        print_info(f"  Name:   {vault.name}")
        print_info(f"  Owner:  {vault.owner[:16]}..." if vault.owner else "  Owner:  (pending)")
        print_info(f"  Status: {vault.status}")
        return vault

    def get_fx_rate(self, from_currency: str, to_currency: str) -> Optional[FxRate]:
        """Get foreign exchange rate."""
        print_info(f"Fetching FX rate: {from_currency}/{to_currency}...")

        data = self._get("/v1/trading/fx", params={
            "from": from_currency.upper(),
            "to": to_currency.upper(),
        })
        if not data:
            return None

        rate = FxRate(
            from_currency=data.get("from", from_currency),
            to_currency=data.get("to", to_currency),
            rate=float(data.get("rate", 0)),
            timestamp=data.get("timestamp", time.time()),
            source=data.get("source", "sdp"),
        )

        print_success(f"1 {rate.from_currency} = {rate.rate:.6f} {rate.to_currency}")
        return rate

    # ── Air-gap signing helpers ──────────────────────────────

    def sign_sdp_transaction(
        self,
        tx_data: Dict[str, Any],
        rust_signer: Any,
        encrypted_container: Dict[str, Any],
        password: str,
    ) -> Optional[bytes]:
        """Sign an SDP transaction using the Rust secure signer.

        Used when SDP returns unsigned transaction data that requires
        on-chain authorization (minting, swaps, etc.).
        """
        from solders.transaction import Transaction, VersionedTransaction
        from solders.signature import Signature

        tx_base64 = tx_data.get("unsigned_transaction") or tx_data.get("transaction")
        if not tx_base64:
            print_error("No transaction data to sign")
            return None

        try:
            tx_bytes = base64.b64decode(tx_base64)

            # Try versioned transaction first (newer format)
            try:
                vtx = VersionedTransaction.from_bytes(tx_bytes)
                message_bytes = bytes(vtx.message)
                is_versioned = True
            except Exception:
                tx = Transaction.from_bytes(tx_bytes)
                message_bytes = bytes(tx.message)
                is_versioned = False

            print_info("Signing SDP transaction via Rust secure signer...")

            signature_bytes, _ = rust_signer.sign_transaction(
                encrypted_container,
                password,
                message_bytes,
            )

            sig = Signature.from_bytes(signature_bytes)

            if is_versioned:
                vtx.signatures = [sig]
                signed_bytes = bytes(vtx)
            else:
                tx.signatures = [sig]
                signed_bytes = bytes(tx)

            print_success("SDP transaction signed securely")
            return signed_bytes

        except Exception as e:
            print_error(f"Failed to sign SDP transaction: {sanitize_error(e)}")
            return None

    def save_sdp_transaction(
        self,
        tx_data: Dict[str, Any],
        path: str,
        operation: str = "sdp_operation",
    ) -> bool:
        """Save SDP transaction data for air-gapped signing."""
        try:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            save_data = {
                "type": f"sdp_{operation}",
                "version": "1.0",
                "network": self.network,
                "timestamp": time.time(),
                "data": tx_data,
            }

            with open(filepath, "w") as f:
                json.dump(save_data, f, indent=2)

            print_success(f"SDP transaction saved to: {filepath}")
            return True

        except Exception as e:
            print_error(f"Failed to save SDP transaction: {sanitize_error(e)}")
            return False

    def load_sdp_transaction(self, path: str) -> Optional[Dict[str, Any]]:
        """Load a saved SDP transaction from file."""
        try:
            filepath = Path(path)
            if not filepath.exists():
                print_error(f"File not found: {filepath}")
                return None

            with open(filepath, "r") as f:
                save_data = json.load(f)

            if not save_data.get("type", "").startswith("sdp_"):
                print_error("Invalid SDP transaction file")
                return None

            print_success(f"Loaded SDP transaction from: {filepath}")
            return save_data.get("data", {})

        except Exception as e:
            print_error(f"Failed to load SDP transaction: {sanitize_error(e)}")
            return None

    # ── Cleanup ──────────────────────────────────────────────

    def close(self) -> None:
        """Close the HTTP client."""
        try:
            self.client.close()
        except Exception:
            pass

    def __del__(self) -> None:
        self.close()
