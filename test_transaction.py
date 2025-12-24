"""
Test script to verify transaction construction
"""
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.system_program import transfer, TransferParams
from solders.transaction import Transaction
from solders.message import Message
import base64

# Create test values
from_keypair = Keypair()
to_pubkey = Pubkey.from_string("2BqcFZhc4CPa7sbwa5QCKxTWJB1UZUgEV3fLUQjXgrjn")
lamports = 1000000  # 0.001 SOL

# Mock blockhash
blockhash = Hash.from_string("11111111111111111111111111111111")

# Create transfer instruction
transfer_ix = transfer(
    TransferParams(
        from_pubkey=from_keypair.pubkey(),
        to_pubkey=to_pubkey,
        lamports=lamports
    )
)

print(f"Transfer instruction created:")
print(f"  Program ID: {transfer_ix.program_id}")
print(f"  Accounts: {len(transfer_ix.accounts)}")
print(f"  Data: {transfer_ix.data.hex()}")
print()

# Create message
message = Message.new_with_blockhash(
    [transfer_ix],
    from_keypair.pubkey(),
    blockhash
)

print(f"Message created:")
print(f"  Num instructions: {len(message.instructions)}")
print(f"  Num accounts: {len(message.account_keys)}")
print(f"  Account keys:")
for i, key in enumerate(message.account_keys):
    print(f"    {i}: {key}")
print()

# Create unsigned transaction
tx = Transaction.new_unsigned(message)

print(f"Unsigned transaction:")
print(f"  Message instructions: {len(tx.message.instructions)}")
print()

# Sign it
tx.sign([from_keypair], tx.message.recent_blockhash)

print(f"Signed transaction:")
print(f"  Signatures: {len(tx.signatures)}")
print(f"  Message instructions: {len(tx.message.instructions)}")
print()

# Serialize
tx_bytes = bytes(tx)
tx_base64 = base64.b64encode(tx_bytes).decode('utf-8')

print(f"Serialized transaction (base64):")
print(tx_base64[:100] + "...")
print()
print(f"Total bytes: {len(tx_bytes)}")

# Deserialize and verify
tx_decoded = Transaction.from_bytes(tx_bytes)
print(f"\nDecoded transaction:")
print(f"  Instructions: {len(tx_decoded.message.instructions)}")
print(f"  Accounts: {len(tx_decoded.message.account_keys)}")
for ix in tx_decoded.message.instructions:
    print(f"  Instruction program_id_index: {ix.program_id_index}")
    print(f"  Instruction data: {ix.data.hex()}")
    print(f"  Instruction accounts: {ix.accounts}")
