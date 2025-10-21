import json
from io import StringIO
from pathlib import Path

from cmc_service.logging_utils import configure_logging, render_metrics, reset_metrics
from cmc_service.memory_store import MemoryStore
from cmc_service.models import AtomContent, AtomCreate


# goals: [KR-2.3, KR-3.1]
def test_snapshot_log_contains_correlation_id(tmp_path: Path) -> None:
    reset_metrics()
    buffer = StringIO()
    configure_logging(stream=buffer)

    store = MemoryStore(tmp_path / "cmc")
    correlation_id = "test-corr-id"

    store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="hello"),
        ),
        correlation_id=correlation_id,
    )
    store.create_snapshot(note="log-test", correlation_id=correlation_id)
    buffer.seek(0)

    log_lines = [json.loads(line) for line in buffer.getvalue().splitlines() if line.strip()]
    snapshot_logs = [line for line in log_lines if line.get("action") == "snapshot.create"]
    assert snapshot_logs, "Expected snapshot log entries"
    latest_log = snapshot_logs[-1]
    assert latest_log["correlation_id"] == correlation_id
    assert latest_log["note"] == "log-test"
    assert latest_log["snapshot_id"]


def test_metrics_endpoint_exposes_counters(tmp_path: Path) -> None:
    reset_metrics()
    configure_logging(stream=StringIO())
    store = MemoryStore(tmp_path / "cmc")
    store.create_atom(
        AtomCreate(modality="text", content=AtomContent(inline="payload")),
        correlation_id="mid",
    )
    store.create_snapshot(correlation_id="mid")

    metrics_text = render_metrics().decode("utf-8")
    assert "cmc_atoms_created_total" in metrics_text
    assert "cmc_snapshots_created_total" in metrics_text
    assert "cmc_snapshot_duration_seconds" in metrics_text
