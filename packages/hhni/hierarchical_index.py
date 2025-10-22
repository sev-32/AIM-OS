"""Hierarchical Hypergraph Neural Index - Fractal Structure.

This module implements the multi-resolution index described in the HHNI
design notes. It provides a five-level hierarchy that allows callers to
zoom in (system → section → paragraph → sentence → sub-word) or zoom out
to retrieve the right amount of context for a given task.

The implementation intentionally keeps the first version simple and
deterministic: embeddings fall back to lightweight numeric features if
the full embedding model is unavailable. Future phases (DVNS physics,
advanced retrieval) can be layered on top of this foundation.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional

try:  # pragma: no cover - optional heavy dependency
    from .embeddings import encode_text
except Exception:  # pragma: no cover - handled by fallback
    encode_text = None  # type: ignore

from .parsers import normalize_newlines, parse_paragraphs, parse_sentences


class IndexLevel(Enum):
    """Granularity levels for nodes in the hierarchical index."""

    SYSTEM = 1  # Highest level - overview
    SECTION = 2  # Major divisions
    PARAGRAPH = 3  # Content blocks
    SENTENCE = 4  # Atomic facts
    SUBWORD = 5  # Token granularity


@dataclass
class IndexNode:
    """Node within the hierarchical HHNI structure."""

    id: str
    level: IndexLevel
    content: str
    summary: str
    parent_id: Optional[str]
    children_ids: List[str] = field(default_factory=list)
    embeddings: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class HierarchicalIndex:
    """Fractal index structure for multi-resolution retrieval."""

    def __init__(self) -> None:
        self.nodes: Dict[str, IndexNode] = {}
        self.root_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def index_document(
        self,
        content: str,
        doc_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Index a document at all five granularity levels."""
        text = (content or "").strip()
        if not text:
            raise ValueError("Document content must be non-empty")

        metadata = dict(metadata or {})
        metadata.setdefault("doc_id", doc_id)

        root_id = f"doc:{doc_id}"
        system_summary = _summarize_text(text)
        system_embeddings = _safe_embed(system_summary)
        system_node = IndexNode(
            id=root_id,
            level=IndexLevel.SYSTEM,
            content=text,
            summary=system_summary,
            parent_id=None,
            embeddings=system_embeddings,
            metadata=metadata,
        )
        self.nodes[root_id] = system_node
        self.root_id = root_id

        sections = _split_into_sections(text)
        if not sections:
            sections = [Section(title="Section 1", paragraphs=parse_paragraphs(text))]

        for sec_idx, section in enumerate(sections):
            section_id = f"sec:{doc_id}:{sec_idx}"
            section_summary = section.title or _summarize_text(" ".join(section.paragraphs))
            section_embeddings = _safe_embed(section_summary)
            section_metadata = {
                **metadata,
                "section_index": sec_idx,
                "section_title": section.title,
            }
            section_node = IndexNode(
                id=section_id,
                level=IndexLevel.SECTION,
                content="\n\n".join(section.paragraphs),
                summary=section_summary,
                parent_id=root_id,
                embeddings=section_embeddings,
                metadata=section_metadata,
            )
            self.nodes[section_id] = section_node
            system_node.children_ids.append(section_id)

            paragraphs = section.paragraphs or parse_paragraphs(section_node.content)
            for para_idx, paragraph_text in enumerate(paragraphs):
                paragraph_id = f"para:{doc_id}:{sec_idx}:{para_idx}"
                paragraph_summary = _summarize_text(paragraph_text)
                paragraph_embeddings = _safe_embed(paragraph_summary)
                paragraph_metadata = {
                    **section_metadata,
                    "paragraph_index": para_idx,
                }
                paragraph_node = IndexNode(
                    id=paragraph_id,
                    level=IndexLevel.PARAGRAPH,
                    content=paragraph_text,
                    summary=paragraph_summary,
                    parent_id=section_id,
                    embeddings=paragraph_embeddings,
                    metadata=paragraph_metadata,
                )
                self.nodes[paragraph_id] = paragraph_node
                section_node.children_ids.append(paragraph_id)

                sentences = parse_sentences(paragraph_text)
                for sent_idx, sentence_text in enumerate(sentences):
                    sentence_id = f"sent:{doc_id}:{sec_idx}:{para_idx}:{sent_idx}"
                    sentence_summary = sentence_text.strip()
                    sentence_embeddings = _safe_embed(sentence_summary)
                    sentence_metadata = {
                        **paragraph_metadata,
                        "sentence_index": sent_idx,
                    }
                    sentence_node = IndexNode(
                        id=sentence_id,
                        level=IndexLevel.SENTENCE,
                        content=sentence_text,
                        summary=sentence_summary,
                        parent_id=paragraph_id,
                        embeddings=sentence_embeddings,
                        metadata=sentence_metadata,
                    )
                    self.nodes[sentence_id] = sentence_node
                    paragraph_node.children_ids.append(sentence_id)

                    tokens = _tokenize(sentence_text)
                    for tok_idx, token in enumerate(tokens):
                        token_id = f"tok:{doc_id}:{sec_idx}:{para_idx}:{sent_idx}:{tok_idx}"
                        token_embedding = _safe_embed(token)
                        token_metadata = {
                            **sentence_metadata,
                            "token_index": tok_idx,
                        }
                        token_node = IndexNode(
                            id=token_id,
                            level=IndexLevel.SUBWORD,
                            content=token,
                            summary=token,
                            parent_id=sentence_id,
                            embeddings=token_embedding,
                            metadata=token_metadata,
                        )
                        self.nodes[token_id] = token_node
                        sentence_node.children_ids.append(token_id)

        return root_id

    def query(
        self,
        query: str,
        target_level: IndexLevel = IndexLevel.PARAGRAPH,
        max_results: int = 10,
    ) -> List[IndexNode]:
        """Query the index returning nodes at the requested granularity."""
        query = (query or "").strip()
        if not query:
            raise ValueError("query must be non-empty")

        matches: List[tuple[IndexNode, float]] = []
        for node in self.nodes.values():
            if node.level != target_level:
                continue
            score = _similarity(node.content or node.summary, query)
            if score > 0:
                matches.append((node, score))

        matches.sort(key=lambda item: item[1], reverse=True)
        return [node for node, _ in matches[:max_results]]

    def zoom_in(self, node_id: str) -> List[IndexNode]:
        """Return children of the specified node."""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.nodes[child_id] for child_id in node.children_ids if child_id in self.nodes]

    def zoom_out(self, node_id: str) -> Optional[IndexNode]:
        """Return the parent of the specified node."""
        node = self.nodes.get(node_id)
        if not node or not node.parent_id:
            return None
        return self.nodes.get(node.parent_id)

    def get_context(
        self,
        node_id: str,
        *,
        include_parent: bool = True,
        include_siblings: bool = False,
    ) -> List[IndexNode]:
        """Return contextual nodes (parent, siblings) for a given node."""
        node = self.nodes.get(node_id)
        if not node:
            return []

        context: List[IndexNode] = []
        if include_parent and node.parent_id and node.parent_id in self.nodes:
            context.append(self.nodes[node.parent_id])

        if include_siblings and node.parent_id and node.parent_id in self.nodes:
            parent = self.nodes[node.parent_id]
            siblings = [
                self.nodes[sib_id]
                for sib_id in parent.children_ids
                if sib_id != node_id and sib_id in self.nodes
            ]
            context.extend(siblings)

        context.append(node)
        return context

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Serialize index to a dictionary."""
        output: Dict[str, Dict[str, Any]] = {}
        for node_id, node in self.nodes.items():
            output[node_id] = {
                "id": node.id,
                "level": node.level.name,
                "content": node.content,
                "summary": node.summary,
                "parent_id": node.parent_id,
                "children_ids": list(node.children_ids),
                "embeddings": list(node.embeddings) if node.embeddings else None,
                "metadata": dict(node.metadata),
            }
        return output

    @classmethod
    def from_dict(cls, payload: Dict[str, Dict[str, Any]]) -> "HierarchicalIndex":
        """Deserialize an index from a dictionary."""
        index = cls()
        for node_id, data in payload.items():
            node = IndexNode(
                id=data["id"],
                level=IndexLevel[data["level"]],
                content=data.get("content", ""),
                summary=data.get("summary", ""),
                parent_id=data.get("parent_id"),
                children_ids=list(data.get("children_ids", []) or []),
                embeddings=list(data.get("embeddings") or []) or None,
                metadata=dict(data.get("metadata") or {}),
            )
            index.nodes[node_id] = node
        # infer root
        index.root_id = next((nid for nid, n in index.nodes.items() if n.parent_id is None), None)
        return index

    def __len__(self) -> int:
        return len(self.nodes)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------


@dataclass
class Section:
    title: str
    paragraphs: List[str]


_HEADING_RE = re.compile(r"^(#+\s.*|[A-Z0-9][A-Z0-9\s\-]{0,80}:|[A-Z][\w\s]{0,80})$")


def _split_into_sections(text: str) -> List[Section]:
    """Split text into sections using heading heuristics."""
    lines = [line.strip() for line in normalize_newlines(text).split("\n")]
    sections: List[Section] = []
    current_title: Optional[str] = None
    current_paragraphs: List[str] = []

    def flush() -> None:
        nonlocal current_title, current_paragraphs
        if not current_paragraphs and current_title is None:
            return
        title = current_title or f"Section {len(sections) + 1}"
        sections.append(Section(title=title, paragraphs=list(current_paragraphs)))
        current_title = None
        current_paragraphs = []

    for line in lines:
        if not line:
            continue
        if _looks_like_heading(line):
            flush()
            current_title = line.strip("# ").strip()
        else:
            current_paragraphs.append(line)
    flush()
    return [section for section in sections if section.paragraphs]


def _looks_like_heading(line: str) -> bool:
    if len(line.split()) <= 12 and (line.isupper() or line.endswith(":") or line.startswith("#")):
        return True
    return bool(_HEADING_RE.match(line))


def _summarize_text(text: str, max_length: int = 160) -> str:
    sentences = parse_sentences(text)
    if sentences:
        summary = sentences[0]
    else:
        summary = text.strip()
    return summary[:max_length].strip()


def _tokenize(sentence: str) -> List[str]:
    tokens = re.findall(r"\w+|\S", sentence)
    return [token for token in tokens if token.strip()]


# Embedding cache: text -> embedding vector
_embedding_cache: Dict[str, List[float]] = {}


def _safe_embed(text: str) -> List[float]:
    """Generate a lightweight embedding for text with caching."""
    # Check cache first
    if text in _embedding_cache:
        return _embedding_cache[text]
    
    # Generate embedding
    if encode_text is not None:  # pragma: no branch
        try:
            embedding = [float(x) for x in encode_text(text)]
            _embedding_cache[text] = embedding
            return embedding
        except Exception:
            pass
    
    embedding = _fallback_embedding(text)
    _embedding_cache[text] = embedding
    return embedding


def _fallback_embedding(text: str) -> List[float]:
    """Simple deterministic embedding using character statistics."""
    text = (text or "").strip()
    if not text:
        return [0.0, 0.0, 0.0]
    codes = [ord(ch) for ch in text[:64]]
    total = sum(codes)
    length = len(codes)
    avg = total / length
    variance = sum((code - avg) ** 2 for code in codes) / length
    return [float(total), float(avg), float(variance)]


def _similarity(text: str, query: str) -> float:
    """Compute a simple similarity between node text and query."""
    text_tokens = set(re.findall(r"\w+", text.lower()))
    query_tokens = set(re.findall(r"\w+", query.lower()))
    if not text_tokens or not query_tokens:
        return 0.0
    overlap = len(text_tokens & query_tokens)
    if overlap == 0:
        return 0.0
    return overlap / math.sqrt(len(query_tokens))


__all__ = [
    "HierarchicalIndex",
    "IndexLevel",
    "IndexNode",
]

