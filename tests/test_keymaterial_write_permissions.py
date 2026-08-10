"""
Every file Coldstar writes that contains key material must land at 0o600 and
must never leave a temp file behind.

These are regression tests for a bug class, not for individual functions: each
of these call sites independently used open()+chmod (or, for the paper wallet,
open() with no chmod at all), which leaves the secret readable at the umask
default until the chmod runs and truncates any existing file before the new
bytes land.
"""

import os
import secrets
import stat
from pathlib import Path
from unittest.mock import patch

import pytest
from solders.keypair import Keypair

import src.backup as backup_module
from src.backup import WalletBackup
from src.secure_io import TEMP_MARKER


def make_password() -> str:
    """
    Build a throwaway password at runtime.

    Deliberately not a literal: the repo's pre-commit credential scanner blocks
    password-shaped strings in source, and it is right to. The prefix supplies
    the upper/lower/digit/symbol classes the strength validator wants.
    """
    return "Aa1!" + secrets.token_urlsafe(16)


def mode_of(path):
    return stat.S_IMODE(os.stat(path).st_mode)


def assert_no_temp_files(directory: Path):
    leftovers = [p.name for p in Path(directory).iterdir() if TEMP_MARKER in p.name]
    assert not leftovers, f"interrupted-write temp files left behind: {leftovers}"


class FakeQRImage:
    """qrcode.make() stand-in — the real one needs PIL, which is optional."""

    def save(self, buffer, format=None):
        buffer.write(b"\x89PNG\r\n\x1a\n fake")


# ---------------------------------------------------------------------------
# backup_to_file
# ---------------------------------------------------------------------------


def test_encrypted_backup_is_owner_only(tmp_path):
    target = tmp_path / "backup.json"
    assert WalletBackup().backup_to_file(Keypair(), str(target), password=make_password())

    assert mode_of(target) == 0o600
    assert_no_temp_files(tmp_path)


def test_unencrypted_backup_is_also_owner_only(tmp_path):
    """
    The plaintext fallback stores raw key bytes. It is discouraged, but if it
    runs at all it must not also be world-readable.
    """
    target = tmp_path / "backup.json"
    assert WalletBackup().backup_to_file(Keypair(), str(target), password=None)

    assert mode_of(target) == 0o600
    assert_no_temp_files(tmp_path)


def test_backup_overwrite_tightens_a_loose_existing_file(tmp_path):
    """A backup written by an older, pre-fix build must be tightened."""
    target = tmp_path / "backup.json"
    target.write_text("{}")
    os.chmod(target, 0o644)

    assert WalletBackup().backup_to_file(Keypair(), str(target), password=make_password())
    assert mode_of(target) == 0o600


# ---------------------------------------------------------------------------
# create_paper_wallet
# ---------------------------------------------------------------------------


def test_paper_wallet_is_owner_only(tmp_path):
    """
    The paper wallet HTML holds the private key in the clear, ready to print.
    It previously had no chmod at all.
    """
    with patch.object(backup_module, "qrcode", create=True) as qr:
        qr.make.return_value = FakeQRImage()
        path = WalletBackup().create_paper_wallet(Keypair(), output_dir=str(tmp_path))

    assert path, "paper wallet was not created"
    assert mode_of(path) == 0o600
    assert_no_temp_files(tmp_path)


# ---------------------------------------------------------------------------
# EVM keystore
# ---------------------------------------------------------------------------


def test_evm_keystore_is_owner_only(tmp_path):
    pytest.importorskip("eth_account", reason="EVM support is optional")
    from src.evm_wallet import EVMWalletManager

    manager = EVMWalletManager(str(tmp_path))
    manager.set_wallet_directory(str(tmp_path))
    manager.generate_keypair()

    with patch("src.evm_wallet.get_password_input", return_value=make_password()):
        assert manager.save_keypair()

    keystore = tmp_path / "evm_keypair.json"
    address = tmp_path / "evm_address.txt"

    assert mode_of(keystore) == 0o600, "EVM keystore must be owner-only"
    assert mode_of(address) == 0o644, "the address is public, not secret"
    assert_no_temp_files(tmp_path)
