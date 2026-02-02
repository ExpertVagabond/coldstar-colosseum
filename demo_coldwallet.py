#!/usr/bin/env python3
"""
Coldstar Cold Wallet Demo
Demonstrates offline wallet generation & transaction signing on external drive
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.wallet import WalletManager, create_wallet_structure
from src.network import SolanaNetwork
from src.transaction import TransactionManager
from src.ui import print_success, print_error, print_info, print_warning, print_section_header, print_banner

# Use external drive or local fallback
EXTERNAL_DRIVE = "/Volumes/Virtual Server/coldwallet"
LOCAL_FALLBACK = "./local_wallet"

def main():
    print_banner()
    print_section_header("COLDSTAR COLD WALLET DEMO")
    print_info("Demonstrating air-gapped Solana wallet functionality\n")

    # Setup wallet directory
    wallet_base = EXTERNAL_DRIVE if os.path.exists("/Volumes/Virtual Server") else LOCAL_FALLBACK
    print_info(f"Wallet location: {wallet_base}")

    # Create wallet structure
    dirs = create_wallet_structure(wallet_base)
    wallet_dir = dirs['wallet']

    # Initialize managers
    wallet_mgr = WalletManager()
    wallet_mgr.set_wallet_directory(wallet_dir)

    network = SolanaNetwork()
    tx_mgr = TransactionManager()

    # Check network
    print_info("\n[1/5] Checking Solana Devnet connection...")
    is_connected = network.is_connected()
    if is_connected:
        print_success("Connected to Solana Devnet!")
        net_info = network.get_network_info()
        print_info(f"  Solana version: {net_info.get('version', 'unknown')}")
        print_info(f"  Current slot: {net_info.get('slot', 'unknown')}")
    else:
        print_warning("Network unavailable - offline mode")

    # Generate or load wallet
    print_info("\n[2/5] Setting up wallet...")
    keypair_path = Path(wallet_dir) / "keypair.json"

    if keypair_path.exists():
        print_info("Loading existing wallet...")
        wallet_mgr.load_keypair(str(keypair_path))
    else:
        print_info("Generating new Solana keypair...")
        wallet_mgr.generate_keypair()
        wallet_mgr.save_keypair(str(keypair_path))

    pubkey = wallet_mgr.get_public_key()
    print_success(f"Wallet Address: {pubkey}")

    # Check balance
    print_info("\n[3/5] Checking wallet balance...")
    balance = 0
    if is_connected:
        balance = network.get_balance(pubkey) or 0
        print_success(f"Balance: {balance} SOL")

        # Request airdrop if balance is 0
        if balance == 0:
            print_info("\n[4/5] Requesting devnet airdrop (1 SOL)...")
            sig = network.request_airdrop(pubkey, 1.0)
            if sig:
                print_info("Waiting for confirmation...")
                time.sleep(5)
                new_balance = network.get_balance(pubkey) or 0
                print_success(f"New Balance: {new_balance} SOL")
                balance = new_balance
            else:
                print_warning("Airdrop failed - may be rate limited")
        else:
            print_info("\n[4/5] Wallet already funded, skipping airdrop")
    else:
        print_warning("Offline - cannot check balance")
        print_info("\n[4/5] Skipping airdrop (offline)")

    # Create unsigned transaction (for demo)
    print_info("\n[5/5] Creating sample transaction...")

    if is_connected and balance > 0:
        # Get blockhash for transaction
        blockhash_result = network.get_latest_blockhash()
        if blockhash_result:
            blockhash, _ = blockhash_result
            demo_recipient = "11111111111111111111111111111111"  # System program (demo)

            # Create transfer transaction
            unsigned_tx = tx_mgr.create_transfer_transaction(
                from_pubkey=pubkey,
                to_pubkey=demo_recipient,
                amount_sol=0.001,
                recent_blockhash=blockhash
            )

            if unsigned_tx:
                # Save to inbox
                inbox_path = Path(dirs['inbox']) / "unsigned_tx.json"
                tx_mgr.save_unsigned_transaction(unsigned_tx, str(inbox_path))

                # Sign transaction (this is the offline part)
                print_info("\nSigning transaction with private key (OFFLINE OPERATION)...")
                signed_tx = tx_mgr.sign_transaction(unsigned_tx, wallet_mgr.keypair)

                if signed_tx:
                    outbox_path = Path(dirs['outbox']) / "signed_tx.json"
                    tx_mgr.save_signed_transaction(signed_tx, str(outbox_path))
                    print_success("Transaction signed and ready for broadcast!")
        else:
            print_warning("Could not get blockhash - skipping transaction demo")
    else:
        print_warning("Skipping transaction demo (no balance or offline)")

    print_section_header("COLD WALLET DEMO COMPLETE")
    print_info(f"""
Wallet files created at: {wallet_base}
├── wallet/
│   ├── keypair.json   (PRIVATE KEY - KEEP SECURE!)
│   └── pubkey.txt     (Public address)
├── inbox/             (Place unsigned transactions here)
└── outbox/            (Signed transactions ready to broadcast)

This demonstrates a working Solana cold wallet!
The private key never needs to touch the internet.

Wallet Address: {pubkey}
""")

    network.close()
    return pubkey

if __name__ == "__main__":
    pubkey = main()
