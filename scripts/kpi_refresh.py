"""Refresh KPI metrics by appending history entries and emitting trend CSVs."""
from __future__ import annotations

import argparse
import csv
import json
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

DEFAULT_METRICS_PATH = Path('goals/KPI_METRICS.json')
DEFAULT_OUTPUT_DIR = Path('goals/kpi_trends')


def _load_metrics(path: Path) -> Tuple[OrderedDict[str, Any], Dict[str, List[Dict[str, Any]]]]:
    data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=OrderedDict)
    history = data.get('history') or {}
    if not isinstance(history, dict):
        history = {}
    return data, history


def _append_history(
    history: Dict[str, List[Dict[str, Any]]],
    data: Dict[str, Any],
    timestamp: str,
    include_keys: Iterable[str] | None,
) -> None:
    include_set = {key for key in (include_keys or []) if key in data}
    for key, value in data.items():
        if key in {'history', 'history_metadata'}:
            continue
        if include_set and key not in include_set:
            continue
        history.setdefault(key, []).append({'timestamp': timestamp, 'value': value})


def _emit_csv(history: Dict[str, List[Dict[str, Any]]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for metric, entries in history.items():
        if not entries:
            continue
        csv_path = output_dir / f'{metric}.csv'
        with csv_path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.writer(handle)
            writer.writerow(['timestamp', 'value'])
            for entry in entries:
                writer.writerow([entry.get('timestamp', ''), entry.get('value', '')])


def refresh_kpis(
    *,
    metrics_path: Path = DEFAULT_METRICS_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    include_keys: Iterable[str] | None = None,
) -> None:
    metrics_path = metrics_path.resolve()
    output_dir = output_dir.resolve()
    data, history = _load_metrics(metrics_path)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    _append_history(history, data, timestamp, include_keys)
    data['history'] = history
    data['history_metadata'] = {
        'generated_at': timestamp,
        'notes': 'Updated via kpi_refresh script.',
    }
    metrics_path.write_text(json.dumps(data, indent=2) + "\n", encoding='utf-8')
    _emit_csv(history, output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metrics-path', default=str(DEFAULT_METRICS_PATH), help='Path to KPI_METRICS.json')
    parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR), help='Directory for trend CSVs')
    parser.add_argument('--include', nargs='*', default=None, help='Optional subset of keys to refresh')
    args = parser.parse_args()
    refresh_kpis(
        metrics_path=Path(args.metrics_path),
        output_dir=Path(args.output_dir),
        include_keys=args.include,
    )


if __name__ == '__main__':
    main()
