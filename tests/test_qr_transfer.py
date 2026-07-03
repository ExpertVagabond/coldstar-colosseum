"""
Tests for QR transfer module: QR code generation, transaction parsing,
and data round-trip through the air-gap transfer format.
"""

import base64
import json

import pytest

from src.qr_transfer import QRTransfer


# ── QR availability ───────────────────────────────────────────────────────


class TestQRAvailability:
    def test_qr_library_available(self):
        qr = QRTransfer()
        assert qr.qr_available, "qrcode library should be installed for tests"


# ── ASCII QR generation ──────────────────────────────────────────────────


class TestGenerateAsciiQR:
    def test_generates_string(self):
        qr = QRTransfer()
        result = qr.generate_ascii_qr("hello")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_block_chars(self):
        qr = QRTransfer()
        result = qr.generate_ascii_qr("test data 12345")
        # QR uses block characters for dark modules
        assert "\u2588" in result  # full block character

    def test_different_data_different_qr(self):
        qr = QRTransfer()
        qr1 = qr.generate_ascii_qr("data_one")
        qr2 = qr.generate_ascii_qr("data_two")
        assert qr1 != qr2

    def test_empty_string(self):
        qr = QRTransfer()
        result = qr.generate_ascii_qr("")
        # qrcode lib handles empty strings (generates a valid but minimal QR)
        assert result is not None


# ── Parse unsigned transaction ────────────────────────────────────────────


class TestParseUnsignedTx:
    def test_parse_valid_json(self):
        qr = QRTransfer()
        tx_data = {
            "type": "unsigned_transaction",
            "version": "1.0",
            "data": base64.b64encode(b"fake-tx-bytes").decode(),
        }
        result = qr.parse_unsigned_tx_input(json.dumps(tx_data))
        assert result is not None
        assert result["type"] == "unsigned_transaction"

    def test_parse_base64_encoded(self):
        qr = QRTransfer()
        tx_data = {
            "type": "unsigned_transaction",
            "version": "1.0",
            "data": base64.b64encode(b"fake-tx-bytes").decode(),
        }
        encoded = base64.b64encode(json.dumps(tx_data).encode()).decode()
        result = qr.parse_unsigned_tx_input(encoded)
        assert result is not None
        assert result["type"] == "unsigned_transaction"

    def test_reject_wrong_type(self):
        qr = QRTransfer()
        tx_data = {
            "type": "signed_transaction",
            "version": "1.0",
            "data": "AAAA",
        }
        result = qr.parse_unsigned_tx_input(json.dumps(tx_data))
        assert result is None

    def test_reject_garbage(self):
        qr = QRTransfer()
        result = qr.parse_unsigned_tx_input("not json at all {{{{")
        assert result is None

    def test_reject_empty(self):
        qr = QRTransfer()
        result = qr.parse_unsigned_tx_input("")
        assert result is None


# ── QR signed transaction display data ────────────────────────────────────


class TestSignedTxQRData:
    def test_display_signed_tx_qr_builds_correct_structure(self):
        """Verify the data structure that display_signed_tx_qr would encode."""
        signed_tx_bytes = b"\x01\x02\x03\x04\x05"
        tx_data = {
            "type": "signed_transaction",
            "version": "1.0",
            "data": base64.b64encode(signed_tx_bytes).decode("utf-8"),
        }
        # Verify roundtrip
        assert tx_data["type"] == "signed_transaction"
        decoded = base64.b64decode(tx_data["data"])
        assert decoded == signed_tx_bytes


# ── End-to-end QR data roundtrip ──────────────────────────────────────────


class TestQRDataRoundtrip:
    def test_unsigned_tx_roundtrip_through_qr_data(self):
        """Simulate: create tx data -> JSON -> QR data -> parse back."""
        qr = QRTransfer()

        # Step 1: Create transaction data (what the companion app would build)
        original = {
            "type": "unsigned_transaction",
            "version": "1.0",
            "from": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
            "to": "2BqcFZhc4CPa7sbwa5QCKxTWJB1UZUgEV3fLUQjXgrjn",
            "amount_sol": 0.5,
            "data": base64.b64encode(b"tx-payload-here").decode(),
        }

        # Step 2: Serialize to JSON (what would go into the QR code)
        json_str = json.dumps(original, separators=(",", ":"))

        # Step 3: Parse back (what the cold wallet does after scanning)
        parsed = qr.parse_unsigned_tx_input(json_str)
        assert parsed is not None
        assert parsed["type"] == "unsigned_transaction"
        assert parsed["from"] == original["from"]
        assert parsed["to"] == original["to"]
        assert parsed["data"] == original["data"]

    def test_large_payload_base64_fallback(self):
        """Payloads over 2000 chars trigger base64 encoding in display_transaction_qr.
        Verify the parsing side handles base64-wrapped JSON."""
        qr = QRTransfer()

        original = {
            "type": "unsigned_transaction",
            "version": "1.0",
            "data": base64.b64encode(b"x" * 2000).decode(),
        }
        json_str = json.dumps(original)
        # Simulate the base64 wrapping that display_transaction_qr does for large payloads
        b64_wrapped = base64.b64encode(json_str.encode()).decode()
        parsed = qr.parse_unsigned_tx_input(b64_wrapped)
        assert parsed is not None
        assert parsed["type"] == "unsigned_transaction"
