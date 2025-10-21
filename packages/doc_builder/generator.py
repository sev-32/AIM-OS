from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


@dataclass
class DocumentBuildResult:
    output_path: Path
    word_count: int
    section_count: int
    generated_at: datetime


def _ensure_path(value: Path | str) -> Path:
    return Path(value).expanduser().resolve()


def generate_document(
    seed: Dict[str, Any] | Path | str,
    *,
    output_dir: Path | str | None = None,
    filename: Optional[str] = None,
) -> DocumentBuildResult:
    """Generate a Markdown document from a structured seed."""

    if isinstance(seed, (str, Path)):
        seed_path = _ensure_path(seed)
        payload = json.loads(seed_path.read_text(encoding="utf-8"))
    else:
        payload = dict(seed)
        seed_path = None

    title = str(payload.get("title", "Untitled Document")).strip() or "Untitled Document"
    summary = str(payload.get("summary", "")).strip()
    sections: Iterable[Dict[str, Any]] = payload.get("sections", []) or []

    generated_at = datetime.now(timezone.utc)
    out_dir = _ensure_path(output_dir) if output_dir else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    if filename:
        output_name = filename
    else:
        safe = title.lower().replace(" ", "-").replace("/", "-")
        output_name = f"{safe or 'document'}-build.md"
    output_path = out_dir / output_name

    lines: list[str] = [f"# {title}", ""]
    if summary:
        lines.extend([summary, ""])

    for section in sections:
        heading = str(section.get("heading", "")).strip()
        if heading:
            lines.append(f"## {heading}")
        body = section.get("body")
        if isinstance(body, str) and body.strip():
            lines.extend([body.strip(), ""])
        bullets = section.get("bullets")
        if isinstance(bullets, list) and bullets:
            for item in bullets:
                lines.append(f"- {item}")
            lines.append("")

    lines.append("## Provenance")
    lines.append(f"Generated at: {generated_at.isoformat().replace('+00:00', 'Z')}")
    lines.append(f"Seed file: {seed_path if seed_path else '<inline seed>'}")
    if "metadata" in payload:
        lines.append(f"Metadata: {json.dumps(payload['metadata'], indent=2)}")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")

    text = output_path.read_text(encoding="utf-8")
    words = [word for word in text.split() if word.strip()]
    section_count = sum(1 for line in lines if line.startswith("## "))

    return DocumentBuildResult(
        output_path=output_path,
        word_count=len(words),
        section_count=section_count,
        generated_at=generated_at,
    )
