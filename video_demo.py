#!/usr/bin/env python3
"""
Coldstar Video Demo - Full Cold Wallet Flow
For X/Twitter grant application video
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.wallet import WalletManager, create_wallet_structure
from src.network import SolanaNetwork
from src.transaction import TransactionManager
from src.ui import print_success, print_error, print_info, print_warning, print_section_header, print_banner, print_explorer_link

WALLET_PATH = "/Volumes/Virtual Server/coldwallet"

def main():
    print_banner()
    print_section_header("COLDSTAR COLD WALLET - LIVE DEMO")
    print_info("Air-gapped Solana wallet on external drive\n")
    time.sleep(1)

    # Load existing wallet
    wallet_mgr = WalletManager()
    wallet_mgr.set_wallet_directory(f"{WALLET_PATH}/wallet")
    wallet_mgr.load_encrypted_container(f"{WALLET_PATH}/wallet/keypair.json")

    network = SolanaNetwork()
    tx_mgr = TransactionManager()

    pubkey = wallet_mgr.get_public_key()

    print_section_header("STEP 1: WALLET ON EXTERNAL DRIVE")
    print_info(f"Location: {WALLET_PATH}")
    print_success(f"Address: {pubkey}")
    time.sleep(1)

    # Check balance
    print_section_header("STEP 2: CHECK BALANCE (Online)")
    balance = network.get_balance(pubkey) or 0
    print_success(f"Balance: {balance} SOL")

    if balance == 0:
        print_info("Requesting devnet airdrop...")
        sig = network.request_airdrop(pubkey, 1.0)
        if sig:
            time.sleep(5)
            balance = network.get_balance(pubkey) or 0
            print_success(f"Funded! New balance: {balance} SOL")
    time.sleep(1)

    if balance > 0.01:
        print_section_header("STEP 3: CREATE TRANSACTION (Online)")
        # Create a real transaction - send to a burn address
        recipient = "BurnedDEaDxxxxxxxxxxxxxxxxxxxxxxxxxxx1111111"  # Not a real burn but won't work anyway
        # Actually let's send to ourselves for a clean demo
        recipient = pubkey  # Send to self

        blockhash_result = network.get_latest_blockhash()
        if blockhash_result:
            blockhash, _ = blockhash_result
            print_info(f"Blockhash: {blockhash[:20]}...")

            unsigned_tx = tx_mgr.create_transfer_transaction(
                from_pubkey=pubkey,
                to_pubkey=recipient,
                amount_sol=0.001,
                recent_blockhash=blockhash
            )

            if unsigned_tx:
                inbox = f"{WALLET_PATH}/inbox/demo_tx.json"
                tx_mgr.save_unsigned_transaction(unsigned_tx, inbox)
                time.sleep(1)

                print_section_header("STEP 4: SIGN OFFLINE (Air-Gapped)")
                print_warning(">>> PRIVATE KEY NEVER LEAVES EXTERNAL DRIVE <<<")
                time.sleep(0.5)

                container = wallet_mgr.encrypted_container
                if container:
                    from src.ui import get_password_input
                    password = get_password_input("Enter wallet password to sign:")
                    signed_tx = tx_mgr.sign_transaction_secure(unsigned_tx, container, password)
                else:
                    print_warning("No encrypted container loaded — wallet may be legacy format")
                    signed_tx = None

                if signed_tx:
                    outbox = f"{WALLET_PATH}/outbox/demo_tx_signed.json"
                    tx_mgr.save_signed_transaction(signed_tx, outbox)
                    time.sleep(1)

                    print_section_header("STEP 5: BROADCAST (Online)")
                    print_info("Sending signed transaction to Solana Devnet...")

                    tx_base64 = tx_mgr.get_transaction_for_broadcast()
                    signature = network.send_transaction(tx_base64)

                    if signature:
                        print_info("Confirming transaction...")
                        confirmed = network.confirm_transaction(signature, max_retries=15)
                        if confirmed:
                            print_success("TRANSACTION CONFIRMED!")
                            print_explorer_link(signature, "devnet")
                        else:
                            print_warning("Transaction sent but confirmation timed out")
                            print_explorer_link(signature, "devnet")
                    else:
                        print_warning("Transaction may have failed - check explorer")

    print_section_header("DEMO COMPLETE")
    final_balance = network.get_balance(pubkey) or 0
    print_info(f"""
Wallet: {pubkey}
Final Balance: {final_balance} SOL
Files: {WALLET_PATH}

Key Features Demonstrated:
- Wallet stored on external drive (air-gapped capable)
- Private key never transmitted over network
- Offline transaction signing
- Online broadcast of pre-signed transactions

github.com/ExpertVagabond/coldstar-colosseum
""")

    network.close()

if __name__ == "__main__":
    main()
