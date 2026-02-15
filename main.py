#!/usr/bin/env python3
"""
Solana Cold Wallet USB Tool
Main CLI Entry Point

A terminal-based tool for creating and managing Solana cold wallets on USB drives.

B - Love U 3000
"""

import sys
import os
import tempfile
from pathlib import Path

from rich.console import Console

from config import APP_NAME, APP_VERSION, SOLANA_RPC_URL
from src.ui import (
    print_banner, print_success, print_error, print_info, print_warning,
    print_section_header, print_wallet_info, print_transaction_summary,
    print_device_list, select_menu_option, get_text_input, get_float_input,
    get_password_input, confirm_dangerous_action, print_explorer_link,
    clear_screen, console
)
from src.wallet import WalletManager, create_wallet_structure
from src.usb import USBManager
from src.network import SolanaNetwork
from src.transaction import TransactionManager
from src.iso_builder import ISOBuilder
from src.backup import WalletBackup
from src.jupiter_integration import JupiterSwapManager, sol_to_lamports, lamports_to_sol
from src.pyth_integration import PythPriceClient, format_usd
from src.fairscore_integration import FairScoreClient, format_reputation_badge


class SolanaColdWalletCLI:
    def __init__(self):
        self.wallet_manager = WalletManager()
        self.usb_manager = USBManager()
        self.network = SolanaNetwork()
        self.transaction_manager = TransactionManager()
        self.iso_builder = ISOBuilder()
        self.backup_manager = WalletBackup()
        self.jupiter_manager = JupiterSwapManager(slippage_bps=50)  # 0.5% slippage
        self.pyth_client = PythPriceClient()
        self.fairscore_client = FairScoreClient()

        self.current_usb_device = None
        self.current_public_key = None
        self.usb_is_cold_wallet = False
    
    def _check_usb_for_wallet(self, mount_point: str) -> tuple:
        """Check if mounted USB has a cold wallet with pubkey.txt"""
        pubkey_path = Path(mount_point) / "wallet" / "pubkey.txt"
        if pubkey_path.exists():
            with open(pubkey_path, 'r') as f:
                return True, f.read().strip()
        return False, None
    
    def _display_wallet_balance(self):
        if not self.current_public_key:
            return

        print_section_header("WALLET STATUS")
        balance = self.network.get_balance(self.current_public_key)
        print_wallet_info(self.current_public_key, balance)

        # Show USD value if online
        if self.network.is_connected() and balance is not None and balance > 0:
            try:
                sol_price = self.pyth_client.get_price("SOL/USD")
                if sol_price:
                    usd_value = balance * sol_price["price"]
                    print_info(f"≈ {format_usd(usd_value)} USD (SOL @ ${sol_price['price']:.2f})")
            except:
                pass  # Silently fail if price fetch fails

        # Show wallet reputation
        if self.network.is_connected() and self.current_public_key:
            try:
                assessment = self.fairscore_client.get_risk_assessment(self.current_public_key)
                if assessment["available"]:
                    badge = format_reputation_badge(assessment["tier"])
                    print_info(f"Wallet Reputation: {badge}")
            except:
                pass

        console.print()
    
    def run(self):
        # B - Love U 3000
        while True:
            try:
                self.main_menu()
            except KeyboardInterrupt:
                console.print("\n")
                print_info("Exiting...")
                self.cleanup()
                sys.exit(0)
            except Exception as e:
                print_error(f"Error: {e}")
                continue
    
    def _draw_header(self):
        clear_screen()
        print_banner()
        print_info(f"Network: {SOLANA_RPC_URL}")
        if self.network.is_connected():
            print_success("Status: Connected")
        else:
            print_warning("Status: Offline")
        console.print()
    
    def main_menu(self):
        self._draw_header()
        devices = self.usb_manager.detect_usb_devices()
        
        if not devices:
            self._no_usb_menu()
        elif self.usb_is_cold_wallet and self.current_public_key:
            self._wallet_menu()
        else:
            self._usb_detected_menu(devices)
    
    def _no_usb_menu(self):
        print_section_header("NO USB DEVICE DETECTED")
        print_warning("Please connect a USB drive to continue.")
        console.print()
        
        options = [
            "1. Refresh (Check for USB)",
            "2. Network Status",
            "0. Exit"
        ]
        
        choice = select_menu_option(options, "Select an option:")
        
        if choice is None:
            return
        
        choice_num = choice.split(".")[0].strip()
        
        if choice_num == "2":
            self._draw_header()
            self.show_network_status()
            self._wait_for_key()
        elif choice_num == "0":
            self.exit_app()
    
    def _wait_for_key(self):
        console.print()
        console.input("[dim]Press Enter to continue...[/dim]")
    
    def _usb_detected_menu(self, devices):
        print_section_header("USB DEVICE DETECTED")
        print_device_list(devices)
        console.print()
        
        options = [
            "1. Flash Cold Wallet OS to USB",
            "2. Mount USB (Check for existing wallet)",
            "3. Network Status",
            "0. Exit"
        ]
        
        choice = select_menu_option(options, "Select an option:")
        
        if choice is None:
            return
        
        choice_num = choice.split(".")[0].strip()
        
        if choice_num == "1":
            self._draw_header()
            self.flash_cold_wallet()
            self._wait_for_key()
        elif choice_num == "2":
            self._mount_and_check_wallet(devices)
        elif choice_num == "3":
            self._draw_header()
            self.show_network_status()
            self._wait_for_key()
        elif choice_num == "0":
            self.exit_app()
    
    def _mount_and_check_wallet(self, devices):
        if len(devices) == 1:
            idx = 0
            device = devices[0]
        else:
            device_options = [f"{i+1}. {d['device']} ({d['size']})" for i, d in enumerate(devices)]
            device_options.append("Cancel")
            
            selection = select_menu_option(device_options, "Select device to mount:")
            
            if not selection or "Cancel" in selection:
                return
            
            idx = int(selection.split(".")[0]) - 1
            device = devices[idx]
        
        # Select the device first so USB manager has the context
        self.usb_manager.select_device(idx)
        
        mount_point = self.usb_manager.mount_device(device['device'])
        if mount_point:
            is_wallet, pubkey = self._check_usb_for_wallet(mount_point)
            if is_wallet:
                self.usb_is_cold_wallet = True
                self.current_public_key = pubkey
                self.current_usb_device = device
                print_success("Cold wallet found on USB!")
                print_info(f"Public Key: {pubkey}")
                # Load the wallet
                wallet_dir = Path(mount_point) / "wallet"
                self.wallet_manager.set_wallet_directory(str(wallet_dir))
                self._display_wallet_balance()
            else:
                print_info("No wallet found on this USB.")
                # Offer to create a wallet
                create_choice = select_menu_option(
                    ["Yes, create a new wallet", "No, go back"],
                    "Would you like to create a new wallet on this USB?"
                )
                if create_choice and "Yes" in create_choice:
                    self._create_wallet_on_usb(mount_point, device)
    
    def _create_wallet_on_usb(self, mount_point: str, device: dict):
        """Generate and save a new wallet on the USB drive"""
        print_section_header("CREATING NEW WALLET")
        
        wallet_dir = Path(mount_point) / "wallet"
        wallet_dir.mkdir(parents=True, exist_ok=True)
        
        self.wallet_manager.set_wallet_directory(str(wallet_dir))
        
        print_info("Generating new Solana keypair...")
        keypair, public_key = self.wallet_manager.generate_keypair()
        
        print_warning("⚠️  SECURITY WARNING ⚠️")
        print_warning("You are creating a wallet on a device connected to this computer.")
        print_warning("For maximum security, private keys should be generated OFFLINE.")
        console.print()
        
        confirm = confirm_dangerous_action(
            "Generate wallet on this USB drive?",
            "CREATE"
        )
        
        if not confirm:
            print_info("Wallet creation cancelled")
            return
        
        if self.wallet_manager.save_keypair():
            self.usb_is_cold_wallet = True
            self.current_public_key = public_key
            self.current_usb_device = device
            
            print_success("✓ Wallet created successfully!")
            console.print()
            print_info(f"Public Key: {public_key}")
            print_info(f"Wallet saved to: {wallet_dir}")
            console.print()
            print_warning("IMPORTANT: Keep this USB drive secure and offline!")
            print_warning("Anyone with access to keypair.json can control your funds.")
            console.print()
            self._display_wallet_balance()
        else:
            print_error("Failed to create wallet")
    
    def _wallet_menu(self):
        self._display_wallet_balance()
        
        print_section_header("WALLET OPERATIONS")
        
        options = [
            "1. View Wallet / Balance",
            "2. Send SOL (Create Unsigned Transaction)",
            "3. Sign Transaction (Offline)",
            "4. Broadcast Signed Transaction",
            "5. Quick Send (Create+Sign+Broadcast - INSECURE)",
            "6. View Transaction History",
            "7. Backup / Restore Wallet",
            "8. Request Devnet Airdrop",
            "9. Network Status",
            "J. Jupiter Swap (Create Unsigned Swap)",
            "F. Check FairScore Reputation",
            "A. Unmount USB / Switch Device",
            "0. Exit"
        ]
        
        choice = select_menu_option(options, "Select an option:")
        
        if choice is None:
            return
        
        choice_num = choice.split(".")[0].strip()
        
        if choice_num == "1":
            self._draw_header()
            self.view_wallet_info()
            self._wait_for_key()
        elif choice_num == "2":
            self._draw_header()
            self.create_unsigned_transaction()
            self._wait_for_key()
        elif choice_num == "3":
            self._draw_header()
            self.sign_transaction()
            self._wait_for_key()
        elif choice_num == "4":
            self._draw_header()
            self.broadcast_transaction()
            self._wait_for_key()
        elif choice_num == "5":
            self._draw_header()
            self.quick_send_transaction()
            self._wait_for_key()
        elif choice_num == "6":
            self._draw_header()
            self.view_transaction_history()
            self._wait_for_key()
        elif choice_num == "7":
            self._draw_header()
            self.backup_restore_wallet()
            self._wait_for_key()
        elif choice_num == "8":
            self._draw_header()
            self.request_airdrop()
            self._wait_for_key()
        elif choice_num == "9":
            self._draw_header()
            self.show_network_status()
            self._wait_for_key()
        elif choice_num.upper() == "J":
            self._draw_header()
            self.jupiter_swap()
            self._wait_for_key()
        elif choice_num.upper() == "F":
            self._draw_header()
            self.check_fairscore_reputation()
            self._wait_for_key()
        elif choice_num.upper() == "A":
            self._unmount_usb()
        elif choice_num == "0":
            self.exit_app()
    
    def _unmount_usb(self):
        if self.current_usb_device:
            self.usb_manager.unmount_device(self.current_usb_device['device'])
        self.current_usb_device = None
        self.current_public_key = None
        self.usb_is_cold_wallet = False
        print_success("USB unmounted. You can now remove or switch devices.")
    
    def detect_usb_devices(self):
        print_section_header("USB DEVICE DETECTION")
        
        print_info("Scanning for USB devices...")
        devices = self.usb_manager.detect_usb_devices()
        
        if devices:
            print_device_list(devices)
            
            console.print()
            mount_choice = select_menu_option(
                ["Yes, select and mount a device", "No, return to main menu"],
                "Would you like to mount a device?"
            )
            
            if mount_choice and "Yes" in mount_choice:
                device_options = [f"{i+1}. {d['device']} ({d['size']})" for i, d in enumerate(devices)]
                device_options.append("Cancel")
                
                selection = select_menu_option(device_options, "Select a device:")
                
                if selection and "Cancel" not in selection:
                    idx = int(selection.split(".")[0]) - 1
                    self.usb_manager.select_device(idx)
                    
                    if self.usb_manager.check_permissions():
                        mount_point = self.usb_manager.mount_device()
                        if mount_point:
                            if self.usb_manager.check_wallet_exists():
                                print_success("Wallet found on USB device!")
                                paths = self.usb_manager.get_wallet_paths()
                                self.wallet_manager.set_wallet_directory(paths['wallet'])
                            else:
                                print_info("No wallet found on this device")
                    else:
                        print_warning("Run with sudo for USB mounting")
        else:
            print_warning("No USB devices detected")
            print_info("Make sure your USB drive is properly connected")
    
    def flash_cold_wallet(self):
        print_section_header("FLASH COLD WALLET OS TO USB")
        
        # Only check root on Linux systems
        if not self.usb_manager.is_windows and not self.usb_manager.is_root():
            print_error("This operation requires root privileges")
            print_info("Please run: sudo python main.py")
            return
        
        print_info("This will create a bootable cold wallet USB drive")
        print_warning("ALL DATA on the target USB will be ERASED!")
        console.print()
        
        devices = self.usb_manager.detect_usb_devices()
        
        if not devices:
            print_error("No USB devices found")
            return
        
        print_device_list(devices)
        
        device_options = [f"{i+1}. {d['device']} ({d['size']} - {d['model']})" for i, d in enumerate(devices)]
        device_options.append("Cancel")
        
        selection = select_menu_option(device_options, "Select target USB device:")
        
        if not selection or "Cancel" in selection:
            print_info("Operation cancelled")
            return
        
        idx = int(selection.split(".")[0]) - 1
        selected_device = devices[idx]
        
        print_section_header("BUILDING COLD WALLET IMAGE")
        
        work_dir = tempfile.mkdtemp(prefix="solana_wallet_")
        
        try:
            tarball = self.iso_builder.download_alpine_rootfs(work_dir)
            if not tarball:
                return
            
            rootfs = self.iso_builder.extract_rootfs(tarball)
            if not rootfs:
                return
            
            if not self.iso_builder.configure_offline_os():
                return
            
            image = self.iso_builder.build_iso()
            if not image:
                return
            
            if self.iso_builder.flash_to_usb(selected_device['device']):
                print_section_header("SUCCESS")
                print_success("Cold wallet USB created successfully!")
                console.print()
                print_info("Next steps:")
                print_info("1. Boot from this USB on an AIR-GAPPED computer")
                print_info("2. Wallet keypair will generate ON THE DEVICE (never online)")
                print_info("3. Record the public key displayed on screen")
                print_info("4. Use inbox/outbox directories for transaction signing")
                console.print()
                print_warning("SECURITY: The private key is generated and stays")
                print_warning("ONLY on the air-gapped device - maximum security!")
            
        finally:
            self.iso_builder.cleanup()
    
    def view_wallet_info(self):
        print_section_header("WALLET INFORMATION")
        
        if self.current_public_key:
            balance = self.network.get_balance(self.current_public_key)
            print_wallet_info(self.current_public_key, balance)
        else:
            print_info("No wallet connected. Mount a USB with a cold wallet first.")
            manual = get_text_input("Or enter a public key to check balance: ")
            if manual and self.wallet_manager.validate_address(manual):
                balance = self.network.get_balance(manual)
                if balance is not None:
                    print_wallet_info(manual, balance)
                else:
                    print_wallet_info(manual)
    
    def quick_send_transaction(self):
        """Create, sign, and broadcast a transaction in one step (for testing only)"""
        print_section_header("QUICK SEND (INSECURE - TESTING ONLY)")
        
        print_warning("⚠️  SECURITY WARNING ⚠️")
        print_warning("This creates, signs, and broadcasts a transaction immediately.")
        print_warning("Private key is loaded on an ONLINE device - NOT secure for production!")
        print_info("For secure cold wallet operation, use the 3-step process:")
        print_info("  1. Create Unsigned Transaction")
        print_info("  2. Sign on Air-Gapped Device")
        print_info("  3. Broadcast Signed Transaction")
        console.print()
        
        if not self.current_public_key:
            print_error("No wallet connected. Mount a USB with a cold wallet first.")
            return
        
        # Load encrypted wallet container for secure signing
        wallet_dir = Path(self.usb_manager.mount_point) / "wallet"
        keypair_path = wallet_dir / "keypair.json"

        if not keypair_path.exists():
            print_error("Keypair not found on USB")
            return

        container = self.wallet_manager.load_encrypted_container(str(keypair_path))
        if not container:
            print_error("Failed to load wallet. Legacy unencrypted wallets must be upgraded first.")
            return

        password = get_password_input("Enter wallet password to sign transaction:")
        if not password:
            print_error("Password required for encrypted wallet")
            return

        from_address = self.current_public_key
        print_info(f"From: {from_address}")
        
        balance = self.network.get_balance(from_address)
        if balance is not None:
            print_info(f"Current balance: {balance:.9f} SOL")
        
        console.print()
        
        to_address = get_text_input("Enter recipient's public key: ")
        if not self.wallet_manager.validate_address(to_address):
            print_error("Invalid recipient address")
            return
        
        amount = get_float_input("Enter amount to send (SOL): ")
        if amount <= 0:
            print_error("Amount must be greater than 0")
            return
        
        if balance is not None and amount >= balance:
            print_warning(f"Amount ({amount} SOL) exceeds available balance ({balance} SOL)")
            if not confirm_dangerous_action("Proceed anyway?", "YES"):
                return
        
        console.print()
        print_transaction_summary(from_address, to_address, amount)
        console.print()
        
        if not confirm_dangerous_action("Send this transaction NOW?", "SEND"):
            print_info("Transaction cancelled")
            return
        
        # Get fresh blockhash
        blockhash_result = self.network.get_latest_blockhash()
        if not blockhash_result:
            print_error("Failed to get blockhash from network")
            return
        
        blockhash, _ = blockhash_result
        
        # Create transaction
        tx_bytes = self.transaction_manager.create_transfer_transaction(
            from_address, to_address, amount, blockhash
        )
        
        if not tx_bytes:
            return
        
        # Sign transaction securely via Rust signer
        print_info("Signing transaction...")
        signed_tx = self.transaction_manager.sign_transaction_secure(tx_bytes, container, password)

        if not signed_tx:
            return

        # Broadcast transaction
        print_info("Broadcasting transaction...")
        
        import base64
        tx_base64 = base64.b64encode(signed_tx).decode('utf-8')
        
        signature = self.network.send_transaction(tx_base64)
        
        if signature:
            print_success("Transaction sent!")
            print_info(f"Signature: {signature}")
            print_info("Waiting for confirmation...")
            
            if self.network.confirm_transaction(signature):
                print_success("✓ Transaction confirmed!")
                console.print()
                
                # Refresh balance after successful transaction
                import time
                time.sleep(2)  # Wait a bit for balance to update on chain
                new_balance = self.network.get_balance(from_address)
                if new_balance is not None:
                    print_success(f"Updated balance: {new_balance:.9f} SOL")
                
                print_explorer_link(signature, "devnet")
            else:
                print_warning("Transaction sent but confirmation timed out")
                print_info("Check the explorer for final status")
                console.print()
                print_explorer_link(signature, "devnet")
    
    def create_unsigned_transaction(self):
        print_section_header("CREATE UNSIGNED TRANSACTION")

        if not self.current_public_key:
            print_error("No wallet connected. Mount a USB with a cold wallet first.")
            return

        from_address = self.current_public_key
        print_info(f"From: {from_address}")

        balance = self.network.get_balance(from_address)
        if balance is not None:
            print_info(f"Current balance: {balance:.9f} SOL")

        console.print()

        to_address = get_text_input("Enter recipient's public key: ")
        if not self.wallet_manager.validate_address(to_address):
            print_error("Invalid recipient address")
            return

        # FairScore reputation check before proceeding
        if self.network.is_connected():
            console.print()
            print_section_header("FAIRSCORE REPUTATION CHECK")
            print_info(f"Checking reputation for {to_address[:12]}...{to_address[-8:]}")
            console.print()

            self.fairscore_client.display_reputation_badge(to_address, verbose=True)
            console.print()

            should_block, block_reason = self.fairscore_client.should_block_transaction(to_address)

            if should_block:
                print_error("TRANSACTION BLOCKED")
                print_error(block_reason)
                print_warning("Coldstar will not create transactions to untrusted wallets.")
                print_info("If you believe this is an error, verify the address and try again.")
                return

            assessment = self.fairscore_client.get_risk_assessment(to_address)
            if assessment["tier"] == 2:
                print_warning("PROCEED WITH CAUTION")
                print_warning("This wallet has a low trust score. Only proceed if you know the recipient.")
                console.print()
                if not confirm_dangerous_action("Send to low-trust wallet?", "PROCEED"):
                    print_info("Transaction cancelled for safety")
                    return

            console.print()
        else:
            print_warning("Offline mode - skipping FairScore reputation check")
            console.print()

        amount = get_float_input("Enter amount to send (SOL): ")
        if amount <= 0:
            print_error("Amount must be greater than 0")
            return
        
        if balance is not None and amount >= balance:
            print_warning(f"Amount ({amount} SOL) exceeds available balance ({balance} SOL)")
            if not confirm_dangerous_action("Proceed anyway?", "YES"):
                return
        
        console.print()
        print_transaction_summary(from_address, to_address, amount)
        console.print()
        
        if not confirm_dangerous_action("Create this transaction?", "CREATE"):
            print_info("Transaction cancelled")
            return
        
        blockhash_result = self.network.get_latest_blockhash()
        if not blockhash_result:
            print_error("Failed to get blockhash from network")
            return
        
        blockhash, _ = blockhash_result
        
        tx_bytes = self.transaction_manager.create_transfer_transaction(
            from_address, to_address, amount, blockhash
        )
        
        if tx_bytes:
            if self.usb_manager.mount_point:
                inbox_dir = Path(self.usb_manager.mount_point) / "inbox"
                inbox_dir.mkdir(exist_ok=True)
                output_dir = inbox_dir
            else:
                output_dir = Path("./transactions")
                output_dir.mkdir(exist_ok=True)
            
            import time
            filename = f"unsigned_tx_{int(time.time())}.json"
            output_path = output_dir / filename
            
            if self.transaction_manager.save_unsigned_transaction(tx_bytes, str(output_path)):
                console.print()
                print_success("Unsigned transaction created!")
                print_info(f"File: {output_path}")
                if self.usb_manager.mount_point:
                    print_info("Transaction saved to USB inbox.")
                    print_info("Boot the USB on an air-gapped computer to sign.")
                else:
                    print_info("Copy this file to your cold wallet's /inbox directory for signing")
    
    def sign_transaction(self):
        print_section_header("SIGN TRANSACTION")
        
        if not self.usb_manager.mount_point:
            print_error("No USB mounted. Mount your cold wallet USB first.")
            return
        
        inbox_dir = Path(self.usb_manager.mount_point) / "inbox"
        outbox_dir = Path(self.usb_manager.mount_point) / "outbox"
        outbox_dir.mkdir(exist_ok=True)
        
        # Look for unsigned transactions in inbox
        unsigned_files = list(inbox_dir.glob("unsigned_*.json")) if inbox_dir.exists() else []
        
        if not unsigned_files:
            print_warning("No unsigned transactions found in USB inbox.")
            print_info("Create a transaction first using 'Send SOL' option.")
            return
        
        print_success(f"Found {len(unsigned_files)} unsigned transaction(s)")
        console.print()
        
        # Offer signing options
        print_warning("⚠️  SECURITY NOTICE ⚠️")
        print_warning("For maximum security, transactions should be signed on an AIR-GAPPED device.")
        print_info("This device has the private key loaded and is ONLINE.")
        console.print()
        
        sign_choice = select_menu_option(
            ["Yes, sign on this device (INSECURE - for testing only)", "No, I'll sign offline"],
            "Sign transaction on this online device?"
        )
        
        if not sign_choice or "No" in sign_choice:
            print_info("Copy unsigned transactions to an air-gapped device for secure signing.")
            return
        
        # Load encrypted wallet container for secure signing
        wallet_dir = Path(self.usb_manager.mount_point) / "wallet"
        keypair_path = wallet_dir / "keypair.json"

        if not keypair_path.exists():
            print_error("Keypair not found on USB")
            return

        container = self.wallet_manager.load_encrypted_container(str(keypair_path))
        if not container:
            print_error("Failed to load wallet. Legacy unencrypted wallets must be upgraded first.")
            return

        password = get_password_input("Enter wallet password to sign transaction:")
        if not password:
            print_error("Password required for encrypted wallet")
            return

        # Let user select which transaction to sign
        file_options = [f.name for f in unsigned_files]
        file_options.append("Cancel")
        
        selection = select_menu_option(file_options, "Select transaction to sign:")
        
        if not selection or "Cancel" in selection:
            return
        
        tx_path = inbox_dir / selection
        
        # Load and sign the transaction
        unsigned_tx = self.transaction_manager.load_unsigned_transaction(str(tx_path))
        if not unsigned_tx:
            return

        print_info("Signing transaction securely via Rust signer...")
        signed_tx = self.transaction_manager.sign_transaction_secure(unsigned_tx, container, password)
        
        if signed_tx:
            # Save to outbox with signed_ prefix
            output_name = selection.replace("unsigned_", "signed_")
            output_path = outbox_dir / output_name
            
            if self.transaction_manager.save_signed_transaction(signed_tx, str(output_path)):
                print_success("Transaction signed and saved to outbox!")
                print_info(f"Signed file: {output_name}")
                print_info("You can now broadcast this transaction.")
                
                # Optionally delete the unsigned transaction
                delete_choice = select_menu_option(
                    ["Yes", "No"],
                    "Delete the unsigned transaction from inbox?"
                )
                
                if delete_choice and "Yes" in delete_choice:
                    tx_path.unlink()
                    print_success("Unsigned transaction removed from inbox.")
    
    def broadcast_transaction(self):
        print_section_header("BROADCAST SIGNED TRANSACTION")
        
        if not self.usb_manager.mount_point:
            print_error("No USB mounted. Mount your cold wallet USB first.")
            return
        
        outbox_dir = Path(self.usb_manager.mount_point) / "outbox"
        
        signed_files = list(outbox_dir.glob("signed_*.json")) if outbox_dir.exists() else []
        
        if not signed_files:
            print_warning("No signed transactions found in USB outbox")
            print_info("Sign transactions on the air-gapped device first.")
            return
        
        file_options = [f.name for f in signed_files]
        file_options.append("Cancel")
        
        selection = select_menu_option(file_options, "Select transaction to broadcast:")
        
        if not selection or "Cancel" in selection:
            return
        
        tx_path = outbox_dir / selection
        
        tx_bytes = self.transaction_manager.load_signed_transaction(str(tx_path))
        if not tx_bytes:
            return
        
        tx_info = self.transaction_manager.decode_transaction_info(tx_bytes)
        if tx_info:
            print_info(f"Transaction has {tx_info['num_instructions']} instruction(s)")
            print_info(f"Signed: {'Yes' if tx_info['is_signed'] else 'No'}")
        
        console.print()
        print_warning("This will broadcast the transaction to the Solana network")
        if not confirm_dangerous_action("Broadcast this transaction?", "BROADCAST"):
            return
        
        tx_base64 = self.transaction_manager.get_transaction_for_broadcast()
        if not tx_base64:
            return
        
        signature = self.network.send_transaction(tx_base64)
        
        if signature:
            print_info("Waiting for confirmation...")
            
            if self.network.confirm_transaction(signature):
                print_success("Transaction confirmed!")
                console.print()
                
                # Refresh balance after successful transaction
                import time
                time.sleep(2)  # Wait for balance to update on chain
                if self.current_public_key:
                    new_balance = self.network.get_balance(self.current_public_key)
                    if new_balance is not None:
                        print_success(f"Updated balance: {new_balance:.9f} SOL")
            else:
                print_warning("Transaction sent but confirmation timed out")
                print_info("Check the explorer for final status")
            
            print_explorer_link(signature, "devnet")
    
    def view_transaction_history(self):
        """View recent transaction history for the wallet"""
        print_section_header("TRANSACTION HISTORY")
        
        if not self.current_public_key:
            print_error("No wallet connected. Mount a USB with a cold wallet first.")
            return
        
        public_key = self.current_public_key
        print_info(f"Wallet: {public_key}")
        console.print()
        
        limit = get_float_input("Number of transactions to show (1-50): ", 10)
        limit = int(min(max(limit, 1), 50))  # Clamp between 1 and 50
        
        print_info(f"Fetching last {limit} transactions...")
        console.print()
        
        transactions = self.network.get_transaction_history(public_key, limit)
        
        if not transactions:
            print_warning("No transaction history found")
            return
        
        print_success(f"Found {len(transactions)} transaction(s)")
        console.print()
        
        from rich.table import Table
        
        table = Table(title="Recent Transactions", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Signature", style="cyan", width=50)
        table.add_column("Status", width=12)
        table.add_column("Slot", justify="right", width=10)
        table.add_column("Time", width=20)
        
        for idx, tx in enumerate(transactions, 1):
            signature = tx.get("signature", "Unknown")
            slot = str(tx.get("slot", "N/A"))
            
            # Determine status
            err = tx.get("err")
            if err is None:
                status = "[green]✓ Success[/green]"
            else:
                status = "[red]✗ Failed[/red]"
            
            # Format timestamp
            block_time = tx.get("blockTime")
            if block_time:
                import datetime
                dt = datetime.datetime.fromtimestamp(block_time)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = "Pending"
            
            # Truncate signature for display
            sig_display = signature[:20] + "..." + signature[-20:] if len(signature) > 44 else signature
            
            table.add_row(
                str(idx),
                sig_display,
                status,
                slot,
                time_str
            )
        
        console.print(table)
        console.print()
        
        # Offer to view details of a specific transaction
        view_details = select_menu_option(
            ["Yes", "No"],
            "View details of a specific transaction?"
        )
        
        if view_details and "Yes" in view_details:
            tx_num = get_float_input(f"Enter transaction number (1-{len(transactions)}): ", 1)
            tx_idx = int(tx_num) - 1
            
            if 0 <= tx_idx < len(transactions):
                signature = transactions[tx_idx]["signature"]
                self._show_transaction_details(signature)
            else:
                print_error("Invalid transaction number")
    
    def _show_transaction_details(self, signature: str):
        """Show detailed information about a specific transaction"""
        console.print()
        print_info(f"Fetching details for transaction: {signature[:20]}...")
        
        details = self.network.get_transaction_details(signature)
        
        if not details:
            print_error("Could not fetch transaction details")
            return
        
        console.print()
        print_success("Transaction Details:")
        console.print()
        
        from rich.panel import Panel
        from rich.json import JSON
        
        # Extract key information
        meta = details.get("meta", {})
        transaction = details.get("transaction", {})
        
        info_text = f"""[bold]Signature:[/bold] {signature}
[bold]Slot:[/bold] {details.get('slot', 'N/A')}
[bold]Block Time:[/bold] {details.get('blockTime', 'N/A')}
[bold]Fee:[/bold] {meta.get('fee', 0) / 1000000000} SOL

[bold]Status:[/bold] {'✓ Success' if meta.get('err') is None else '✗ Failed'}
[bold]Pre Balance:[/bold] {meta.get('preBalances', [0])[0] / 1000000000} SOL
[bold]Post Balance:[/bold] {meta.get('postBalances', [0])[0] / 1000000000} SOL
"""
        
        console.print(Panel(info_text, title="Transaction Info", border_style="cyan"))
        console.print()
        
        # Show explorer link
        print_explorer_link(signature, "devnet")
    
    def backup_restore_wallet(self):
        """Backup or restore wallet with multiple options"""
        print_section_header("WALLET BACKUP / RESTORE")

        if not self.usb_manager.mount_point:
            print_error("No USB mounted. Mount your cold wallet USB first.")
            return

        wallet_dir = Path(self.usb_manager.mount_point) / "wallet"
        keypair_path = wallet_dir / "keypair.json"

        if not keypair_path.exists():
            print_warning("No wallet found on USB.")
            # Offer restore option
            restore_choice = select_menu_option(
                ["Yes, restore from backup", "No, go back"],
                "Would you like to restore a wallet from backup?"
            )
            if restore_choice and "Yes" in restore_choice:
                self._restore_wallet(wallet_dir)
            return

        # Load encrypted container and decrypt for backup operations
        container = self.wallet_manager.load_encrypted_container(str(keypair_path))
        if not container:
            print_error("Failed to load wallet. Legacy unencrypted wallets must be upgraded first.")
            return

        # Show public key from file (no decryption needed)
        pubkey = self.wallet_manager.get_public_key_from_file(
            str(wallet_dir / "pubkey.txt")
        )
        if pubkey:
            print_info(f"Wallet: {pubkey[:16]}...")
        else:
            print_info("Wallet: [encrypted — pubkey.txt not found]")
        console.print()

        options = [
            "1. Create Paper Wallet (Printable HTML with QR)",
            "2. Export Encrypted Backup",
            "3. Export Plaintext Backup (NOT SECURE)",
            "4. Generate Mnemonic Seed Phrase",
            "5. Restore from Backup File",
            "6. Cancel"
        ]

        choice = select_menu_option(options, "Select backup option:")

        if choice is None or "Cancel" in choice:
            return

        choice_num = choice.split(".")[0].strip()

        # Create backups directory
        backup_dir = Path(self.usb_manager.mount_point) / "backups"
        backup_dir.mkdir(exist_ok=True)

        if choice_num in ("1", "2", "3"):
            # Options 1-3 require decrypting the wallet to access the keypair
            wallet_password = get_password_input("Enter wallet password to decrypt for backup:")
            if not wallet_password:
                print_error("Password required to decrypt wallet")
                return

            # Decrypt via Rust signer to get temporary keypair
            import gc
            try:
                from src.secure_memory import SecureWalletHandler
                # Try Rust signer first
                if self.wallet_manager.rust_signer:
                    normalized = self.wallet_manager._normalize_container_format(container)
                    private_key = self.wallet_manager.rust_signer.decrypt_private_key(
                        normalized, wallet_password
                    )
                    if not private_key or len(private_key) != 32:
                        print_error("Invalid password or corrupted wallet")
                        return
                    from solders.keypair import Keypair
                    keypair = Keypair.from_bytes(bytes(private_key))
                    del private_key
                else:
                    # Fallback to PyNaCl
                    keypair = SecureWalletHandler.decrypt_keypair(container, wallet_password)
                    if not keypair:
                        print_error("Invalid password or corrupted wallet")
                        return
            except Exception as e:
                print_error(f"Failed to decrypt wallet: {e}")
                return

            try:
                if choice_num == "1":
                    # Paper wallet
                    print_info("Creating paper wallet...")
                    path = self.backup_manager.create_paper_wallet(keypair, str(backup_dir))
                    if path:
                        print_success(f"Paper wallet created: {path}")
                        print_info("Open this HTML file in a browser to print.")
                        print_warning("IMPORTANT: Print on a secure, offline printer!")

                elif choice_num == "2":
                    # Encrypted backup
                    print_warning("Enter a strong password for the backup (minimum 8 characters)")
                    backup_password = get_text_input("Backup password: ")
                    if len(backup_password) < 8:
                        print_error("Password must be at least 8 characters")
                        return

                    confirm_pw = get_text_input("Confirm backup password: ")
                    if backup_password != confirm_pw:
                        print_error("Passwords don't match")
                        return

                    import time
                    backup_path = backup_dir / f"encrypted_backup_{int(time.time())}.json"

                    if self.backup_manager.backup_to_file(keypair, str(backup_path), backup_password):
                        print_success(f"Encrypted backup saved to: {backup_path}")
                        print_info("Store this file securely. You'll need the password to restore.")

                elif choice_num == "3":
                    # Plaintext backup
                    print_warning("⚠️  WARNING: Plaintext backups are NOT secure!")
                    print_warning("Anyone with access to this file can steal your funds.")

                    confirm_action = confirm_dangerous_action(
                        "Create unencrypted backup?",
                        "INSECURE"
                    )

                    if confirm_action:
                        import time
                        backup_path = backup_dir / f"plaintext_backup_{int(time.time())}.json"
                        if self.backup_manager.backup_to_file(keypair, str(backup_path)):
                            print_success(f"Plaintext backup saved to: {backup_path}")
            finally:
                # Always clear decrypted keypair from memory
                del keypair
                gc.collect()

        elif choice_num == "4":
            # Generate mnemonic
            if not self.backup_manager.mnemonic_available:
                print_warning("mnemonic library not installed")
                print_info("Install with: pip install mnemonic")
                return

            print_warning("⚠️  IMPORTANT SECURITY NOTICE ⚠️")
            print_warning("The mnemonic phrase gives FULL ACCESS to your wallet.")
            print_warning("Write it down on paper - NEVER store digitally!")
            console.print()

            word_choice = select_menu_option(
                ["12 words (standard)", "24 words (extra security)"],
                "Select mnemonic length:"
            )

            if word_choice:
                strength = 128 if "12" in word_choice else 256
                mnemonic = self.backup_manager.generate_mnemonic(strength)

                if mnemonic:
                    console.print()
                    print_section_header("YOUR SEED PHRASE")
                    words = mnemonic.split()
                    for i, word in enumerate(words, 1):
                        console.print(f"  {i:2}. {word}")
                    console.print()
                    print_warning("Write these words down in order!")
                    print_warning("NEVER share or store digitally!")
                    print_info("You can use these words to recover your wallet.")

        elif choice_num == "5":
            self._restore_wallet(wallet_dir)

    def _restore_wallet(self, wallet_dir: Path):
        """Restore wallet from backup file"""
        print_section_header("RESTORE WALLET")

        backup_dir = Path(self.usb_manager.mount_point) / "backups"
        backup_files = list(backup_dir.glob("*.json")) if backup_dir.exists() else []

        if backup_files:
            print_success(f"Found {len(backup_files)} backup file(s)")
            file_options = [f.name for f in backup_files]
            file_options.append("Enter custom path")
            file_options.append("Cancel")

            selection = select_menu_option(file_options, "Select backup file:")

            if not selection or "Cancel" in selection:
                return

            if "Enter custom" in selection:
                backup_path = get_text_input("Enter backup file path: ")
            else:
                backup_path = str(backup_dir / selection)
        else:
            backup_path = get_text_input("Enter backup file path: ")

        if not backup_path or not Path(backup_path).exists():
            print_error("Backup file not found")
            return

        # Check if encrypted
        import json
        with open(backup_path, 'r') as f:
            data = json.load(f)

        password = None
        if data.get("type") == "encrypted_keypair":
            password = get_text_input("Enter decryption password: ")

        keypair = self.backup_manager.restore_from_file(backup_path, password)

        if keypair:
            # Save to wallet directory
            wallet_dir.mkdir(parents=True, exist_ok=True)
            keypair_path = wallet_dir / "keypair.json"
            pubkey_path = wallet_dir / "pubkey.txt"

            # Backup existing if present
            if keypair_path.exists():
                print_warning("Existing wallet will be replaced!")
                if not confirm_dangerous_action("Replace existing wallet?", "REPLACE"):
                    return
                import time
                old_backup = wallet_dir / f"keypair_old_{int(time.time())}.json"
                keypair_path.rename(old_backup)
                print_info(f"Old wallet backed up to: {old_backup}")

            # Save new keypair
            with open(keypair_path, 'w') as f:
                json.dump(list(bytes(keypair)), f)

            with open(pubkey_path, 'w') as f:
                f.write(str(keypair.pubkey()))

            self.current_public_key = str(keypair.pubkey())
            print_success("Wallet restored successfully!")
            print_info(f"Public key: {self.current_public_key}")

    def request_airdrop(self):
        print_section_header("REQUEST DEVNET AIRDROP")
        
        if "devnet" not in SOLANA_RPC_URL:
            print_error("Airdrops are only available on Devnet")
            return
        
        if not self.current_public_key:
            print_error("No wallet connected. Mount a USB with a cold wallet first.")
            return
        
        public_key = self.current_public_key
        print_info(f"Wallet: {public_key}")
        
        amount = get_float_input("Enter amount (max 2 SOL): ", 1.0)
        if amount > 2:
            print_warning("Devnet airdrops are limited to 2 SOL")
            amount = 2.0
        
        print_info(f"Requesting {amount} SOL airdrop...")
        
        signature = self.network.request_airdrop(public_key, amount)
        
        if signature:
            print_info("Waiting for confirmation...")
            
            if self.network.confirm_transaction(signature):
                print_success("Airdrop confirmed!")
                console.print()
                
                # Refresh balance after successful airdrop
                import time
                time.sleep(2)  # Wait for balance to update on chain
                balance = self.network.get_balance(public_key)
                if balance is not None:
                    print_success(f"Updated balance: {balance:.9f} SOL")
            else:
                print_warning("Airdrop may still be processing")
            
            print_explorer_link(signature, "devnet")
    
    def show_network_status(self):
        print_section_header("NETWORK STATUS")
        
        print_info(f"RPC URL: {SOLANA_RPC_URL}")
        
        if self.network.is_connected():
            print_success("Connection: OK")
            
            info = self.network.get_network_info()
            if "error" not in info:
                print_info(f"Solana Version: {info.get('version', 'Unknown')}")
                print_info(f"Current Slot: {info.get('slot', 'Unknown')}")
                print_info(f"Current Epoch: {info.get('epoch', 'Unknown')}")
        else:
            print_error("Connection: FAILED")
            print_info("Check your internet connection or RPC URL")
    
    def jupiter_swap(self):
        """Create unsigned Jupiter swap transaction for air-gapped signing"""
        print_section_header("JUPITER SWAP - CREATE UNSIGNED TRANSACTION")

        if not self.current_public_key:
            print_error("No wallet connected. Mount a USB with a cold wallet first.")
            return

        if not self.network.is_connected():
            print_error("No network connection. Jupiter requires online access.")
            return

        print_info(f"Wallet: {self.current_public_key}")
        console.print()

        # Show available tokens
        print_info("Common tokens: SOL, USDC, USDT, BONK, JUP, RAY")
        print_info("Or enter a custom mint address")
        console.print()

        # Get input token
        from_token = get_text_input("From token (e.g., SOL): ", "SOL").strip()
        from_mint = self.jupiter_manager.get_token_address(from_token)

        # Get output token
        to_token = get_text_input("To token (e.g., USDC): ", "USDC").strip()
        to_mint = self.jupiter_manager.get_token_address(to_token)

        # Get amount
        amount_float = get_float_input(f"Amount of {from_token} to swap: ", 0.1)

        # Convert to smallest unit (lamports for SOL)
        if from_token.upper() == "SOL":
            amount = sol_to_lamports(amount_float)
            print_info(f"Amount in lamports: {amount}")
        else:
            # For SPL tokens, assume 6 decimals (USDC/USDT)
            # TODO: Fetch actual decimals from chain
            decimals = 6
            amount = int(amount_float * (10 ** decimals))
            print_info(f"Amount in smallest unit: {amount}")

        console.print()
        print_info("Fetching best route from Jupiter...")

        # Get quote
        quote = self.jupiter_manager.get_quote(
            input_mint=from_mint,
            output_mint=to_mint,
            amount=amount
        )

        if not quote:
            print_error("Failed to get quote from Jupiter")
            return

        # Display quote details
        console.print()
        in_amount = int(quote.get("inAmount", 0))
        out_amount = int(quote.get("outAmount", 0))
        price_impact = float(quote.get("priceImpactPct", 0))

        # Convert back to human-readable
        if from_token.upper() == "SOL":
            display_in = lamports_to_sol(in_amount)
        else:
            display_in = in_amount / (10 ** decimals)

        if to_token.upper() == "SOL":
            display_out = lamports_to_sol(out_amount)
        else:
            display_out = out_amount / (10 ** 6)  # Assume 6 decimals for output

        # Show swap summary
        summary = self.jupiter_manager.get_swap_summary(
            input_symbol=from_token,
            output_symbol=to_token,
            input_amount=display_in,
            output_amount=display_out,
            price_impact=price_impact,
            route_steps=len(quote.get('routePlan', []))
        )
        console.print(summary)
        console.print()

        # Warn about high price impact
        if price_impact > 1.0:
            print_warning(f"⚠️  HIGH PRICE IMPACT: {price_impact:.2f}%")
            console.print()

        # Confirm swap creation
        confirm = select_menu_option(
            ["Yes, create swap transaction", "No, cancel"],
            "Create unsigned swap transaction?"
        )

        if not confirm or "No" in confirm:
            print_info("Swap cancelled")
            return

        # Create unsigned transaction
        print_info("Creating unsigned swap transaction...")
        unsigned_tx = self.jupiter_manager.create_swap_transaction(
            quote=quote,
            user_pubkey=self.current_public_key,
            wrap_unwrap_sol=True
        )

        if not unsigned_tx:
            print_error("Failed to create swap transaction")
            return

        # Save to file
        wallet_dir = Path(self.wallet_manager.wallet_dir) if self.wallet_manager.wallet_dir else Path.cwd()
        inbox_dir = wallet_dir.parent / "inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)

        import time
        timestamp = int(time.time())
        filename = f"swap_{from_token}_to_{to_token}_{timestamp}.json"
        filepath = inbox_dir / filename

        # Prepare quote info for saving
        quote_info = {
            "from_token": from_token,
            "to_token": to_token,
            "from_amount": str(display_in),
            "to_amount": str(display_out),
            "inAmount": quote.get("inAmount"),
            "outAmount": quote.get("outAmount"),
            "priceImpactPct": price_impact,
            "timestamp": timestamp
        }

        if self.jupiter_manager.save_swap_transaction(unsigned_tx, str(filepath), quote_info):
            console.print()
            print_success("✓ Unsigned swap transaction created!")
            print_info(f"Saved to: {filepath}")
            console.print()

            print_section_header("NEXT STEPS")
            print_info("1. Transfer this file to your air-gapped device")
            print_info("2. Sign the transaction on the offline device")
            print_info("3. Transfer the signed transaction back")
            print_info("4. Broadcast using option 4 in the wallet menu")
            console.print()

            print_warning("⚠️  IMPORTANT: Review transaction details on offline device before signing!")
            print_warning("Jupiter swaps interact with multiple programs and accounts.")

    def check_fairscore_reputation(self):
        """Check FairScore reputation for any wallet address"""
        print_section_header("FAIRSCORE REPUTATION LOOKUP")

        if not self.network.is_connected():
            print_error("No network connection. FairScore requires online access.")
            return

        console.print()
        print_info("Enter a Solana wallet address to check its reputation.")
        console.print()

        address = get_text_input("Wallet address: ").strip()

        if not address:
            print_info("Cancelled")
            return

        if not self.wallet_manager.validate_address(address):
            print_error("Invalid Solana address")
            return

        console.print()
        print_info(f"Checking reputation for {address[:12]}...{address[-8:]}")
        console.print()

        self.fairscore_client.display_reputation_badge(address, verbose=True)
        console.print()

        show_legend = select_menu_option(
            ["Yes, show tier explanations", "No, return to menu"],
            "Show FairScore tier legend?",
        )

        if show_legend and "Yes" in show_legend:
            self.fairscore_client.display_tier_legend()

    def exit_app(self):
        print_info("Cleaning up...")
        self.cleanup()
        print_success("Goodbye!")
        sys.exit(0)
    
    def cleanup(self):
        try:
            self.network.close()
            self.fairscore_client.close()
            if self.usb_manager.mount_point:
                self.usb_manager.unmount_device()
        except Exception:
            pass


def main():
    cli = SolanaColdWalletCLI()
    cli.run()


if __name__ == "__main__":
    main()
