import json
import logging
import sys
from datetime import datetime, timezone
from typing import Optional, TextIO

from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest

DEFAULT_BUCKETS = (
    0.001,
    0.005,
    0.01,
    0.05,
    0.1,
    0.5,
    1.0,
    2.5,
    5.0,
)

DEFAULT_REGISTRY: CollectorRegistry
SNAPSHOT_DURATION: Histogram
WRITE_ERRORS_TOTAL: Counter
ATOMS_CREATED_TOTAL: Counter
SNAPSHOTS_CREATED_TOTAL: Counter


def _init_metrics(registry: Optional[CollectorRegistry] = None) -> None:
    global DEFAULT_REGISTRY, SNAPSHOT_DURATION, WRITE_ERRORS_TOTAL, ATOMS_CREATED_TOTAL, SNAPSHOTS_CREATED_TOTAL

    DEFAULT_REGISTRY = registry or CollectorRegistry()
    SNAPSHOT_DURATION = Histogram(
        "cmc_snapshot_duration_seconds",
        "Duration of snapshot creation",
        buckets=DEFAULT_BUCKETS,
        registry=DEFAULT_REGISTRY,
    )
    WRITE_ERRORS_TOTAL = Counter(
        "cmc_write_errors_total",
        "Total write errors",
        registry=DEFAULT_REGISTRY,
    )
    ATOMS_CREATED_TOTAL = Counter(
        "cmc_atoms_created_total",
        "Atoms created by modality",
        ["modality"],
        registry=DEFAULT_REGISTRY,
    )
    SNAPSHOTS_CREATED_TOTAL = Counter(
        "cmc_snapshots_created_total",
        "Total snapshots created",
        registry=DEFAULT_REGISTRY,
    )


_init_metrics()


class JsonFormatter(logging.Formatter):
    """Formatter that emits JSON payloads for log records."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {}
        extra: dict = getattr(record, "json", {}) or {}

        ts = extra.pop("ts", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
        payload["ts"] = ts
        payload["level"] = record.levelname.lower()
        payload["action"] = extra.pop("action", record.getMessage())
        payload["message"] = record.getMessage()
        payload.update(extra)

        if record.exc_info:
            payload.setdefault("error", self.formatException(record.exc_info))

        return json.dumps(payload)


def configure_logging(*, stream: Optional[TextIO] = None, level: int = logging.INFO) -> None:
    """Configure the cmc_service logger with JSON output."""
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("cmc_service")
    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    # Ensure child loggers inherit configuration
    for name in list(logging.root.manager.loggerDict.keys()):
        if name.startswith("cmc_service."):
            logging.getLogger(name).handlers.clear()
            logging.getLogger(name).propagate = True


def render_metrics() -> bytes:
    return generate_latest(DEFAULT_REGISTRY)


def reset_metrics() -> None:
    """Recreate metrics on a fresh registry for deterministic tests."""
    _init_metrics()


__all__ = [
    "configure_logging",
    "JsonFormatter",
    "render_metrics",
    "reset_metrics",
    "DEFAULT_REGISTRY",
    "SNAPSHOT_DURATION",
    "WRITE_ERRORS_TOTAL",
    "ATOMS_CREATED_TOTAL",
    "SNAPSHOTS_CREATED_TOTAL",
]
