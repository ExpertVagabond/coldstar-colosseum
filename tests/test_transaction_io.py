"""
Tests for transaction module: fee calculation, transaction creation,
serialization/deserialization, and transaction info decoding.

These tests mock the Rust signer dependency since the FFI library
may not be available in all test environments.
"""

import base64
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from solders.hash import Hash
from solders.keypair import Keypair
from solders.message import Message
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction


# ---------------------------------------------------------------------------
# Patch Rust signer at module level so transaction.py can be imported
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _patch_signer(monkeypatch):
    """Prevent transaction.py from calling sys.exit when Rust signer is missing."""
    import sys

    fake_signer_mod = type(sys)("python_signer_example")
    fake_signer_mod.SolanaSecureSigner = MagicMock
    monkeypatch.setitem(sys.modules, "python_signer_example", fake_signer_mod)


def _import_transaction():
    from src.transaction import TransactionManager
    return TransactionManager


def _make_unsigned_tx():
    """Helper: build a real unsigned Solana transfer transaction."""
    from_kp = Keypair()
    to_pk = Pubkey.from_string("2BqcFZhc4CPa7sbwa5QCKxTWJB1UZUgEV3fLUQjXgrjn")
    blockhash = Hash.from_string("11111111111111111111111111111111")
    ix = transfer(TransferParams(
        from_pubkey=from_kp.pubkey(),
        to_pubkey=to_pk,
        lamports=1_000_000,
    ))
    msg = Message.new_with_blockhash([ix], from_kp.pubkey(), blockhash)
    tx = Transaction.new_unsigned(msg)
    return bytes(tx), from_kp, to_pk, blockhash


# ── Fee calculation ───────────────────────────────────────────────────────


