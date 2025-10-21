from __future__ import annotations

import json
import os
import uuid
from datetime import timezone
from pathlib import Path
from typing import Optional

import typer

from .logging_utils import configure_logging, render_metrics
from .memory_store import MemoryStore
from .models import AtomContent, AtomCreate

app = typer.Typer(help="CMC Service CLI (Phase 1)")


def _setup_logging() -> None:
    configure_logging()


def _get_store(base: Path) -> MemoryStore:
    _setup_logging()
    return MemoryStore(base)


def _resolve_correlation_id(correlation_id: Optional[str]) -> str:
    return correlation_id or str(uuid.uuid4())


@app.command("atoms:create")
def atoms_create(
    file: Path = typer.Option(..., exists=True, readable=True, help="Path to text payload"),
    modality: str = typer.Option("text", help="Payload modality"),
    tag: Optional[str] = typer.Option(None, help="Tag in key:value form"),
    base_path: Path = typer.Option(Path("./packages/cmc_service/data"), help="Data directory"),
    correlation_id: Optional[str] = typer.Option(None, help="Correlation identifier for logging"),
) -> None:
    corr_id = _resolve_correlation_id(correlation_id)
    store = _get_store(base_path)
    content = file.read_text(encoding="utf-8")
    tags = {}
    if tag:
        key, value = tag.split(":", 1)
        tags[key] = 1.0 if not value else float(value)
    atom = store.create_atom(
        AtomCreate(
            modality=modality,
            content=AtomContent(inline=content, media_type="text/plain"),
            tags=tags,
        ),
        correlation_id=corr_id,
    )
    typer.echo(json.dumps(atom.to_record(), indent=2))


@app.command("atoms:list")
def atoms_list(
    tag: Optional[str] = typer.Option(None, help="Filter by tag key"),
    limit: int = typer.Option(10, help="Maximum records"),
    base_path: Path = typer.Option(Path("./packages/cmc_service/data")),
    correlation_id: Optional[str] = typer.Option(None, help="Correlation identifier for logging"),
) -> None:
    corr_id = _resolve_correlation_id(correlation_id)
    store = _get_store(base_path)
    atoms = store.list_atoms(tag=tag, limit=limit, correlation_id=corr_id)
    typer.echo(json.dumps([a.to_record() for a in atoms], indent=2))


@app.command("snapshots:create")
def snapshots_create(
    note: Optional[str] = typer.Option(None, help="Snapshot note"),
    base_path: Path = typer.Option(Path("./packages/cmc_service/data")),
    correlation_id: Optional[str] = typer.Option(None, help="Correlation identifier for logging"),
) -> None:
    corr_id = _resolve_correlation_id(correlation_id)
    store = _get_store(base_path)
    snapshot = store.create_snapshot(note=note, correlation_id=corr_id)
    typer.echo(json.dumps(snapshot.to_record(), indent=2))


@app.command("snapshots:replay")
def snapshots_replay(
    snapshot_id: str = typer.Argument(..., help="Snapshot identifier"),
    base_path: Path = typer.Option(Path("./packages/cmc_service/data")),
    correlation_id: Optional[str] = typer.Option(None, help="Correlation identifier for logging"),
) -> None:
    corr_id = _resolve_correlation_id(correlation_id)
    store = _get_store(base_path)
    atoms = list(store.replay_snapshot(snapshot_id, correlation_id=corr_id))
    typer.echo(json.dumps([a.to_record() for a in atoms], indent=2))


@app.command("hhni:build")
def hhni_build(
    file: Path = typer.Option(..., exists=True, readable=True, help="Path to text payload"),
    modality: str = typer.Option("text", help="Payload modality"),
    tag: Optional[str] = typer.Option(None, help="Tag in key:value form (use priority:0.6 to trigger)"),
    force: bool = typer.Option(False, help="Force HHNI build regardless of priority"),
    base_path: Path = typer.Option(Path("./packages/cmc_service/data"), help="Data directory"),
    correlation_id: Optional[str] = typer.Option(None, help="Correlation identifier for logging"),
) -> None:
    """Create an atom and build HHNI nodes (Document → Paragraph → Sentence)."""
    corr_id = _resolve_correlation_id(correlation_id)
    store = _get_store(base_path)
    content = file.read_text(encoding="utf-8")
    tags = {}
    if tag:
        key, value = tag.split(":", 1)
        tags[key] = 1.0 if not value else float(value)
    atom, nodes = store.create_atom_with_hhni(
        AtomCreate(
            modality=modality,
            content=AtomContent(inline=content, media_type="text/plain"),
            tags=tags,
        ),
        build_hhni=force,
        correlation_id=corr_id,
    )
    typer.echo(json.dumps({"atom": atom.to_record(), "nodes": nodes}, indent=2))


