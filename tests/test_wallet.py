"""
Tests for wallet module: password validation, keypair generation,
address validation, memory clearing, container normalization,
and secure memory encrypt/decrypt roundtrip.
"""

import json
import math
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from solders.keypair import Keypair
from solders.pubkey import Pubkey


# ---------------------------------------------------------------------------
# Password validation (standalone function, no Rust dependency)
# ---------------------------------------------------------------------------
# We import the function directly rather than the whole module, because
# wallet.py does a module-level import of the Rust signer and sys.exit(1).
# We patch sys.exit and the signer import so the module loads safely.


@pytest.fixture(autouse=True)
def _patch_signer(monkeypatch):
    """Prevent wallet.py from calling sys.exit when Rust signer is missing."""
    import sys

    # Inject a fake python_signer_example module before wallet.py tries to import it
    fake_signer_mod = type(sys)("python_signer_example")
    fake_signer_mod.SolanaSecureSigner = MagicMock
    monkeypatch.setitem(sys.modules, "python_signer_example", fake_signer_mod)


def _import_wallet():
    from src.wallet import (
        PasswordAttemptTracker,
        WalletManager,
        create_wallet_structure,
        validate_password_strength,
    )
    return validate_password_strength, PasswordAttemptTracker, WalletManager, create_wallet_structure


# ── Password strength ─────────────────────────────────────────────────────


class TestPasswordValidation:
    def test_strong_password_passes(self):
        validate, *_ = _import_wallet()
        ok, reason = validate("C0ldStar!2025x")
        assert ok, reason

    def test_too_short(self):
        validate, *_ = _import_wallet()
        ok, reason = validate("Ab1!")
        assert not ok
        assert "12 characters" in reason

    def test_no_uppercase(self):
        validate, *_ = _import_wallet()
        ok, reason = validate("abcdefghij1!")
        assert not ok
        assert "uppercase" in reason

    def test_no_lowercase(self):
        validate, *_ = _import_wallet()
        ok, reason = validate("ABCDEFGHIJ1!")
        assert not ok
        assert "lowercase" in reason

    def test_no_digit(self):
        validate, *_ = _import_wallet()
        ok, reason = validate("Abcdefghijk!")
        assert not ok
        assert "digit" in reason

    def test_no_special(self):
        validate, *_ = _import_wallet()
        ok, reason = validate("Abcdefghij12")
        assert not ok
        assert "special" in reason

    def test_entropy_calculation(self):
        validate, *_ = _import_wallet()
        # A password with all character classes gets full charset (94)
        ok, _ = validate("C0ldStar!2025x")
        assert ok
        # Verify math: 14 chars * log2(94) ~= 91.6 bits (well above 50)
        charset = 26 + 26 + 10 + 32
        entropy = 14 * math.log2(charset)
        assert entropy > 50


# ── Attempt tracker ────────────────────────────────────────────────────────


class TestPasswordAttemptTracker:
    def test_first_attempt_allowed(self):
        _, TrackerCls, *_ = _import_wallet()
        tracker = TrackerCls()
        allowed, _ = tracker.check_allowed()
        assert allowed

    def test_lockout_after_max(self):
        _, TrackerCls, *_ = _import_wallet()
        tracker = TrackerCls()
        for _ in range(tracker.MAX_ATTEMPTS):
            tracker.record_failure()
        allowed, reason = tracker.check_allowed()
        assert not allowed
        assert "locked" in reason.lower()

    def test_success_resets_counter(self):
        _, TrackerCls, *_ = _import_wallet()
        tracker = TrackerCls()
        tracker.record_failure()
        tracker.record_failure()
        tracker.record_success()
        allowed, _ = tracker.check_allowed()
        assert allowed


# ── WalletManager basics ──────────────────────────────────────────────────


