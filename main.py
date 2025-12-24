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
        
        if choice_num == "1":
            print_info("Scanning for USB devices...")
            devices = self.usb_manager.detect_usb_devices()
            if devices:
                print_success(f"Found {len(devices)} USB device(s)")
            else:
                print_warning("No USB devices found. Please connect a device.")
        elif choice_num == "2":
            self.show_network_status()
        elif choice_num == "0":
            self.exit_app()
    
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
            self.flash_cold_wallet()
        elif choice_num == "2":
            self._mount_and_check_wallet(devices)
        elif choice_num == "3":
            self.show_network_status()
        elif choice_num == "0":
            self.exit_app()
    
    def _mount_and_check_wallet(self, devices):
        if len(devices) == 1:
            device = devices[0]
        else:
            device_options = [f"{i+1}. {d['device']} ({d['size']})" for i, d in enumerate(devices)]
            device_options.append("Cancel")
            
            selection = select_menu_option(device_options, "Select device to mount:")
            
            if not selection or "Cancel" in selection:
                return
            
            idx = int(selection.split(".")[0]) - 1
            device = devices[idx]
        
        mount_point = self.usb_manager.mount_device(device['device'])
        if mount_point:
            is_wallet, pubkey = self._check_usb_for_wallet(mount_point)
            if is_wallet:
                self.usb_is_cold_wallet = True
                self.current_public_key = pubkey
                self.current_usb_device = device
                print_success("Cold wallet found on USB!")
                self._display_wallet_balance()
            else:
                print_info("No wallet found on this USB. You can flash it with Cold Wallet OS.")
    
    def _wallet_menu(self):
        self._display_wallet_balance()
        
        print_section_header("WALLET OPERATIONS")
        
        options = [
            "1. View Wallet / Balance",
            "2. Send SOL",
            "3. Sign Transaction (Offline)",
            "4. Broadcast Signed Transaction",
            "5. Request Devnet Airdrop",
            "6. Network Status",
            "7. Unmount USB / Switch Device",
            "0. Exit"
        ]
        
        choice = select_menu_option(options, "Select an option:")
        
        if choice is None:
            return
        
        choice_num = choice.split(".")[0].strip()
        
        actions = {
            "1": self.view_wallet_info,
            "2": self.create_unsigned_transaction,
            "3": self.sign_transaction,
            "4": self.broadcast_transaction,
            "5": self.request_airdrop,
            "6": self.show_network_status,
            "7": self._unmount_usb,
            "0": self.exit_app
        }
        
        action = actions.get(choice_num)
        if action:
            action()
    
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
        print_info("Signing happens on the AIR-GAPPED cold wallet device.")
        print_info("This option checks for signed transactions in the USB outbox.")
        console.print()
        
        if not self.usb_manager.mount_point:
            print_error("No USB mounted. Mount your cold wallet USB first.")
            return
        
        outbox_dir = Path(self.usb_manager.mount_point) / "outbox"
        
        signed_files = list(outbox_dir.glob("signed_*.json")) if outbox_dir.exists() else []
        
        if signed_files:
            print_success(f"Found {len(signed_files)} signed transaction(s) ready to broadcast")
            for f in signed_files:
                print_info(f"  - {f.name}")
        else:
            print_warning("No signed transactions found in USB outbox.")
            print_info("Boot the cold wallet USB on an air-gapped computer to sign transactions.")
    
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
            else:
                print_warning("Transaction sent but confirmation timed out")
                print_info("Check the explorer for final status")
            
            print_explorer_link(signature, "devnet")
    
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
