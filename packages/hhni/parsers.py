"""Text parsing helpers for HHNI."""

from __future__ import annotations

import re
from typing import List

_PARAGRAPH_SPLIT_RE = re.compile(r"(?:\r?\n){2,}")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")  # naive fallback if needed


def normalize_newlines(text: str) -> str:
    """Normalize different newline styles to `\n`."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_non_empty(chunks: List[str]) -> List[str]:
    return [chunk.strip() for chunk in chunks if chunk and chunk.strip()]


def parse_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs using blank-line heuristic."""
    normalized = normalize_newlines(text or "")
    if not normalized.strip():
        return []
    chunks = _PARAGRAPH_SPLIT_RE.split(normalized)
    return strip_non_empty(chunks)


def parse_sentences(paragraph: str) -> List[str]:
    """Split a paragraph into sentences using simple punctuation rules."""
    text = paragraph.strip()
    if not text:
        return []
    # Use regex that keeps punctuation by splitting on boundaries
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    return strip_non_empty(sentences)
