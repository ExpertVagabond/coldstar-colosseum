"""
Tests for secure_io: atomic writes, permission tightening, and detection of
interrupted writes.

secure_io has no Rust-signer dependency, so it imports directly without the
patching dance the other wallet tests need.
"""

import os
import stat
from pathlib import Path

import pytest

from src.secure_io import (
    TEMP_MARKER,
    find_orphan_temps,
    is_temp_path,
    orphan_temps_for,
    target_of_temp,
    write_public_atomic,
    write_secret_atomic,
)


def mode_of(path):
    return stat.S_IMODE(os.stat(path).st_mode)


# ---------------------------------------------------------------------------
# Atomic write basics
# ---------------------------------------------------------------------------


def test_writes_contents_and_leaves_no_temp(tmp_path):
    p = tmp_path / "keypair.json"
    write_secret_atomic(p, '{"v":1}')
    assert p.read_text() == '{"v":1}'
    assert find_orphan_temps(tmp_path) == []


def test_accepts_bytes_and_str(tmp_path):
    write_secret_atomic(tmp_path / "a", b"bytes")
    write_secret_atomic(tmp_path / "b", "text")
    assert (tmp_path / "a").read_bytes() == b"bytes"
    assert (tmp_path / "b").read_text() == "text"


def test_creates_missing_parent_directories(tmp_path):
    p = tmp_path / "deep" / "nested" / "keypair.json"
    write_secret_atomic(p, "x")
    assert p.exists()


def test_overwrite_replaces_contents(tmp_path):
    p = tmp_path / "keypair.json"
    write_secret_atomic(p, "first")
    write_secret_atomic(p, "second-and-longer")
    assert p.read_text() == "second-and-longer"
    assert find_orphan_temps(tmp_path) == []


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


def test_secret_is_never_wider_than_600(tmp_path):
    p = tmp_path / "keypair.json"
    write_secret_atomic(p, "secret")
    assert mode_of(p) == 0o600


def test_public_companion_is_644(tmp_path):
    p = tmp_path / "pubkey.txt"
    write_public_atomic(p, "abc")
    assert mode_of(p) == 0o644


def test_overwriting_a_loose_file_tightens_permissions(tmp_path):
    """A keystore written by an older, pre-fix build must be tightened."""
    p = tmp_path / "keypair.json"
    p.write_text("old")
    os.chmod(p, 0o644)

    write_secret_atomic(p, "new")

    assert p.read_text() == "new"
    assert mode_of(p) == 0o600, "replace must install the tight mode, not inherit"


# ---------------------------------------------------------------------------
# Interrupted writes
# ---------------------------------------------------------------------------


def test_orphans_are_found_and_attributed_to_their_target(tmp_path):
    target = tmp_path / "keypair.json"
    write_secret_atomic(target, "live")

    # The exact artifact a crash between "temp created" and "replace done" leaves.
    orphan = tmp_path / f"keypair.json{TEMP_MARKER}999-0"
    orphan.write_text("partial")
    unrelated = tmp_path / f"backup.json{TEMP_MARKER}999-1"
    unrelated.write_text("other")

    assert len(find_orphan_temps(tmp_path)) == 2
    assert orphan_temps_for(target) == [orphan], "must not claim another file's temp"


def test_missing_directory_reports_no_orphans(tmp_path):
    assert find_orphan_temps(tmp_path / "nope") == []


def test_target_of_temp_roundtrip(tmp_path):
    target = tmp_path / "keypair.json"
    temp = tmp_path / f"keypair.json{TEMP_MARKER}1-2"

    assert target_of_temp(temp) == target
    assert target_of_temp(target) is None
    assert is_temp_path(temp)
    assert not is_temp_path(target)


def test_failed_write_leaves_original_intact_and_cleans_up(tmp_path):
    """
    A write that fails while the caller still holds the plaintext is not a
    recovery case — the temp must be removed and the original left alone.
    """
    p = tmp_path / "keypair.json"
    write_secret_atomic(p, "original")

    class Unserialisable:
        pass

    with pytest.raises(TypeError):
        write_secret_atomic(p, Unserialisable())

    assert p.read_text() == "original"
    assert find_orphan_temps(tmp_path) == []


def test_temp_marker_matches_the_rust_implementation():
    """
    The Rust CLI and the Python tool share wallet directories, so each must
    recognise an interrupted write left behind by the other.
    """
    rust = Path(
        "/Volumes/Virtual Server/projects/coldstar-rs/crates/coldstar-config/src/secure_io.rs"
    )
    if not rust.exists():
        pytest.skip("coldstar-rs checkout not present")
    assert f'TEMP_MARKER: &str = "{TEMP_MARKER}"' in rust.read_text()