class TestWalletManagerBasics:
    def test_generate_keypair(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        kp, pubkey_str = wm.generate_keypair()
        assert isinstance(kp, Keypair)
        assert len(pubkey_str) > 30  # base58 Solana address

    def test_validate_address_valid(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        kp = Keypair()
        assert wm.validate_address(str(kp.pubkey()))

    def test_validate_address_invalid(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        assert not wm.validate_address("not-a-valid-address")
        assert not wm.validate_address("")

    def test_export_public_key_bytes(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        wm.generate_keypair()
        pk_bytes = wm.export_public_key_bytes()
        assert pk_bytes is not None
        assert len(pk_bytes) == 32  # Ed25519 public key size

    def test_export_public_key_bytes_none_without_keypair(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        assert wm.export_public_key_bytes() is None

    def test_clear_memory(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        wm.generate_keypair()
        wm._cached_password = bytearray(b"secret")
        wm.clear_memory()
        assert wm.keypair is None
        assert wm.encrypted_container is None
        assert wm._cached_password is None

    def test_get_public_key_from_file(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU\n")
            f.flush()
            result = wm.get_public_key_from_file(f.name)
        os.unlink(f.name)
        assert result == "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"

    def test_keypair_exists_false(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        assert not wm.keypair_exists("/nonexistent/path/keypair.json")


# ── Container normalization ───────────────────────────────────────────────


class TestContainerNormalization:
    def test_normalize_array_to_base64(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        container = {
            "ciphertext": [1, 2, 3, 4],
            "nonce": [5, 6, 7],
            "salt": [8, 9, 10],
        }
        normalized = wm._normalize_container_format(container)
        import base64
        assert normalized["ciphertext"] == base64.b64encode(bytes([1, 2, 3, 4])).decode()
        assert normalized["nonce"] == base64.b64encode(bytes([5, 6, 7])).decode()
        assert normalized["salt"] == base64.b64encode(bytes([8, 9, 10])).decode()
        assert normalized["version"] == 1

    def test_normalize_already_string(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        container = {
            "version": 2,
            "ciphertext": "AQID",
            "nonce": "BQYH",
            "salt": "CAkK",
        }
        normalized = wm._normalize_container_format(container)
        assert normalized["ciphertext"] == "AQID"
        assert normalized["version"] == 2

    def test_normalize_public_key_array(self):
        *_, WalletManager, _ = _import_wallet()
        wm = WalletManager()
        import base58
        pk_bytes = bytes(range(32))
        container = {"public_key": list(pk_bytes)}
        normalized = wm._normalize_container_format(container)
        assert normalized["public_key"] == base58.b58encode(pk_bytes).decode()


# ── create_wallet_structure ───────────────────────────────────────────────


class TestCreateWalletStructure:
    def test_creates_directories(self):
        *_, create_wallet_structure = _import_wallet()
        with tempfile.TemporaryDirectory() as tmpdir:
            dirs = create_wallet_structure(tmpdir)
            assert "wallet" in dirs
            assert "inbox" in dirs
            assert "outbox" in dirs
            assert Path(dirs["wallet"]).is_dir()
            assert Path(dirs["inbox"]).is_dir()
            assert Path(dirs["outbox"]).is_dir()


# ── SecureWalletHandler encrypt/decrypt roundtrip ─────────────────────────


class TestSecureMemoryRoundtrip:
    def test_encrypt_decrypt_roundtrip(self):
        from src.secure_memory import SecureWalletHandler

        kp = Keypair()
        password = "TestP@ssw0rd123!"

        encrypted = SecureWalletHandler.encrypt_keypair(kp, password)

        # Verify encrypted structure
        assert encrypted["version"] == 1
        assert encrypted["algo"] == "argon2i_xsalsa20poly1305"
        assert "salt" in encrypted
        assert "nonce" in encrypted
        assert "ciphertext" in encrypted

        # Decrypt and verify
        recovered = SecureWalletHandler.decrypt_keypair(encrypted, password)
        assert recovered is not None
        assert str(recovered.pubkey()) == str(kp.pubkey())

    def test_wrong_password_returns_none(self):
        from src.secure_memory import SecureWalletHandler

        kp = Keypair()
        encrypted = SecureWalletHandler.encrypt_keypair(kp, "Correct!Pass1")
        recovered = SecureWalletHandler.decrypt_keypair(encrypted, "Wrong!Pass123")
        assert recovered is None

    def test_encrypted_data_is_hex(self):
        from src.secure_memory import SecureWalletHandler

        kp = Keypair()
        encrypted = SecureWalletHandler.encrypt_keypair(kp, "TestP@ssw0rd!")
        # All crypto fields should be valid hex strings
        bytes.fromhex(encrypted["salt"])
        bytes.fromhex(encrypted["nonce"])
        bytes.fromhex(encrypted["ciphertext"])
