"""
SDP CLI Menu — Interactive menus for Solana Developer Platform operations.

Integrates with Coldstar's existing Rich-based UI system and questionary
menus to provide stablecoin, payment, and trading workflows through the
air-gapped cold wallet interface.
"""

from typing import Optional

from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED, DOUBLE

from src.ui import (
    console,
    print_success,
    print_error,
    print_info,
    print_warning,
    print_section_header,
    select_menu_option,
    get_text_input,
    get_float_input,
    get_password_input,
)
from src.sdp_integration import (
    SdpClient,
    StablecoinInfo,
    PaymentResult,
    SwapQuote,
    Vault,
    FxRate,
    FeeEstimate,
    PaymentStatus,
)


class SdpMenuHandler:
    """Handles all SDP interactive menu flows."""

    def __init__(self, wallet_address: Optional[str] = None):
        self.client = SdpClient()
        self.wallet_address = wallet_address

    def set_wallet(self, address: str) -> None:
        """Set the active wallet address for operations."""
        self.wallet_address = address

    # ── Main SDP Menu ────────────────────────────────────────

    def sdp_menu(self) -> None:
        """Main SDP submenu — entry point for all SDP operations."""
        while True:
            print_section_header("SOLANA DEVELOPER PLATFORM (SDP)")

            if not self.client.api_key:
                print_warning("SDP_API_KEY not configured. Set it as an environment variable.")
                print_info("  export SDP_API_KEY=your_key_here")
                console.print()

            print_info(f"Network: {self.client.network}")
            if self.wallet_address:
                print_info(f"Wallet:  {self.wallet_address[:16]}...")
            console.print()

            options = [
                "1. Stablecoin Operations (Issuance)",
                "2. Payment Operations (On/Off-ramp)",
                "3. Trading Operations (Swap/Vault/FX)",
                "0. Back to Main Menu",
            ]

            choice = select_menu_option(options, "Select SDP module:")
            if choice is None:
                return

            choice_num = choice.split(".")[0].strip()

            if choice_num == "1":
                self.sdp_stablecoin_menu()
            elif choice_num == "2":
                self.sdp_payments_menu()
            elif choice_num == "3":
                self.sdp_trading_menu()
            elif choice_num == "0":
                return

    # ── Stablecoin Menu ──────────────────────────────────────

    def sdp_stablecoin_menu(self) -> None:
        """Stablecoin operations submenu."""
        while True:
            print_section_header("SDP — STABLECOIN OPERATIONS")

            options = [
                "1. List Stablecoins",
                "2. Get Stablecoin Info",
                "3. Mint Stablecoin",
                "0. Back",
            ]

            choice = select_menu_option(options, "Select operation:")
            if choice is None:
                return

            choice_num = choice.split(".")[0].strip()

            if choice_num == "1":
                self._list_stablecoins()
            elif choice_num == "2":
                self._get_stablecoin_info()
            elif choice_num == "3":
                self._mint_stablecoin()
            elif choice_num == "0":
                return

            _wait_for_key()

    def _list_stablecoins(self) -> None:
        """List all available stablecoins."""
        tokens = self.client.list_stablecoins()
        if not tokens:
            print_warning("No stablecoins found or API unavailable")
            return

        table = Table(
            title="Available Stablecoins",
            box=ROUNDED,
            border_style="cyan",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Symbol", style="cyan bold")
        table.add_column("Name", style="white")
        table.add_column("Decimals", style="green", justify="right")
        table.add_column("Total Supply", style="yellow", justify="right")
        table.add_column("Token ID", style="dim")

        for i, token in enumerate(tokens, 1):
            table.add_row(
                str(i),
                token.symbol,
                token.name,
                str(token.decimals),
                f"{token.total_supply:,.2f}",
                f"{token.token_id[:20]}...",
            )

        console.print(table)

    def _get_stablecoin_info(self) -> None:
        """Get detailed info for a specific stablecoin."""
        token_id = get_text_input("Enter token ID or mint address:")
        if not token_id:
            return

        info = self.client.get_stablecoin_info(token_id)
        if not info:
            return

        table = Table(box=DOUBLE, show_header=False, border_style="cyan")
        table.add_column("Field", style="dim")
        table.add_column("Value", style="green bold")

        table.add_row("Token ID", info.token_id)
        table.add_row("Symbol", info.symbol)
        table.add_row("Name", info.name)
        table.add_row("Decimals", str(info.decimals))
        table.add_row("Total Supply", f"{info.total_supply:,.2f}")
        table.add_row("Issuer", info.issuer)
        if info.mint_authority:
            table.add_row("Mint Authority", info.mint_authority)
        if info.freeze_authority:
            table.add_row("Freeze Authority", info.freeze_authority)

        panel = Panel(
            table,
            title=f"[bold cyan]{info.symbol} — Stablecoin Details[/bold cyan]",
            border_style="cyan",
            box=DOUBLE,
        )
        console.print(panel)

    def _mint_stablecoin(self) -> None:
        """Mint stablecoins to a recipient wallet."""
        token_id = get_text_input("Enter token ID to mint:")
        if not token_id:
            return

        amount = get_float_input("Enter amount to mint:")
        if amount <= 0:
            print_error("Amount must be positive")
            return

        recipient = get_text_input(
            "Enter recipient wallet:",
            default=self.wallet_address or "",
        )
        if not recipient:
            return

        result = self.client.mint_stablecoin(token_id, amount, recipient)
        if not result:
            return

        if result.get("requires_signing"):
            print_section_header("SIGNING REQUIRED")
            print_info("This mint operation requires on-chain signing.")
            print_info("Transfer the transaction file to your air-gapped device for signing.")

            save_path = get_text_input("Save transaction to:", default="/outbox/sdp_mint.json")
            if save_path:
                self.client.save_sdp_transaction(result, save_path, "mint")

    # ── Payments Menu ────────────────────────────────────────

    def sdp_payments_menu(self) -> None:
        """Payment operations submenu."""
        while True:
            print_section_header("SDP — PAYMENT OPERATIONS")

            options = [
                "1. On-Ramp (Fiat -> Crypto)",
                "2. Off-Ramp (Crypto -> Fiat)",
                "3. Transfer Stablecoin",
                "4. Check Payment Status",
                "5. Estimate Fees",
                "0. Back",
            ]

            choice = select_menu_option(options, "Select operation:")
            if choice is None:
                return

            choice_num = choice.split(".")[0].strip()

            if choice_num == "1":
                self._create_onramp()
            elif choice_num == "2":
                self._create_offramp()
            elif choice_num == "3":
                self._transfer_stablecoin()
            elif choice_num == "4":
                self._check_payment_status()
            elif choice_num == "5":
                self._estimate_fees()
            elif choice_num == "0":
                return

            _wait_for_key()

    def _create_onramp(self) -> None:
        """Create fiat-to-crypto on-ramp."""
        amount = get_float_input("Enter fiat amount:")
        if amount <= 0:
            print_error("Amount must be positive")
            return

        currency = get_text_input("Enter fiat currency (e.g. USD, EUR):", default="USD")
        if not currency:
            return

        wallet = get_text_input(
            "Enter destination wallet:",
            default=self.wallet_address or "",
        )
        if not wallet:
            return

        result = self.client.create_onramp(amount, currency, wallet)
        if result:
            _display_payment_result(result, "ON-RAMP")

    def _create_offramp(self) -> None:
        """Create crypto-to-fiat off-ramp."""
        amount = get_float_input("Enter crypto amount:")
        if amount <= 0:
            print_error("Amount must be positive")
            return

        currency = get_text_input("Enter currency (e.g. USDC, USDT):", default="USDC")
        if not currency:
            return

        print_section_header("BANK DETAILS")
        print_warning("Bank details are transmitted securely via SDP.")

        bank_name = get_text_input("Bank name:")
        routing = get_text_input("Routing number:")
        account = get_text_input("Account number:")

        if not all([bank_name, routing, account]):
            print_error("All bank details are required")
            return

        bank_details = {
            "bank_name": bank_name,
            "routing_number": routing,
            "account_number": account,
        }

        result = self.client.create_offramp(amount, currency, bank_details)
        if result:
            _display_payment_result(result, "OFF-RAMP")

    def _transfer_stablecoin(self) -> None:
        """Transfer stablecoins between wallets."""
        token_id = get_text_input("Enter token ID (e.g. USDC mint address):")
        if not token_id:
            return

        amount = get_float_input("Enter amount:")
        if amount <= 0:
            print_error("Amount must be positive")
            return

        from_wallet = get_text_input(
            "Enter source wallet:",
            default=self.wallet_address or "",
        )
        if not from_wallet:
            return

        to_wallet = get_text_input("Enter destination wallet:")
        if not to_wallet:
            return

        result = self.client.transfer_stablecoin(token_id, amount, from_wallet, to_wallet)
        if result:
            _display_payment_result(result, "STABLECOIN TRANSFER")

    def _check_payment_status(self) -> None:
        """Check status of a payment."""
        payment_id = get_text_input("Enter payment ID:")
        if not payment_id:
            return

        result = self.client.get_payment_status(payment_id)
        if result:
            _display_payment_result(result, "PAYMENT STATUS")

    def _estimate_fees(self) -> None:
        """Estimate fees for a payment."""
        amount = get_float_input("Enter amount:")
        if amount <= 0:
            print_error("Amount must be positive")
            return

        currency = get_text_input("Enter currency:", default="USDC")
        if not currency:
            return

        estimate = self.client.estimate_fees(amount, currency)
        if not estimate:
            return

        table = Table(box=ROUNDED, show_header=False, border_style="yellow")
        table.add_column("Field", style="dim")
        table.add_column("Value", style="bold")

        table.add_row("Amount", f"{estimate.amount:,.2f} {estimate.currency}")
        table.add_row("Network Fee", f"[yellow]{estimate.network_fee:.6f} {estimate.currency}[/yellow]")
        table.add_row("Platform Fee", f"[yellow]{estimate.platform_fee:.6f} {estimate.currency}[/yellow]")
        table.add_row("Total Fee", f"[red]{estimate.total_fee:.6f} {estimate.currency}[/red]")

        panel = Panel(
            table,
            title="[bold yellow]FEE ESTIMATE[/bold yellow]",
            border_style="yellow",
            box=ROUNDED,
        )
        console.print(panel)

    # ── Trading Menu ─────────────────────────────────────────

    def sdp_trading_menu(self) -> None:
        """Trading operations submenu."""
        while True:
            print_section_header("SDP — TRADING OPERATIONS")

            options = [
                "1. Get Swap Quote",
                "2. Execute Swap",
                "3. Create Vault",
                "4. Get FX Rate",
                "0. Back",
            ]

            choice = select_menu_option(options, "Select operation:")
            if choice is None:
                return

            choice_num = choice.split(".")[0].strip()

            if choice_num == "1":
                self._get_swap_quote()
            elif choice_num == "2":
                self._execute_swap()
            elif choice_num == "3":
                self._create_vault()
            elif choice_num == "4":
                self._get_fx_rate()
            elif choice_num == "0":
                return

            _wait_for_key()

    def _get_swap_quote(self) -> None:
        """Get a swap quote."""
        from_token = get_text_input("From token (symbol or mint):", default="USDC")
        if not from_token:
            return

        to_token = get_text_input("To token (symbol or mint):", default="SOL")
        if not to_token:
            return

        amount = get_float_input("Amount to swap:")
        if amount <= 0:
            print_error("Amount must be positive")
            return

        quote = self.client.get_swap_quote(from_token, to_token, amount)
        if not quote:
            return

        _display_swap_quote(quote)

    def _execute_swap(self) -> None:
        """Execute a swap from a quote ID."""
        quote_id = get_text_input("Enter quote ID:")
        if not quote_id:
            return

        print_warning("Executing swap — this may require signing.")
        result = self.client.execute_swap(quote_id)
        if not result:
            return

        if result.get("requires_signing"):
            print_section_header("SIGNING REQUIRED")
            print_info("This swap requires on-chain signing via air-gap.")

            save_path = get_text_input("Save transaction to:", default="/outbox/sdp_swap.json")
            if save_path:
                self.client.save_sdp_transaction(result, save_path, "swap")
        elif result.get("tx_signature"):
            print_success(f"Swap executed successfully!")
            print_info(f"  Signature: {result['tx_signature']}")

    def _create_vault(self) -> None:
        """Create a new trading vault."""
        name = get_text_input("Vault name:")
        if not name:
            return

        token = get_text_input("Vault token (e.g. USDC, SOL):", default="USDC")
        if not token:
            return

        max_deposit = get_float_input("Max deposit limit (0 for unlimited):", default=0.0)
        auto_rebalance = get_text_input("Enable auto-rebalance? (y/n):", default="n")

        config = {
            "token": token,
            "max_deposit": max_deposit if max_deposit > 0 else None,
            "auto_rebalance": auto_rebalance.lower() == "y",
        }

        vault = self.client.create_vault(name, config)
        if not vault:
            return

        _display_vault(vault)

    def _get_fx_rate(self) -> None:
        """Get foreign exchange rate."""
        from_currency = get_text_input("From currency:", default="USD")
        if not from_currency:
            return

        to_currency = get_text_input("To currency:", default="USDC")
        if not to_currency:
            return

        rate = self.client.get_fx_rate(from_currency, to_currency)
        if not rate:
            return

        panel = Panel(
            f"[green bold]1 {rate.from_currency} = {rate.rate:.6f} {rate.to_currency}[/green bold]",
            title="[bold cyan]FX RATE[/bold cyan]",
            border_style="cyan",
            box=ROUNDED,
        )
        console.print(panel)

    # ── Cleanup ──────────────────────────────────────────────

    def close(self) -> None:
        """Cleanup resources."""
        self.client.close()


# ── Display Helpers ──────────────────────────────────────────


def _wait_for_key() -> None:
    console.print()
    console.input("[dim]Press Enter to continue...[/dim]")


def _display_payment_result(result: PaymentResult, title: str) -> None:
    """Display a payment result in a Rich panel."""
    status_color = {
        PaymentStatus.COMPLETED: "green",
        PaymentStatus.FAILED: "red",
        PaymentStatus.CANCELLED: "yellow",
        PaymentStatus.PROCESSING: "cyan",
        PaymentStatus.PENDING: "white",
    }.get(result.status, "white")

    table = Table(box=ROUNDED, show_header=False, border_style="cyan")
    table.add_column("Field", style="dim")
    table.add_column("Value", style="bold")

    table.add_row("Payment ID", result.payment_id)
    table.add_row("Status", f"[{status_color}]{result.status.value}[/{status_color}]")
    table.add_row("Amount", f"[green]{result.amount:,.2f} {result.currency}[/green]")
    if result.wallet:
        table.add_row("Wallet", result.wallet)
    if result.fee > 0:
        table.add_row("Fee", f"[yellow]{result.fee:.6f} {result.currency}[/yellow]")
    if result.tx_signature:
        table.add_row("Tx Signature", result.tx_signature)

    panel = Panel(
        table,
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        box=ROUNDED,
    )
    console.print(panel)


def _display_swap_quote(quote: SwapQuote) -> None:
    """Display a swap quote in a Rich panel."""
    table = Table(box=ROUNDED, show_header=False, border_style="green")
    table.add_column("Field", style="dim")
    table.add_column("Value", style="bold")

    table.add_row("Quote ID", quote.quote_id)
    table.add_row("From", f"{quote.from_amount:,.6f} {quote.from_token}")
    table.add_row("To", f"[green]{quote.to_amount:,.6f} {quote.to_token}[/green]")
    table.add_row("Exchange Rate", f"{quote.exchange_rate:.6f}")
    if quote.price_impact > 0:
        impact_color = "red" if quote.price_impact > 1.0 else "yellow"
        table.add_row("Price Impact", f"[{impact_color}]{quote.price_impact:.2f}%[/{impact_color}]")
    if quote.fee > 0:
        table.add_row("Fee", f"[yellow]{quote.fee:.6f}[/yellow]")
    if quote.route:
        table.add_row("Route", " -> ".join(quote.route))

    panel = Panel(
        table,
        title="[bold green]SWAP QUOTE[/bold green]",
        border_style="green",
        box=ROUNDED,
    )
    console.print(panel)


def _display_vault(vault: Vault) -> None:
    """Display vault details in a Rich panel."""
    table = Table(box=DOUBLE, show_header=False, border_style="cyan")
    table.add_column("Field", style="dim")
    table.add_column("Value", style="green bold")

    table.add_row("Vault ID", vault.vault_id)
    table.add_row("Name", vault.name)
    table.add_row("Owner", vault.owner if vault.owner else "(pending)")
    table.add_row("Token", vault.token)
    table.add_row("Balance", f"{vault.balance:,.2f}")
    table.add_row("Status", vault.status)

    panel = Panel(
        table,
        title="[bold cyan]TRADING VAULT[/bold cyan]",
        border_style="cyan",
        box=DOUBLE,
    )
    console.print(panel)
