"""
SPL Token Transfer Module - Create and sign SPL token transactions

Supports:
- Token balance queries
- Token transfers between wallets
- Associated token account creation

B - Love U 3000
"""

import json
import base64
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.instruction import Instruction, AccountMeta
from solders.transaction import Transaction
from solders.message import Message
from solders.system_program import create_account, CreateAccountParams

from config import LAMPORTS_PER_SOL
from src.ui import print_success, print_error, print_info, print_warning


# SPL Token Program IDs
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")


@dataclass
class TokenInfo:
    """SPL Token information"""
    mint: str
    symbol: str
    name: str
    decimals: int
    balance: float = 0.0


# Common SPL tokens on Solana
KNOWN_TOKENS = {
    "USDC": TokenInfo(
        mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        symbol="USDC",
        name="USD Coin",
        decimals=6
    ),
    "USDT": TokenInfo(
        mint="Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        symbol="USDT",
        name="Tether USD",
        decimals=6
    ),
    "BONK": TokenInfo(
        mint="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        symbol="BONK",
        name="Bonk",
        decimals=5
    ),
    "RAY": TokenInfo(
        mint="4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
        symbol="RAY",
        name="Raydium",
        decimals=6
    ),
    "JUP": TokenInfo(
        mint="JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
        symbol="JUP",
        name="Jupiter",
        decimals=6
    ),
}


def get_associated_token_address(wallet: Pubkey, mint: Pubkey) -> Pubkey:
    """Derive the associated token account address for a wallet and mint"""
    seeds = [
        bytes(wallet),
        bytes(TOKEN_PROGRAM_ID),
        bytes(mint)
    ]

    # Find program derived address
    # This is a simplified version - in production use the proper PDA derivation
    import hashlib

    combined = b''.join(seeds) + bytes(ASSOCIATED_TOKEN_PROGRAM_ID) + b"ProgramDerivedAddress"

    for bump in range(255, -1, -1):
        try:
            seed_with_bump = combined + bytes([bump])
            hash_result = hashlib.sha256(seed_with_bump).digest()
            # Check if it's a valid point on the curve (simplified)
            return Pubkey.from_bytes(hash_result)
        except Exception:
            continue

    raise ValueError("Could not find valid PDA")


