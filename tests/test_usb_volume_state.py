"""
Tests for USBManager volume-availability detection.

The distinction under test is the one Path.exists() cannot make: a drive that
was ejected or has failed must not read as "a healthy drive with no wallet on
it", because the caller offers to create a new wallet in that case.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.usb import (
    VOLUME_UNAVAILABLE,
    WALLET_ABSENT,
    WALLET_PRESENT,
    USBManager,
)


@pytest.fixture
def manager():
    return USBManager()


def make_wallet(root: Path):
    wallet = root / "wallet"
    wallet.mkdir(parents=True, exist_ok=True)
    (wallet / "keypair.json").write_text('{"version":"2.0"}')
    (wallet / "pubkey.txt").write_text("11111111111111111111111111111111")
    return wallet


# ---------------------------------------------------------------------------
# volume_available
# ---------------------------------------------------------------------------


def test_healthy_mount_is_available(manager, tmp_path):
    assert manager.volume_available(str(tmp_path)) is True


def test_empty_but_healthy_mount_is_available(manager, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert manager.volume_available(str(empty)) is True


def test_missing_mount_is_unavailable(manager, tmp_path):
    assert manager.volume_available(str(tmp_path / "gone")) is False


def test_no_mount_point_is_unavailable(manager):
    assert manager.volume_available(None) is False


def test_io_error_is_unavailable(manager, tmp_path):
    """A failing disk raises EIO from scandir rather than reporting empty."""
    with patch("os.scandir", side_effect=OSError(5, "Input/output error")):
        assert manager.volume_available(str(tmp_path)) is False


# ---------------------------------------------------------------------------
# wallet_status
# ---------------------------------------------------------------------------


def test_wallet_present(manager, tmp_path):
    make_wallet(tmp_path)
    assert manager.wallet_status(str(tmp_path)) == WALLET_PRESENT


def test_wallet_absent_on_healthy_volume(manager, tmp_path):
    assert manager.wallet_status(str(tmp_path)) == WALLET_ABSENT


def test_ejected_volume_is_not_reported_as_absent(manager, tmp_path):
    """
    The regression this guards: an unplugged drive previously returned the same
    answer as an empty one, and the caller offered to create a wallet over it.
    """
    make_wallet(tmp_path)
    with patch("os.scandir", side_effect=OSError(19, "No such device")):
        assert manager.wallet_status(str(tmp_path)) == VOLUME_UNAVAILABLE


def test_volume_lost_between_probe_and_stat(manager, tmp_path):
    """scandir succeeds, then the drive vanishes before the keypair stat."""
    with patch.object(Path, "is_file", side_effect=OSError(5, "Input/output error")):
        assert manager.wallet_status(str(tmp_path)) == VOLUME_UNAVAILABLE


def test_wallet_dir_without_keypair_is_absent(manager, tmp_path):
    (tmp_path / "wallet").mkdir()
    assert manager.wallet_status(str(tmp_path)) == WALLET_ABSENT


# ---------------------------------------------------------------------------
# check_wallet_exists compatibility
# ---------------------------------------------------------------------------


def test_check_wallet_exists_true_when_present(manager, tmp_path):
    make_wallet(tmp_path)
    assert manager.check_wallet_exists(str(tmp_path)) is True


def test_check_wallet_exists_false_when_absent(manager, tmp_path):
    assert manager.check_wallet_exists(str(tmp_path)) is False


def test_check_wallet_exists_false_when_volume_gone(manager, tmp_path):
    make_wallet(tmp_path)
    with patch("os.scandir", side_effect=OSError(19, "No such device")):
        assert manager.check_wallet_exists(str(tmp_path)) is False


def test_manager_falls_back_to_its_own_mount_point(manager, tmp_path):
    make_wallet(tmp_path)
    manager.mount_point = str(tmp_path)
    assert manager.wallet_status() == WALLET_PRESENT
    assert manager.volume_available() is True
