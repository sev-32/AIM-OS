"""Embedding utilities for HHNI."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Iterable, List, Optional

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - optional dependency
    SentenceTransformer = None  # type: ignore

from .safety import HHNISafetyGates

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    if SentenceTransformer is None:
        raise RuntimeError("sentence-transformers package not installed. Install extras: hhni")
    logger.info("hhni.embedder.loaded", extra={"model": MODEL_NAME})
    return SentenceTransformer(MODEL_NAME)


def encode_texts(texts: List[str]) -> List[List[float]]:
    if len(texts) > HHNISafetyGates.MAX_EMBEDDING_BATCH:
        raise ValueError(
            f"Embedding batch too large: {len(texts)} > {HHNISafetyGates.MAX_EMBEDDING_BATCH}"
        )
    model = get_model()
    embeddings = model.encode(texts, batch_size=min(len(texts), 32), show_progress_bar=False)
    return embeddings.tolist()


def encode_text(text: str) -> List[float]:
    embeddings = encode_texts([text])
    return embeddings[0]


def store_embedding(
    vector: List[float],
    *,
    qdrant_client,
    collection: str,
    payload: Optional[dict] = None,
) -> str:
    from uuid import uuid4

    point_id = str(uuid4())
    try:
        qdrant_client.upsert(
            collection_name=collection,
            points=[
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": payload or {},
                }
            ],
        )
    except Exception as exc:  # pragma: no cover - network call
        logger.error(
            "hhni.embedding.store_failed",
            extra={"collection": collection, "error": str(exc)},
        )
        raise
    return point_id


def embed_and_store(
    text: str,
    *,
    qdrant_client,
    collection: str,
    payload: Optional[dict] = None,
) -> str:
    HHNISafetyGates.validate_text_length(text, text_type="text")
    vector = encode_text(text)
    return store_embedding(vector, qdrant_client=qdrant_client, collection=collection, payload=payload)


def embed_batch_and_store(
    texts: Iterable[str],
    *,
    qdrant_client,
    collection: str,
    payload_factory,
) -> List[str]:
    """Embed a batch of texts and store them in Qdrant."""
    text_list = list(texts)
    embeddings = encode_texts(text_list)
    point_ids = []
    for text, vector in zip(text_list, embeddings):
        payload = payload_factory(text)
        point_id = store_embedding(vector, qdrant_client=qdrant_client, collection=collection, payload=payload)
        point_ids.append(point_id)
    return point_ids