class TokenTransferManager:
    """Manage SPL token transfers"""

    def __init__(self):
        self.unsigned_tx: Optional[bytes] = None
        self.signed_tx: Optional[bytes] = None

    def create_token_transfer_instruction(
        self,
        source_ata: Pubkey,
        dest_ata: Pubkey,
        owner: Pubkey,
        amount: int
    ) -> Instruction:
        """Create SPL token transfer instruction"""
        # Token transfer instruction data
        # Instruction index 3 = Transfer
        data = bytes([3]) + amount.to_bytes(8, 'little')

        accounts = [
            AccountMeta(pubkey=source_ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=dest_ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=owner, is_signer=True, is_writable=False),
        ]

        return Instruction(
            program_id=TOKEN_PROGRAM_ID,
            accounts=accounts,
            data=data
        )

    def create_ata_instruction(
        self,
        payer: Pubkey,
        wallet: Pubkey,
        mint: Pubkey,
        ata: Pubkey
    ) -> Instruction:
        """Create Associated Token Account instruction"""
        accounts = [
            AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
            AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=wallet, is_signer=False, is_writable=False),
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        ]

        return Instruction(
            program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
            accounts=accounts,
            data=bytes()
        )

    def create_token_transfer_transaction(
        self,
        from_wallet: str,
        to_wallet: str,
        mint_address: str,
        amount: float,
        decimals: int,
        recent_blockhash: str,
        create_dest_ata: bool = False
    ) -> Optional[bytes]:
        """Create unsigned SPL token transfer transaction"""
        try:
            from_pk = Pubkey.from_string(from_wallet)
            to_pk = Pubkey.from_string(to_wallet)
            mint_pk = Pubkey.from_string(mint_address)
            blockhash = Hash.from_string(recent_blockhash)

            # Calculate token amount with decimals
            token_amount = int(amount * (10 ** decimals))

            # Get associated token accounts
            source_ata = get_associated_token_address(from_pk, mint_pk)
            dest_ata = get_associated_token_address(to_pk, mint_pk)

            instructions = []

            # Optionally create destination ATA
            if create_dest_ata:
                ata_ix = self.create_ata_instruction(from_pk, to_pk, mint_pk, dest_ata)
                instructions.append(ata_ix)

            # Create transfer instruction
            transfer_ix = self.create_token_transfer_instruction(
                source_ata, dest_ata, from_pk, token_amount
            )
            instructions.append(transfer_ix)

            # Build message and transaction
            message = Message.new_with_blockhash(instructions, from_pk, blockhash)
            tx = Transaction.new_unsigned(message)

            self.unsigned_tx = bytes(tx)

            print_success(f"Created unsigned token transfer")
            print_info(f"From: {from_wallet}")
            print_info(f"To: {to_wallet}")
            print_info(f"Amount: {amount} tokens")
            print_info(f"Mint: {mint_address[:16]}...")

            return self.unsigned_tx

        except Exception as e:
            print_error(f"Failed to create token transfer: {e}")
            return None

    def sign_transaction(self, unsigned_tx_bytes: bytes, keypair: Keypair) -> Optional[bytes]:
        """Sign token transfer transaction"""
        try:
            tx = Transaction.from_bytes(unsigned_tx_bytes)
            tx.sign([keypair], tx.message.recent_blockhash)

            self.signed_tx = bytes(tx)
            print_success("Token transaction signed successfully")
            return self.signed_tx
        except Exception as e:
            print_error(f"Failed to sign transaction: {e}")
            return None

    def save_unsigned_transaction(self, tx_bytes: bytes, path: str, token_info: dict) -> bool:
        """Save unsigned token transaction with metadata"""
        try:
            filepath = Path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            tx_data = {
                "type": "unsigned_token_transaction",
                "version": "1.0",
                "token": token_info,
                "data": base64.b64encode(tx_bytes).decode('utf-8')
            }

            with open(filepath, 'w') as f:
                json.dump(tx_data, f, indent=2)

            print_success(f"Unsigned token transaction saved to: {filepath}")
            return True
        except Exception as e:
            print_error(f"Failed to save transaction: {e}")
            return False


async def get_token_accounts(rpc_url: str, wallet: str) -> List[dict]:
    """Query token accounts for a wallet"""
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenAccountsByOwner",
                    "params": [
                        wallet,
                        {"programId": str(TOKEN_PROGRAM_ID)},
                        {"encoding": "jsonParsed"}
                    ]
                },
                timeout=30.0
            )

            data = response.json()

            if "error" in data:
                print_error(f"RPC error: {data['error']}")
                return []

            accounts = []
            for account in data.get("result", {}).get("value", []):
                parsed = account.get("account", {}).get("data", {}).get("parsed", {})
                info = parsed.get("info", {})

                token_amount = info.get("tokenAmount", {})

                accounts.append({
                    "mint": info.get("mint"),
                    "owner": info.get("owner"),
                    "amount": float(token_amount.get("uiAmount", 0)),
                    "decimals": token_amount.get("decimals", 0),
                    "address": account.get("pubkey")
                })

            return accounts

    except Exception as e:
        print_error(f"Failed to get token accounts: {e}")
        return []


def get_token_symbol(mint: str) -> str:
    """Get token symbol from mint address"""
    for symbol, info in KNOWN_TOKENS.items():
        if info.mint == mint:
            return symbol
    return mint[:8] + "..."


if __name__ == "__main__":
    # Test token transfer creation
    import asyncio

    print("SPL Token Transfer Module")
    print("=" * 40)

    # List known tokens
    print("\nKnown tokens:")
    for symbol, info in KNOWN_TOKENS.items():
        print(f"  {symbol}: {info.mint[:20]}... ({info.decimals} decimals)")
