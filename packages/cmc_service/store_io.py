from __future__ import annotations

import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Mapping


class JournalCorruptionError(RuntimeError):
    """Raised when a journal fails integrity checks."""


_LOCK_LENGTH = 0x7FFFFFFF


class Journal:
    """Length-prefixed JSON journal with integrity checks."""

    def __init__(self, path: os.PathLike[str] | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("ab+")
        self._fh.seek(0, io.SEEK_END)
        self._lock_acquired = False
        self._acquire_lock()

    # ------------------------------------------------------------------
    def append(self, record: Mapping[str, object]) -> None:
        payload = json.dumps(record, separators=(",", ":"), sort_keys=True).encode("utf-8")
        length = len(payload)
        checksum = _crc32(payload)
        frame = length.to_bytes(4, "big") + checksum.to_bytes(4, "big") + payload
        self._fh.write(frame)
        self._fh.flush()
        try:
            os.fsync(self._fh.fileno())
        except OSError:
            # Best effort; ignore if fsync unsupported
            pass

    # ------------------------------------------------------------------
    def iter_records(self) -> Iterator[Mapping[str, object]]:
        self._fh.seek(0)
        while True:
            header = self._fh.read(8)
            if not header:
                break
            if len(header) != 8:
                raise JournalCorruptionError("Truncated journal header")
            length = int.from_bytes(header[:4], "big")
            checksum = int.from_bytes(header[4:], "big")
            payload = self._fh.read(length)
            if len(payload) != length:
                raise JournalCorruptionError("Truncated journal payload")
            if _crc32(payload) != checksum:
                raise JournalCorruptionError("Checksum mismatch in journal")
            yield json.loads(payload.decode("utf-8"))

    # ------------------------------------------------------------------
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    def close(self) -> None:
        if getattr(self, "_fh", None) is None:
            return
        if self._fh.closed:
            return
        try:
            self._release_lock()
        finally:
            self._fh.close()

    # ------------------------------------------------------------------
    def _acquire_lock(self) -> None:
        if self._lock_acquired:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, _LOCK_LENGTH)
            else:
                import fcntl

                fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:  # pragma: no cover - platform specific
            raise RuntimeError(f"Unable to acquire exclusive lock for journal {self.path}") from exc
        else:
            self._lock_acquired = True
            self._fh.seek(0, io.SEEK_END)

    # ------------------------------------------------------------------
    def _release_lock(self) -> None:
        if not self._lock_acquired:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, _LOCK_LENGTH)
            else:
                import fcntl

                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        finally:
            self._lock_acquired = False

    # ------------------------------------------------------------------
    def __del__(self) -> None:  # pragma: no cover - best effort cleanup
        try:
            self.close()
        except Exception:
            pass


def _crc32(data: bytes) -> int:
    from zlib import crc32

    return crc32(data) & 0xFFFFFFFF