@app.command("status")
def status(
    base_path: Path = typer.Option(Path("./packages/cmc_service/data")),
    backend: Optional[str] = typer.Option(None, help="Override backend (sqlite/jsonl) for this call"),
) -> None:
    if backend:
        os.environ["CMC_BACKEND"] = backend
    store = _get_store(base_path)
    summary = store.status_summary()
    integrity = store.journal_integrity() if summary.get("backend") == "jsonl" else {"atoms_log_ok": True, "snapshots_log_ok": True}

    payload = {
        "backend": summary.get("backend"),
        "atom_count": summary["atom_count"],
        "snapshot_count": summary.get("snapshot_count"),
        "latest_snapshot": {
            "id": summary["latest_snapshot_id"],
            "created_at": summary["latest_snapshot_time"],
        },
        "counters": summary["counters"],
        "snapshot_duration_ms": summary["snapshot_duration_ms"],
        "journal_intact": integrity,
    }
    typer.echo(json.dumps(payload, indent=2))
    if backend:
        del os.environ["CMC_BACKEND"]


@app.command("hhni:query")
def hhni_query(
    query_text: str = typer.Argument(..., help="Query text for semantic search"),
    level: int = typer.Option(2, help="HHNI level to query (1=doc, 2=paragraph, 3=sentence)"),
    limit: int = typer.Option(5, help="Max results"),
    base_path: Path = typer.Option(Path("./packages/cmc_service/data")),
    correlation_id: Optional[str] = typer.Option(None, help="Correlation identifier for logging"),
) -> None:
    """Query HHNI nodes by semantic similarity."""
    corr_id = _resolve_correlation_id(correlation_id)
    store = _get_store(base_path)
    
    try:
        dgraph_client, qdrant_client = store._get_hhni_clients()
        
        # Get embedding for query
        from hhni.embeddings import encode_text  # type: ignore
        query_vector = encode_text(query_text)
        
        # Choose collection based on level
        collection = "hhni_paragraphs" if level == 2 else "hhni_sentences"
        
        # Search Qdrant
        results = qdrant_client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=limit
        )
        
        # Format output
        formatted = []
        for hit in results:
            formatted.append({
                "score": hit.score,
                "atom_id": hit.payload.get("atom_id"),
                "level": hit.payload.get("level"),
                "index": hit.payload.get("paragraph") or hit.payload.get("sentence"),
            })
        
        typer.echo(json.dumps({"query": query_text, "results": formatted}, indent=2))
    except ImportError as e:
        typer.echo(f"Error: HHNI dependencies not available: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error querying HHNI: {e}", err=True)
        raise typer.Exit(1)


@app.command("hhni:stats")
def hhni_stats(
    base_path: Path = typer.Option(Path("./packages/cmc_service/data")),
) -> None:
    """Show HHNI indexing statistics."""
    store = _get_store(base_path)
    
    try:
        dgraph_client, qdrant_client = store._get_hhni_clients()
        
        # Get collection info from Qdrant
        para_collection = qdrant_client.get_collection("hhni_paragraphs")
        sent_collection = qdrant_client.get_collection("hhni_sentences")
        
        stats = {
            "paragraphs_indexed": para_collection.points_count,
            "sentences_indexed": sent_collection.points_count,
            "vector_dim": para_collection.config.params.vectors.size,
            "qdrant_url": os.environ.get("QDRANT_URL", "http://localhost:6333"),
            "dgraph_url": os.environ.get("DGRAPH_URL", "http://localhost:8080"),
        }
        
        typer.echo(json.dumps(stats, indent=2))
    except ImportError as e:
        typer.echo(f"Error: HHNI dependencies not available: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command("metrics:dump")
def metrics_dump() -> None:
    _setup_logging()
    typer.echo(render_metrics().decode("utf-8"))


def run() -> None:
    app()


if __name__ == "__main__":
    run()
