#!/usr/bin/env python3
"""
Coldstar Base CLI — Air-gapped cold wallet for Base (Coinbase L2)

Standalone entry point for Base/EVM operations. Reuses the same security
model as the Solana CLI (encrypted containers, Rust signer, QR air-gap).

B - Love U 3000
"""

import sys
import gc
from pathlib import Path

from rich.console import Console
from rich.text import Text

from config import (
    APP_VERSION, BASE_RPC_URL, BASE_TESTNET_RPC_URL,
    WEI_PER_ETH, GWEI_PER_ETH,
)
from src.ui import (
    print_success, print_error, print_info, print_warning,
    print_section_header, select_menu_option, get_text_input,
    get_password_input, get_float_input, confirm_dangerous_action,
    clear_screen, console,
)
from src.evm_wallet import EVMWalletManager
from src.evm_network import BaseNetwork
from src.evm_transaction import EVMTransactionManager
from src.qr_transfer import QRTransfer


def print_base_banner():
    banner = """
[bold blue]╔═══════════════════════════════════════════════════════════════╗[/]
[bold blue]║[/]                                                               [bold blue]║[/]
[bold blue]║[/]   [bold white]COLDSTAR[/] [bold blue]× BASE[/]                                            [bold blue]║[/]
[bold blue]║[/]   [dim]Air-Gapped Cold Wallet for Coinbase L2[/]                     [bold blue]║[/]
[bold blue]║[/]                                                               [bold blue]║[/]
[bold blue]╠═══════════════════════════════════════════════════════════════╣[/]
[bold blue]║[/]  [dim]Private keys never touch the network. Sign offline,[/]         [bold blue]║[/]
[bold blue]║[/]  [dim]broadcast online. Same security, new chain.[/]                 [bold blue]║[/]
[bold blue]╚═══════════════════════════════════════════════════════════════╝[/]
"""
    console.print(banner)


