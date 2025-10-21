# Researcher Specification: Structured Logging

*Author: Gemini 2.5 Pro (Researcher)*  
*Date: 20
25-10-18*  
*Status: PROPOSAL*

---

## 1. Schema Definition

Based on the Guardian's requirement for "structured JSON logging with correlation IDs," the following schema is proposed for all log events within the `cmc_service`.

```json
{
    "event": "snapshot.create.start",
    "level": "info",
    "timestamp": "2025-10-18T12:00:00.123456Z",
    "service": "cmc_service",
    "correlation_id": "corr-id-xyz-123",

    "snapshot_id": "snap-abc-456",
    "atom_count": 150,
    "note": "User-provided note",
    
    "error": "Optional error message if level=error",
    "exception": "Optional exception details if level=error"
}
```

### Key Fields:
- **`event` (str):** A dot-separated, machine-readable event name (e.g., `atom.create`, `snapshot.replay.end`, `journal.corruption.quarantined`).
- **`level` (str):** Log level (`debug`, `info`, `warn`, `error`).
- **`timestamp` (str):** ISO 8601 UTC timestamp.
- **`service` (str):** The service name (`cmc_service`).
- **`correlation_id` (str):** A unique ID passed into a request to trace its entire lifecycle.
- **Context-specific fields:** Any other relevant key-value pairs (e.g., `atom_id`, `tag_count`).
- **`error` / `exception`:** Fields reserved for error-level logs.

This schema is compatible with `structlog` and tools like Datadog, Splunk, or the ELK stack for easy parsing and analysis.

---

## 2. Test Case Specification

The following test case should be implemented by the Builder (GPT-5 Codex) to validate the logging implementation. This test will fail until the `structlog` integration is complete.

**File:** `packages/cmc_service/tests/test_observability.py` (new file)

```python
import json
import logging
from io import StringIO

import pytest
from cmc_service.memory_store import MemoryStore
from cmc_service.models import AtomContent, AtomCreate

# This is a placeholder for the actual logger configuration
# The builder will need to implement this.
def configure_test_logger() -> StringIO:
    """Configures structlog to output JSON to an in-memory buffer for testing."""
    # ... implementation details for structlog ...
    log_buffer = StringIO()
    # logging.basicConfig(stream=log_buffer, level=logging.INFO, format='%(message)s')
    return log_buffer

@pytest.mark.skip(reason="TDD: Logging not yet implemented")
def test_create_atom_emits_structured_log(tmp_path):
    """
    Validates that creating an atom emits a structured JSON log.
    """
    log_buffer = configure_test_logger()
    
    store = MemoryStore(tmp_path / "cmc")
    store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Hello logged world"),
            tags={"log-test": 1.0},
        )
    )
    store.close()

    log_output = log_buffer.getvalue()
    assert log_output, "Logger did not capture any output"
    
    log_json = json.loads(log_output)
    
    assert log_json["event"] == "atom.create.complete"
    assert log_json["level"] == "info"
    assert log_json["service"] == "cmc_service"
    assert "atom_id" in log_json
    assert log_json["modality"] == "text"
    assert "content_hash" in log_json
```

---

## 3. Rationale

By defining the schema and test case upfront, we ensure:
- **Consistency:** All logs will follow the same structure.
- **Clarity:** The Builder has a clear, testable target for implementation.
- **Validation:** We can objectively verify that the implementation meets the architectural requirements.

This specification is now ready for the Builder.