class TestFeeCalculation:
    def test_one_percent_fee(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        fee = mgr.calculate_infrastructure_fee(1.0)
        assert abs(fee - 0.01) < 1e-12

    def test_zero_amount(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        fee = mgr.calculate_infrastructure_fee(0.0)
        assert fee == 0.0

    def test_large_amount(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        fee = mgr.calculate_infrastructure_fee(1000.0)
        assert abs(fee - 10.0) < 1e-12


# ── Transaction creation ─────────────────────────────────────────────────


class TestTransactionCreation:
    def test_create_transfer_transaction(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        kp = Keypair()
        to_pk = "2BqcFZhc4CPa7sbwa5QCKxTWJB1UZUgEV3fLUQjXgrjn"
        blockhash = "11111111111111111111111111111111"
        result = mgr.create_transfer_transaction(
            from_pubkey=str(kp.pubkey()),
            to_pubkey=to_pk,
            amount_sol=0.5,
            recent_blockhash=blockhash,
        )
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_transaction_has_correct_structure(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        kp = Keypair()
        to_pk = "2BqcFZhc4CPa7sbwa5QCKxTWJB1UZUgEV3fLUQjXgrjn"
        blockhash = "11111111111111111111111111111111"
        tx_bytes = mgr.create_transfer_transaction(
            from_pubkey=str(kp.pubkey()),
            to_pubkey=to_pk,
            amount_sol=1.0,
            recent_blockhash=blockhash,
        )
        tx = Transaction.from_bytes(tx_bytes)
        # 1% fee means 2 instructions: main transfer + fee transfer
        assert len(tx.message.instructions) == 2

    def test_zero_fee_single_instruction(self):
        """When fee is 0, there should be only 1 instruction."""
        TxMgr = _import_transaction()
        mgr = TxMgr()
        kp = Keypair()
        to_pk = "2BqcFZhc4CPa7sbwa5QCKxTWJB1UZUgEV3fLUQjXgrjn"
        blockhash = "11111111111111111111111111111111"
        # amount 0 means 0 lamports fee
        tx_bytes = mgr.create_transfer_transaction(
            from_pubkey=str(kp.pubkey()),
            to_pubkey=to_pk,
            amount_sol=0.0,
            recent_blockhash=blockhash,
        )
        tx = Transaction.from_bytes(tx_bytes)
        assert len(tx.message.instructions) == 1

    def test_invalid_pubkey_returns_none(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        result = mgr.create_transfer_transaction(
            from_pubkey="invalid",
            to_pubkey="also-invalid",
            amount_sol=1.0,
            recent_blockhash="11111111111111111111111111111111",
        )
        assert result is None


# ── Save / Load unsigned transaction ──────────────────────────────────────


class TestTransactionSerialization:
    def test_save_and_load_unsigned(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        tx_bytes, *_ = _make_unsigned_tx()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            assert mgr.save_unsigned_transaction(tx_bytes, path)
            loaded = mgr.load_unsigned_transaction(path)
            assert loaded == tx_bytes
        finally:
            os.unlink(path)

    def test_load_nonexistent_returns_none(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        result = mgr.load_unsigned_transaction("/nonexistent/tx.json")
        assert result is None

    def test_save_and_load_signed(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        # Use a real signed transaction
        kp = Keypair()
        to_pk = Pubkey.from_string("2BqcFZhc4CPa7sbwa5QCKxTWJB1UZUgEV3fLUQjXgrjn")
        blockhash = Hash.from_string("11111111111111111111111111111111")
        ix = transfer(TransferParams(from_pubkey=kp.pubkey(), to_pubkey=to_pk, lamports=5000))
        msg = Message.new_with_blockhash([ix], kp.pubkey(), blockhash)
        tx = Transaction.new_unsigned(msg)
        tx.sign([kp], blockhash)
        signed_bytes = bytes(tx)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            assert mgr.save_signed_transaction(signed_bytes, path)
            loaded = mgr.load_signed_transaction(path)
            assert loaded == signed_bytes
        finally:
            os.unlink(path)

    def test_load_wrong_type_returns_none(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"type": "signed_transaction", "version": "1.0", "data": "AAAA"}, f)
            path = f.name
        try:
            # Try loading as unsigned — should fail because type is "signed_transaction"
            result = mgr.load_unsigned_transaction(path)
            assert result is None
        finally:
            os.unlink(path)

    def test_saved_format_structure(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        tx_bytes, *_ = _make_unsigned_tx()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            mgr.save_unsigned_transaction(tx_bytes, path)
            with open(path) as fh:
                data = json.load(fh)
            assert data["type"] == "unsigned_transaction"
            assert data["version"] == "1.0"
            # data field should be valid base64
            decoded = base64.b64decode(data["data"])
            assert decoded == tx_bytes
        finally:
            os.unlink(path)


# ── Transaction info decoding ─────────────────────────────────────────────


class TestDecodeTransactionInfo:
    def test_decode_unsigned(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        tx_bytes, from_kp, _, _ = _make_unsigned_tx()
        info = mgr.decode_transaction_info(tx_bytes)
        assert info is not None
        assert info["num_instructions"] == 1
        assert info["fee_payer"] == str(from_kp.pubkey())

    def test_decode_signed(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        kp = Keypair()
        to_pk = Pubkey.from_string("2BqcFZhc4CPa7sbwa5QCKxTWJB1UZUgEV3fLUQjXgrjn")
        blockhash = Hash.from_string("11111111111111111111111111111111")
        ix = transfer(TransferParams(from_pubkey=kp.pubkey(), to_pubkey=to_pk, lamports=5000))
        msg = Message.new_with_blockhash([ix], kp.pubkey(), blockhash)
        tx = Transaction.new_unsigned(msg)
        tx.sign([kp], blockhash)
        info = mgr.decode_transaction_info(bytes(tx))
        assert info is not None
        assert info["is_signed"]
        assert info["signatures"] >= 1

    def test_decode_garbage_returns_none(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        result = mgr.decode_transaction_info(b"\x00\x01\x02")
        assert result is None


# ── Broadcast format ──────────────────────────────────────────────────────


class TestBroadcastFormat:
    def test_no_signed_tx_returns_none(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        assert mgr.get_transaction_for_broadcast() is None

    def test_broadcast_format_is_base64(self):
        TxMgr = _import_transaction()
        mgr = TxMgr()
        kp = Keypair()
        to_pk = Pubkey.from_string("2BqcFZhc4CPa7sbwa5QCKxTWJB1UZUgEV3fLUQjXgrjn")
        blockhash = Hash.from_string("11111111111111111111111111111111")
        ix = transfer(TransferParams(from_pubkey=kp.pubkey(), to_pubkey=to_pk, lamports=5000))
        msg = Message.new_with_blockhash([ix], kp.pubkey(), blockhash)
        tx = Transaction.new_unsigned(msg)
        tx.sign([kp], blockhash)
        mgr.signed_tx = bytes(tx)
        b64 = mgr.get_transaction_for_broadcast()
        assert b64 is not None
        decoded = base64.b64decode(b64)
        assert decoded == mgr.signed_tx