class BaseCLI:
    """Interactive CLI for Base (EVM) cold wallet operations."""

    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.wallet = EVMWalletManager()
        self.network = BaseNetwork(testnet=testnet)
        self.tx_manager = EVMTransactionManager(testnet=testnet)
        self.qr = QRTransfer()
        self.address: str | None = None
        self.wallet_path: Path | None = None

    def run(self):
        while True:
            try:
                self.main_menu()
            except KeyboardInterrupt:
                console.print("\n")
                print_info("Exiting...")
                self.network.close()
                sys.exit(0)
            except Exception as e:
                print_error(f"Error: {e}")
                continue

    def _draw_header(self):
        clear_screen()
        print_base_banner()
        net_label = "Base Sepolia (testnet)" if self.testnet else "Base Mainnet"
        rpc = BASE_TESTNET_RPC_URL if self.testnet else BASE_RPC_URL
        print_info(f"Network: {net_label}")
        print_info(f"RPC: {rpc}")
        if self.network.is_connected():
            print_success("Status: Connected")
        else:
            print_warning("Status: Offline")
        console.print()

    def _wait(self):
        console.print()
        console.input("[dim]Press Enter to continue...[/dim]")

    # ── Main Menu ───────────────────────────────────────────

    def main_menu(self):
        self._draw_header()

        if self.address:
            self._wallet_menu()
        else:
            self._no_wallet_menu()

    def _no_wallet_menu(self):
        print_section_header("WALLET")
        print_info("No wallet loaded.")
        console.print()

        options = [
            "1. Create New Base Wallet",
            "2. Load Existing Wallet",
            "3. Check Address Balance",
            "4. Network Info",
            "0. Exit",
        ]

        choice = select_menu_option(options, "Select an option:")
        if not choice:
            return

        num = choice.split(".")[0].strip()
        if num == "1":
            self._draw_header()
            self.create_wallet()
            self._wait()
        elif num == "2":
            self._draw_header()
            self.load_wallet()
            self._wait()
        elif num == "3":
            self._draw_header()
            self.check_balance_manual()
            self._wait()
        elif num == "4":
            self._draw_header()
            self.show_network_info()
            self._wait()
        elif num == "0":
            self.network.close()
            sys.exit(0)

    def _wallet_menu(self):
        # Show balance
        balance = self.network.get_balance(self.address)
        print_section_header(f"WALLET: {self.address[:10]}...{self.address[-8:]}")
        if balance is not None:
            print_info(f"Balance: {balance:.6f} ETH")
        else:
            print_warning("Could not fetch balance")
        console.print()

        options = [
            "1. View Wallet Info",
            "2. Send ETH (Create Unsigned Tx)",
            "3. Sign Transaction (Offline)",
            "4. Broadcast Signed Transaction",
            "5. Quick Send (Create+Sign+Broadcast)",
            "6. Check ERC-20 Balance",
            "7. View on BaseScan",
            "8. Network Info",
            "9. Switch / Unload Wallet",
            "0. Exit",
        ]

        choice = select_menu_option(options, "Select an option:")
        if not choice:
            return

        num = choice.split(".")[0].strip()
        actions = {
            "1": self.view_wallet_info,
            "2": self.create_unsigned_tx,
            "3": self.sign_transaction_offline,
            "4": self.broadcast_signed_tx,
            "5": self.quick_send,
            "6": self.check_erc20_balance,
            "7": self.view_on_explorer,
            "8": self.show_network_info,
            "9": self.unload_wallet,
        }

        if num == "0":
            self.network.close()
            sys.exit(0)
        elif num in actions:
            self._draw_header()
            actions[num]()
            self._wait()

    # ── Wallet Operations ───────────────────────────────────

    def create_wallet(self):
        print_section_header("CREATE NEW BASE WALLET")

        wallet_dir = get_text_input(
            "Wallet directory (default: ./local_wallet/base): ",
            default="./local_wallet/base",
        )
        wallet_path = Path(wallet_dir)
        wallet_path.mkdir(parents=True, exist_ok=True)

        self.wallet.set_wallet_directory(str(wallet_path))
        account, address = self.wallet.generate_keypair()

        print_warning("SECURITY: For maximum security, generate keys on an OFFLINE device.")
        console.print()

        if self.wallet.save_keypair():
            self.address = address
            self.wallet_path = wallet_path
            print_success(f"Wallet created!")
            print_info(f"Address: {address}")
            print_info(f"Saved to: {wallet_path}")
            print_info(f"Explorer: {self.network.explorer_address_url(address)}")
        else:
            print_error("Failed to create wallet")

    def load_wallet(self):
        print_section_header("LOAD EXISTING WALLET")

        wallet_dir = get_text_input(
            "Wallet directory (default: ./local_wallet/base): ",
            default="./local_wallet/base",
        )
        wallet_path = Path(wallet_dir)
        self.wallet.set_wallet_directory(str(wallet_path))

        container = self.wallet.load_encrypted_container()
        if container:
            address = self.wallet.get_address()
            if address:
                self.address = address
                self.wallet_path = wallet_path
                print_success(f"Wallet loaded: {address}")
            else:
                print_error("Could not determine wallet address")
        else:
            print_error("Failed to load wallet")

    def view_wallet_info(self):
        print_section_header("WALLET INFORMATION")
        if not self.address:
            print_error("No wallet loaded")
            return

        print_info(f"Address: {self.address}")
        print_info(f"Chain:   Base {'Sepolia' if self.testnet else 'Mainnet'}")
        print_info(f"Path:    {self.wallet_path}")

        balance = self.network.get_balance(self.address)
        if balance is not None:
            print_info(f"Balance: {balance:.8f} ETH")
        else:
            print_warning("Could not fetch balance (offline?)")

        print_info(f"Explorer: {self.network.explorer_address_url(self.address)}")

    def unload_wallet(self):
        self.wallet.clear_memory()
        self.address = None
        self.wallet_path = None
        print_success("Wallet unloaded")

    # ── Transaction Operations ──────────────────────────────

    def create_unsigned_tx(self):
        print_section_header("CREATE UNSIGNED ETH TRANSFER")
        if not self.address:
            print_error("No wallet loaded")
            return

        to_addr = get_text_input("Recipient address (0x...): ")
        if not EVMWalletManager.validate_address(to_addr):
            print_error("Invalid address")
            return

        amount = get_float_input("Amount (ETH): ")
        if amount is None or amount <= 0:
            print_error("Invalid amount")
            return

        # Fetch chain params
        nonce = self.network.get_nonce(self.address)
        base_fee = self.network.get_base_fee()
        priority_fee = self.network.get_max_priority_fee()

        if nonce is None or base_fee is None or priority_fee is None:
            print_error("Could not fetch chain parameters (offline?)")
            return

        max_fee = base_fee * 2 + priority_fee

        tx = self.tx_manager.create_eth_transfer(
            from_address=self.address,
            to_address=to_addr,
            amount_eth=amount,
            nonce=nonce,
            max_fee_per_gas=max_fee,
            max_priority_fee_per_gas=priority_fee,
        )

        if tx:
            # Save and show QR
            outbox = (self.wallet_path or Path(".")) / "outbox"
            outbox.mkdir(exist_ok=True)
            import time
            path = outbox / f"unsigned_base_tx_{int(time.time())}.json"
            self.tx_manager.save_unsigned_transaction(tx, str(path))

            # QR for air-gap transfer
            serialized = self.tx_manager.serialize_unsigned_tx(tx)
            self.qr.display_transaction_qr(
                {"type": "unsigned_evm_transaction", "data": serialized},
                "SCAN TO SIGN ON AIR-GAPPED DEVICE",
            )

    def sign_transaction_offline(self):
        print_section_header("SIGN TRANSACTION (OFFLINE)")
        if not self.wallet_path:
            print_error("No wallet loaded")
            return

        # Load unsigned tx
        tx_path = get_text_input("Path to unsigned transaction JSON: ")
        tx = self.tx_manager.load_unsigned_transaction(tx_path)
        if not tx:
            return

        # Load wallet container
        container = self.wallet.load_encrypted_container()
        if not container:
            print_error("Could not load wallet")
            return

        password = get_password_input("Enter wallet password to sign: ")
        if not password:
            print_error("Password required")
            return

        signed = self.tx_manager.sign_transaction_secure(
            tx, container, password, wallet_manager=self.wallet,
        )

        if signed:
            outbox = (self.wallet_path or Path(".")) / "outbox"
            outbox.mkdir(exist_ok=True)
            import time
            path = outbox / f"signed_base_tx_{int(time.time())}.json"
            self.tx_manager.save_signed_transaction(signed, str(path))

            # QR for broadcast
            self.qr.display_transaction_qr(
                {"type": "signed_evm_transaction", "data": "0x" + signed.hex()},
                "SCAN TO BROADCAST",
            )

    def broadcast_signed_tx(self):
        print_section_header("BROADCAST SIGNED TRANSACTION")

        tx_path = get_text_input("Path to signed transaction JSON: ")
        signed_bytes = self.tx_manager.load_signed_transaction(tx_path)
        if not signed_bytes:
            return

        hex_tx = "0x" + signed_bytes.hex()
        print_info(f"Tx size: {len(signed_bytes)} bytes")

        if not confirm_dangerous_action("Broadcast this transaction to Base?", "SEND"):
            print_info("Cancelled")
            return

        tx_hash = self.network.send_raw_transaction(hex_tx)
        if tx_hash:
            print_success(f"Tx hash: {tx_hash}")
            print_info(f"Explorer: {self.network.explorer_url(tx_hash)}")

            print_info("Waiting for confirmation...")
            receipt = self.network.wait_for_receipt(tx_hash, max_retries=30)
            if receipt:
                print_success("Transaction confirmed!")
            else:
                print_warning("Check explorer for status")

    def quick_send(self):
        print_section_header("QUICK SEND (INSECURE - TESTING ONLY)")
        print_warning("This signs and broadcasts on an ONLINE device.")
        print_warning("For production, use the 3-step air-gap process.")
        console.print()

        if not self.address or not self.wallet_path:
            print_error("No wallet loaded")
            return

        to_addr = get_text_input("Recipient address (0x...): ")
        if not EVMWalletManager.validate_address(to_addr):
            print_error("Invalid address")
            return

        amount = get_float_input("Amount (ETH): ")
        if amount is None or amount <= 0:
            print_error("Invalid amount")
            return

        # Fetch params
        nonce = self.network.get_nonce(self.address)
        base_fee = self.network.get_base_fee()
        priority_fee = self.network.get_max_priority_fee()

        if None in (nonce, base_fee, priority_fee):
            print_error("Could not fetch chain parameters")
            return

        max_fee = base_fee * 2 + priority_fee

        tx = self.tx_manager.create_eth_transfer(
            from_address=self.address,
            to_address=to_addr,
            amount_eth=amount,
            nonce=nonce,
            max_fee_per_gas=max_fee,
            max_priority_fee_per_gas=priority_fee,
        )

        if not tx:
            return

        # Load wallet and sign
        container = self.wallet.load_encrypted_container()
        if not container:
            print_error("Could not load wallet")
            return

        password = get_password_input("Enter wallet password: ")
        if not password:
            return

        signed = self.tx_manager.sign_transaction_secure(
            tx, container, password, wallet_manager=self.wallet,
        )

        if not signed:
            return

        if not confirm_dangerous_action("Broadcast to Base?", "SEND"):
            print_info("Cancelled")
            return

        tx_hash = self.network.send_raw_transaction("0x" + signed.hex())
        if tx_hash:
            print_success(f"Tx hash: {tx_hash}")
            print_info(f"Explorer: {self.network.explorer_url(tx_hash)}")

    # ── Helpers ──────────────────────────────────────────────

    def check_balance_manual(self):
        print_section_header("CHECK ADDRESS BALANCE")
        addr = get_text_input("Enter Base address (0x...): ")
        if not EVMWalletManager.validate_address(addr):
            print_error("Invalid address")
            return
        balance = self.network.get_balance(addr)
        if balance is not None:
            print_info(f"Address: {addr}")
            print_info(f"Balance: {balance:.8f} ETH")
            print_info(f"Explorer: {self.network.explorer_address_url(addr)}")
        else:
            print_error("Could not fetch balance")

    def check_erc20_balance(self):
        print_section_header("CHECK ERC-20 TOKEN BALANCE")
        if not self.address:
            print_error("No wallet loaded")
            return
        token_addr = get_text_input("Token contract address (0x...): ")
        if not EVMWalletManager.validate_address(token_addr):
            print_error("Invalid token address")
            return
        raw_balance = self.network.get_erc20_balance(token_addr, self.address)
        if raw_balance is not None:
            print_info(f"Raw balance: {raw_balance}")
            print_info(f"(Divide by 10^decimals for human-readable amount)")
        else:
            print_error("Could not fetch token balance")

    def show_network_info(self):
        print_section_header("NETWORK INFO")
        info = self.network.get_network_info()
        for k, v in info.items():
            print_info(f"  {k}: {v}")

    def view_on_explorer(self):
        if self.address:
            url = self.network.explorer_address_url(self.address)
            print_info(f"BaseScan: {url}")
        else:
            print_error("No wallet loaded")


def main():
    testnet = "--testnet" in sys.argv or "-t" in sys.argv

    if testnet:
        print_info("Running on Base Sepolia testnet")
    else:
        print_info("Running on Base Mainnet")

    cli = BaseCLI(testnet=testnet)
    cli.run()


if __name__ == "__main__":
    main()
