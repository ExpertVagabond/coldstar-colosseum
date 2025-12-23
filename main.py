#!/usr/bin/env python3
"""
Solana Cold Wallet USB Tool
Main CLI Entry Point

A terminal-based tool for creating and managing Solana cold wallets on USB drives.
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
    confirm_dangerous_action, print_explorer_link, clear_screen, console
)
from src.wallet import WalletManager, create_wallet_structure
from src.usb import USBManager
from src.network import SolanaNetwork
from src.transaction import TransactionManager
from src.iso_builder import ISOBuilder


class SolanaColdWalletCLI:
    def __init__(self):
        self.wallet_manager = WalletManager()
        self.usb_manager = USBManager()
        self.network = SolanaNetwork()
        self.transaction_manager = TransactionManager()
        self.iso_builder = ISOBuilder()
        
        self.local_wallet_dir = Path("./local_wallet")
        self.local_wallet_dir.mkdir(exist_ok=True)
        
        self.wallet_configured = False
        self.current_public_key = None
    
    def _check_existing_wallet(self) -> bool:
        local_keypair = self.local_wallet_dir / "keypair.json"
        if local_keypair.exists():
            self.wallet_manager.set_wallet_directory(str(self.local_wallet_dir))
            self.wallet_manager.load_keypair()
            self.current_public_key = self.wallet_manager.get_public_key()
            self.wallet_configured = True
            return True
        return False
    
    def _display_wallet_balance(self):
        if not self.current_public_key:
            return
        
        print_section_header("WALLET STATUS")
        balance = self.network.get_balance(self.current_public_key)
        print_wallet_info(self.current_public_key, balance)
        console.print()
    
    def run(self):
        clear_screen()
        print_banner()
        
        print_info(f"Connected to: {SOLANA_RPC_URL}")
        
        if self.network.is_connected():
            print_success("Network connection: OK")
        else:
            print_warning("Network connection: Failed (some features unavailable)")
        
        console.print()
        
        if self._check_existing_wallet():
            self._display_wallet_balance()
        
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
    
    def main_menu(self):
        print_section_header("MAIN MENU")
        
        if self.wallet_configured:
            options = [
                "1. View Wallet / Balance",
                "2. Send SOL",
                "3. Sign Transaction (Offline)",
                "4. Broadcast Signed Transaction",
                "5. Request Devnet Airdrop",
                "6. Network Status",
                "7. Generate New Wallet",
                "0. Exit"
            ]
            
            actions = {
                "1": self.view_wallet_info,
                "2": self.create_unsigned_transaction,
                "3": self.sign_transaction,
                "4": self.broadcast_transaction,
                "5": self.request_airdrop,
                "6": self.show_network_status,
                "7": self.generate_local_wallet,
                "0": self.exit_app
            }
        else:
            options = [
                "1. Detect USB Devices",
                "2. Flash Cold Wallet OS to USB",
                "3. Generate New Wallet",
                "0. Exit"
            ]
            
            actions = {
                "1": self.detect_usb_devices,
                "2": self.flash_cold_wallet,
                "3": self.generate_local_wallet,
                "0": self.exit_app
            }
        
        choice = select_menu_option(options, "Select an option:")
        
        if choice is None:
            return
        
        choice_num = choice.split(".")[0].strip()
        
        action = actions.get(choice_num)
        if action:
            action()
    
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
        
        if not self.usb_manager.is_root():
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
                print_info("1. Boot from this USB drive")
                print_info("2. The wallet will be initialized on first boot")
                print_info("3. Record the public key displayed")
                print_info("4. Use the inbox/outbox for transaction signing")
            
        finally:
            self.iso_builder.cleanup()
    
    def generate_local_wallet(self):
        print_section_header("GENERATE NEW WALLET")
        
        wallet_path = self.local_wallet_dir / "keypair.json"
        
        if wallet_path.exists():
            print_warning("A wallet already exists in the local directory")
            if not confirm_dangerous_action(
                "Creating a new wallet will REPLACE the existing one!",
                "REPLACE"
            ):
                print_info("Operation cancelled")
                return
        
        self.wallet_manager.set_wallet_directory(str(self.local_wallet_dir))
        
        keypair, public_key = self.wallet_manager.generate_keypair()
        
        if self.wallet_manager.save_keypair(str(wallet_path)):
            self.wallet_configured = True
            self.current_public_key = public_key
            
            console.print()
            balance = self.network.get_balance(public_key)
            print_wallet_info(public_key, balance)
            console.print()
            print_warning("IMPORTANT: Back up your keypair.json file securely!")
            print_info(f"Keypair location: {wallet_path}")
    
    def view_wallet_info(self):
        print_section_header("WALLET INFORMATION")
        
        wallet_options = []
        
        local_keypair = self.local_wallet_dir / "keypair.json"
        if local_keypair.exists():
            wallet_options.append("Local wallet (./local_wallet)")
        
        if self.usb_manager.mount_point and self.usb_manager.check_wallet_exists():
            wallet_options.append(f"USB wallet ({self.usb_manager.mount_point})")
        
        wallet_options.append("Enter public key manually")
        wallet_options.append("Cancel")
        
        if len(wallet_options) == 2:
            print_info("No wallets found. Generate a wallet first.")
            manual = get_text_input("Or enter a public key to check balance: ")
            if manual and self.wallet_manager.validate_address(manual):
                balance = self.network.get_balance(manual)
                if balance is not None:
                    print_wallet_info(manual, balance)
                else:
                    print_wallet_info(manual)
            return
        
        selection = select_menu_option(wallet_options, "Select wallet to view:")
        
        if not selection or "Cancel" in selection:
            return
        
        public_key = None
        
        if "Local" in selection:
            self.wallet_manager.set_wallet_directory(str(self.local_wallet_dir))
            self.wallet_manager.load_keypair()
            public_key = self.wallet_manager.get_public_key()
        elif "USB" in selection:
            paths = self.usb_manager.get_wallet_paths()
            self.wallet_manager.load_keypair(paths['keypair'])
            public_key = self.wallet_manager.get_public_key()
        elif "manually" in selection:
            public_key = get_text_input("Enter public key: ")
            if not self.wallet_manager.validate_address(public_key):
                print_error("Invalid Solana address")
                return
        
        if public_key:
            balance = self.network.get_balance(public_key)
            print_wallet_info(public_key, balance)
    
    def create_unsigned_transaction(self):
        print_section_header("CREATE UNSIGNED TRANSACTION")
        
        from_address = None
        
        local_keypair = self.local_wallet_dir / "keypair.json"
        if local_keypair.exists():
            self.wallet_manager.set_wallet_directory(str(self.local_wallet_dir))
            self.wallet_manager.load_keypair()
            from_address = self.wallet_manager.get_public_key()
        
        if not from_address:
            from_address = get_text_input("Enter sender's public key: ")
            if not self.wallet_manager.validate_address(from_address):
                print_error("Invalid sender address")
                return
        
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
            output_dir = self.local_wallet_dir / "transactions"
            output_dir.mkdir(exist_ok=True)
            
            import time
            filename = f"unsigned_tx_{int(time.time())}.json"
            output_path = output_dir / filename
            
            if self.transaction_manager.save_unsigned_transaction(tx_bytes, str(output_path)):
                console.print()
                print_success("Unsigned transaction created!")
                print_info(f"File: {output_path}")
                print_info("Copy this file to your cold wallet's /inbox directory for signing")
    
    def sign_transaction(self):
        print_section_header("SIGN TRANSACTION (OFFLINE)")
        
        tx_dir = self.local_wallet_dir / "transactions"
        
        unsigned_files = list(tx_dir.glob("unsigned_*.json")) if tx_dir.exists() else []
        
        if not unsigned_files:
            print_warning("No unsigned transactions found")
            manual_path = get_text_input("Enter path to unsigned transaction file: ")
            if manual_path:
                unsigned_files = [Path(manual_path)]
            else:
                return
        
        file_options = [f.name for f in unsigned_files]
        file_options.append("Cancel")
        
        selection = select_menu_option(file_options, "Select transaction to sign:")
        
        if not selection or "Cancel" in selection:
            return
        
        tx_path = tx_dir / selection if tx_dir.exists() else Path(selection)
        
        tx_bytes = self.transaction_manager.load_unsigned_transaction(str(tx_path))
        if not tx_bytes:
            return
        
        keypair = None
        local_keypair = self.local_wallet_dir / "keypair.json"
        
        if local_keypair.exists():
            print_info("Loading local wallet for signing...")
            self.wallet_manager.set_wallet_directory(str(self.local_wallet_dir))
            keypair = self.wallet_manager.load_keypair()
        
        if not keypair:
            keypair_path = get_text_input("Enter path to keypair.json: ")
            if keypair_path:
                keypair = self.wallet_manager.load_keypair(keypair_path)
        
        if not keypair:
            print_error("No keypair available for signing")
            return
        
        print_warning("You are about to sign this transaction with your private key")
        if not confirm_dangerous_action("Sign this transaction?", "SIGN"):
            return
        
        signed_bytes = self.transaction_manager.sign_transaction(tx_bytes, keypair)
        
        if signed_bytes:
            import time
            filename = f"signed_tx_{int(time.time())}.json"
            output_path = tx_dir / filename
            
            if self.transaction_manager.save_signed_transaction(signed_bytes, str(output_path)):
                console.print()
                print_success("Transaction signed successfully!")
                print_info(f"Signed transaction: {output_path}")
    
    def broadcast_transaction(self):
        print_section_header("BROADCAST SIGNED TRANSACTION")
        
        tx_dir = self.local_wallet_dir / "transactions"
        
        signed_files = list(tx_dir.glob("signed_*.json")) if tx_dir.exists() else []
        
        if not signed_files:
            print_warning("No signed transactions found")
            manual_path = get_text_input("Enter path to signed transaction file: ")
            if manual_path:
                signed_files = [Path(manual_path)]
            else:
                return
        
        file_options = [f.name for f in signed_files]
        file_options.append("Cancel")
        
        selection = select_menu_option(file_options, "Select transaction to broadcast:")
        
        if not selection or "Cancel" in selection:
            return
        
        tx_path = tx_dir / selection if tx_dir.exists() else Path(selection)
        
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
            else:
                print_warning("Transaction sent but confirmation timed out")
                print_info("Check the explorer for final status")
            
            print_explorer_link(signature, "devnet")
    
    def request_airdrop(self):
        print_section_header("REQUEST DEVNET AIRDROP")
        
        if "devnet" not in SOLANA_RPC_URL:
            print_error("Airdrops are only available on Devnet")
            return
        
        public_key = None
        
        local_keypair = self.local_wallet_dir / "keypair.json"
        if local_keypair.exists():
            self.wallet_manager.set_wallet_directory(str(self.local_wallet_dir))
            self.wallet_manager.load_keypair()
            public_key = self.wallet_manager.get_public_key()
            print_info(f"Using wallet: {public_key}")
        
        if not public_key:
            public_key = get_text_input("Enter public key for airdrop: ")
            if not self.wallet_manager.validate_address(public_key):
                print_error("Invalid address")
                return
        
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
                
                balance = self.network.get_balance(public_key)
                if balance is not None:
                    print_info(f"New balance: {balance:.9f} SOL")
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
    
    def exit_app(self):
        print_info("Cleaning up...")
        self.cleanup()
        print_success("Goodbye!")
        sys.exit(0)
    
    def cleanup(self):
        try:
            self.network.close()
            if self.usb_manager.mount_point:
                self.usb_manager.unmount_device()
        except Exception:
            pass


def main():
    cli = SolanaColdWalletCLI()
    cli.run()


if __name__ == "__main__":
    main()
