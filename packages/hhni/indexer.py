"""HHNI indexing helpers."""

from __future__ import annotations

import logging
from time import perf_counter, sleep
from typing import List, Optional

from .embeddings import embed_and_store
from .models import HHNINode, sha256_hex
from .parsers import parse_paragraphs, parse_sentences
from .safety import HHNISafetyGates

logger = logging.getLogger(__name__)

PARAGRAPH_COLLECTION = "hhni_paragraphs"
SENTENCE_COLLECTION = "hhni_sentences"
MAX_RETRIES = 3
BACKOFF_SECONDS = 0.5


def build_hhni_for_atom(
    *,
    atom,
    dgraph_client,
    qdrant_client,
    correlation_id: Optional[str] = None,
) -> List[HHNINode]:
    """Build HHNI nodes for the given atom."""
    HHNISafetyGates.validate_atom_pre_build(atom)

    start = perf_counter()
    nodes: List[HHNINode] = []
    extra_log = {
        "correlation_id": correlation_id,
        "atom_id": atom.id,
        "action": "hhni.build",
    }

    try:
        doc_node = HHNINode(
            id=f"doc:{atom.id}",
            level=1,
            path=f"/sys:aimos/doc:{atom.id}",
            content_hash=atom.hash,
            parent_id="sys:aimos",
            atom_refs=[atom.id],
            created_at=atom.created_at,
            snapshot_id=atom.witness.snapshot_id or "",
            tags=dict(atom.tags),
        )
        nodes.append(doc_node)

        content = atom.content.inline
        if content is None and atom.content.uri:
            raise ValueError("URI-based content not yet supported for HHNI")
        if not content:
            HHNISafetyGates.validate_node_count(nodes)
            dgraph_client.upsert_nodes([node.to_dict() for node in nodes])
            duration = perf_counter() - start
            logger.info(
                "hhni.build.success",
                extra={**extra_log, "node_count": len(nodes), "duration_ms": duration * 1000},
            )
            return nodes

        paragraphs = parse_paragraphs(content)
        for p_idx, para_text in enumerate(paragraphs):
            HHNISafetyGates.validate_text_length(para_text, text_type="paragraph")
            payload = {
                "atom_id": atom.id,
                "level": 2,
                "paragraph": p_idx,
            }
            vector_id = _embed_with_retry(
                para_text,
                qdrant_client=qdrant_client,
                collection=PARAGRAPH_COLLECTION,
                payload=payload,
            )
            para_node = HHNINode(
                id=f"para:{atom.id}#p{p_idx}",
                level=2,
                path=f"{doc_node.path}/para:{p_idx}",
                content_hash=sha256_hex(para_text),
                text=para_text,
                parent_id=doc_node.id,
                vector_id=vector_id,
                atom_refs=[atom.id],
                created_at=atom.created_at,
                snapshot_id=atom.witness.snapshot_id or "",
                tags=dict(atom.tags),
            )
            nodes.append(para_node)
            doc_node.children_ids.append(para_node.id)

            sentences = parse_sentences(para_text)
            for s_idx, sent_text in enumerate(sentences):
                HHNISafetyGates.validate_text_length(sent_text, text_type="sentence")
                payload = {
                    "atom_id": atom.id,
                    "level": 3,
                    "paragraph": p_idx,
                    "sentence": s_idx,
                }
                sent_vector_id = _embed_with_retry(
                    sent_text,
                    qdrant_client=qdrant_client,
                    collection=SENTENCE_COLLECTION,
                    payload=payload,
                )
                sent_node = HHNINode(
                    id=f"sent:{atom.id}#p{p_idx}#s{s_idx}",
                    level=3,
                    path=f"{para_node.path}/sent:{s_idx}",
                    content_hash=sha256_hex(sent_text),
                    text=sent_text,
                    parent_id=para_node.id,
                    vector_id=sent_vector_id,
                    atom_refs=[atom.id],
                    created_at=atom.created_at,
                    snapshot_id=atom.witness.snapshot_id or "",
                )
                nodes.append(sent_node)
                para_node.children_ids.append(sent_node.id)

        HHNISafetyGates.validate_node_count(nodes)
        dgraph_client.upsert_nodes([node.to_dict() for node in nodes])
        duration = perf_counter() - start
        logger.info(
            "hhni.build.success",
            extra={**extra_log, "node_count": len(nodes), "duration_ms": duration * 1000},
        )
        return nodes
    except Exception as exc:  # pragma: no cover - safety-critical logging
        duration = perf_counter() - start
        logger.error(
            "hhni.build.failed",
            extra={**extra_log, "error": str(exc), "duration_ms": duration * 1000},
        )
        raise


def _embed_with_retry(text: str, *, qdrant_client, collection: str, payload: dict) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return embed_and_store(
                text,
                qdrant_client=qdrant_client,
                collection=collection,
                payload=payload,
            )
        except Exception as exc:
            logger.warning(
                "hhni.embed.retry",
                extra={
                    "collection": collection,
                    "attempt": attempt,
                    "error": str(exc),
                },
            )
            if attempt == MAX_RETRIES:
                raise
            sleep(BACKOFF_SECONDS * attempt)
    raise RuntimeError("Unexpected embed retry exhaustion")
