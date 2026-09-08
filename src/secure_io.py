"""
Crash-safe, permission-safe writes for secret material.

Python counterpart to the Rust `coldstar_config::secure_io` module. The two
share a temp-file naming convention deliberately: a wallet directory can be
written by the Python tool and later opened by the Rust CLI (or the reverse),
so each must be able to recognise an interrupted write left by the other.

Three defects this closes, none of which a plain ``open(path, 'w')`` can avoid:

1. Truncate-in-place. ``open(path, 'w')`` destroys the previous contents before
   the new bytes land. A crash, a power loss, or a USB volume pulled mid-write
   leaves a zero-length or partial keystore and no way back. We write to a
   sibling temp file and ``os.replace()`` it into position, which is atomic.

2. The chmod-after-write window. Calling ``os.chmod(path, 0o600)`` *after*
   writing leaves the secret readable at the umask default (commonly 0o644)
   for the duration of the write. We pass the mode to ``os.open()`` instead, so
   the file never exists at looser permissions.

3. Unflushed data. ``os.replace`` orders metadata, not file contents. We fsync
   the temp file before replacing and fsync the directory afterwards.

Orphan temp files are never deleted automatically — see ``find_orphan_temps``.
"""

import os
from pathlib import Path
from typing import List, Union

# Infix stamped into every in-flight temp file name. Kept identical to the Rust
# side's TEMP_MARKER so orphan scans interoperate.
TEMP_MARKER = ".cs-tmp."

# Owner read/write only — anything containing or protecting key material.
SECRET_MODE = 0o600

# Non-secret companions such as pubkey.txt.
PUBLIC_MODE = 0o644

# Distinguishes temp files created by concurrent writes in one process.
_counter = 0


def write_secret_atomic(path: Union[str, Path], data: Union[str, bytes]) -> None:
    """
    Atomically write secret material, never observable at wider than 0o600.

    On failure the temp file is removed: the caller still holds the plaintext,
    so there is nothing to recover.
    """
    _write_atomic(Path(path), data, SECRET_MODE)


def write_public_atomic(path: Union[str, Path], data: Union[str, bytes]) -> None:
    """
    Atomically write a non-secret file (public keys, manifests) at 0o644.

    Still atomic — a truncated pubkey.txt next to a valid keystore is its own
    kind of confusing failure.
    """
    _write_atomic(Path(path), data, PUBLIC_MODE)


def find_orphan_temps(directory: Union[str, Path]) -> List[Path]:
    """
    List interrupted writes in ``directory``, sorted for stable reporting.

    An orphan means a previous write died after its temp file was created but
    before the replace completed. It is NOT garbage: it may hold the only copy
    of a freshly generated key. Nothing here deletes one — callers surface them
    to the user and let the user reconcile against their seed phrase.

    A missing directory has no orphans and is not an error.
    """
    directory = Path(directory)
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.iterdir() if is_temp_path(p))


def orphan_temps_for(target: Union[str, Path]) -> List[Path]:
    """
    List interrupted writes belonging specifically to ``target``.

    ``target`` is the final path (e.g. .../keypair.json), not a temp path.
    """
    target = Path(target)
    prefix = target.name + TEMP_MARKER
    return [p for p in find_orphan_temps(target.parent) if p.name.startswith(prefix)]


def is_temp_path(path: Union[str, Path]) -> bool:
    """Whether ``path`` is one of this module's in-flight temp files."""
    return TEMP_MARKER in Path(path).name


def target_of_temp(temp: Union[str, Path]) -> Union[Path, None]:
    """
    Map a temp file back to the file it was being written to.

    ``keypair.json.cs-tmp.4812-0`` -> ``keypair.json``. Returns None for a path
    that does not carry the marker.
    """
    temp = Path(temp)
    stem = temp.name.split(TEMP_MARKER)[0]
    if not stem or stem == temp.name:
        return None
    return temp.with_name(stem)


def _write_atomic(path: Path, data: Union[str, bytes], mode: int) -> None:
    payload = data.encode("utf-8") if isinstance(data, str) else data

    directory = path.parent if str(path.parent) else Path(".")
    directory.mkdir(parents=True, exist_ok=True)

    # The temp file must be a sibling: os.replace is only atomic within one
    # filesystem, and the system temp dir is usually a different one — which
    # matters here, because wallets routinely live on a mounted USB volume
    # rather than the boot disk.
    fd, tmp_path = _create_temp_sibling(path, mode)

    try:
        # fdopen takes ownership of fd, so the with-block closes it exactly once.
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        _discard(tmp_path)
        raise

    _sync_dir(directory)


def _create_temp_sibling(path: Path, mode: int):
    """
    Create a uniquely named temp file next to ``path``, opened with ``mode``.

    Retries on collision rather than trusting the counter alone: two Coldstar
    processes can share a wallet directory on a removable volume.

    Returns (fd, temp_path). The caller owns the fd.
    """
    global _counter
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL

    last_error = None
    for _ in range(64):
        _counter += 1
        tmp_path = path.with_name(f"{path.name}{TEMP_MARKER}{os.getpid()}-{_counter}")
        try:
            fd = os.open(tmp_path, flags, mode)
            return (fd, tmp_path)
        except FileExistsError as exc:
            last_error = exc
            continue

    raise last_error or OSError("exhausted temp file name attempts")


def _discard(tmp_path: Path) -> None:
    try:
        os.unlink(tmp_path)
    except OSError:
        pass


def _sync_dir(directory: Path) -> None:
    """
    Durably record the rename itself.

    Best effort: a filesystem that refuses to fsync a directory (FAT on a USB
    stick, or any Windows volume) must not fail a write whose data is already
    on disk.
    """
    try:
        fd = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)
