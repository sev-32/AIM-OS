"""Strategic compression utilities for HHNI context optimization.

Implements age-based compression strategies to maximize information density
within token budgets while preserving recent and high-priority content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple

from .budget_manager import BudgetItem


class CompressionLevel(Enum):
    """Compression levels based on age and priority."""

    FULL = 1  # Recent: Full detail (no compression)
    DETAILED = 2  # Week old: Detailed summary
    BRIEF = 3  # Month old: Brief summary
    REFERENCE = 4  # Old: Reference only


@dataclass
class CompressionMetrics:
    """Metrics from a compression operation."""

    total_candidates: int
    compressed_count: int
    tokens_saved: int
    compression_ratio: float
    levels_applied: Dict[str, int] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


@dataclass
class CompressionConfig:
    """Configuration for strategic compression."""

    # Age thresholds (in days)
    full_detail_threshold: int = 7  # < 7 days: full detail
    detailed_summary_threshold: int = 30  # 7-30 days: detailed summary
    brief_summary_threshold: int = 90  # 30-90 days: brief summary
    # > 90 days: reference only

    # Priority overrides (high priority items get less compression)
    priority_threshold: float = 0.85  # Items above this get preferential treatment

    # Compression ratios (target token reduction)
    detailed_ratio: float = 0.7  # Keep 70% of tokens
    brief_ratio: float = 0.4  # Keep 40% of tokens
    reference_ratio: float = 0.15  # Keep 15% of tokens

    # Quality preservation
    preserve_key_sentences: bool = True
    min_compressed_tokens: int = 10  # Don't compress below this


def compress_candidates(
    items: Sequence[BudgetItem],
    *,
    config: Optional[CompressionConfig] = None,
    reference_time: Optional[datetime] = None,
    audit: Optional[List[Dict[str, object]]] = None,
) -> Tuple[List[BudgetItem], CompressionMetrics]:
    """
    Apply strategic compression to context items based on age and priority.

    Args:
        items: Candidate budget items to potentially compress.
        config: Compression configuration (uses defaults if None).
        reference_time: Time to measure age from (defaults to now).
        audit: Optional list to populate with compression details.

    Returns:
        Tuple of (compressed_items, metrics).
    """
    config = config or CompressionConfig()
    reference_time = reference_time or datetime.now(timezone.utc)
    candidates = list(items)

    if not candidates:
        metrics = CompressionMetrics(0, 0, 0, 1.0)
        return [], metrics

    compressed_items: List[BudgetItem] = []
    compressed_count = 0
    tokens_saved = 0
    level_counts: Dict[str, int] = {
        "FULL": 0,
        "DETAILED": 0,
        "BRIEF": 0,
        "REFERENCE": 0,
    }

    for item in candidates:
        # Determine age
        timestamp = _extract_timestamp(item)
        age_days = _calculate_age_days(timestamp, reference_time) if timestamp else 0

        # Determine priority (from relevance score and metadata)
        priority = _calculate_priority(item)

        # Determine compression level
        level = _determine_compression_level(
            age_days,
            priority,
            config,
        )

        # Apply compression
        compressed_item, saved_tokens = _apply_compression(
            item,
            level,
            config,
        )

        compressed_items.append(compressed_item)

        if saved_tokens > 0:
            compressed_count += 1
            tokens_saved += saved_tokens

        level_counts[level.name] += 1

        # Audit trail
        if audit is not None:
            audit.append({
                "source_id": item.source_id,
                "age_days": age_days,
                "priority": priority,
                "compression_level": level.name,
                "original_tokens": item.token_count,
                "compressed_tokens": compressed_item.token_count,
                "tokens_saved": saved_tokens,
            })

    total_original_tokens = sum(item.token_count for item in candidates)
    total_compressed_tokens = sum(item.token_count for item in compressed_items)

    compression_ratio = (
        total_compressed_tokens / total_original_tokens
        if total_original_tokens > 0
        else 1.0
    )

    metrics = CompressionMetrics(
        total_candidates=len(candidates),
        compressed_count=compressed_count,
        tokens_saved=tokens_saved,
        compression_ratio=compression_ratio,
        levels_applied=level_counts,
    )

    return compressed_items, metrics


# --------------------------------------------------------------------------- #
# Helpers


def _extract_timestamp(item: BudgetItem) -> Optional[datetime]:
    """Extract timestamp from item metadata."""
    metadata = item.metadata
    ts = metadata.get("timestamp") or metadata.get("created_at") or metadata.get("updated_at")

    if isinstance(ts, datetime):
        return ts

    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(float(ts), tz=timezone.utc)

    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            pass

        # Try common formats
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue

    return None


def _calculate_age_days(timestamp: datetime, reference_time: datetime) -> float:
    """Calculate age in days from reference time."""
    delta = reference_time - timestamp
    return delta.total_seconds() / 86400.0


def _calculate_priority(item: BudgetItem) -> float:
    """Calculate priority score for an item."""
    # Start with relevance score
    priority = item.relevance_score

    # Metadata priority takes precedence if specified
    metadata = item.metadata
    for key in ("priority", "importance", "weight"):
        value = metadata.get(key)
        if isinstance(value, (int, float)):
            # Use max to ensure metadata priority can override relevance
            priority = max(priority, float(value))

    # Confidence boosts priority slightly
    for key in ("confidence", "authority", "evidence"):
        value = metadata.get(key)
        if isinstance(value, (int, float)):
            priority = min(priority + float(value) * 0.15, 1.0)  # Boost up to 15%

    return min(priority, 1.0)  # Cap at 1.0


def _determine_compression_level(
    age_days: float,
    priority: float,
    config: CompressionConfig,
) -> CompressionLevel:
    """Determine compression level based on age and priority."""
    # High priority items get preferential treatment (less compression)
    if priority >= config.priority_threshold:
        # Shift thresholds significantly for high-priority items
        if age_days < config.full_detail_threshold * 3:  # 21 days
            return CompressionLevel.FULL
        elif age_days < config.detailed_summary_threshold * 2.5:  # 75 days
            return CompressionLevel.DETAILED
        elif age_days < config.brief_summary_threshold * 2:  # 180 days
            return CompressionLevel.BRIEF
        else:
            return CompressionLevel.REFERENCE

    # Normal priority items use standard thresholds
    if age_days < config.full_detail_threshold:
        return CompressionLevel.FULL
    elif age_days < config.detailed_summary_threshold:
        return CompressionLevel.DETAILED
    elif age_days < config.brief_summary_threshold:
        return CompressionLevel.BRIEF
    else:
        return CompressionLevel.REFERENCE


def _apply_compression(
    item: BudgetItem,
    level: CompressionLevel,
    config: CompressionConfig,
) -> Tuple[BudgetItem, int]:
    """Apply compression to an item and return (compressed_item, tokens_saved)."""
    if level == CompressionLevel.FULL:
        # No compression
        return item, 0

    content = item.content
    original_tokens = item.token_count

    # Don't compress if already below minimum
    if original_tokens <= config.min_compressed_tokens:
        return item, 0

    # Determine target token count based on compression level
    if level == CompressionLevel.DETAILED:
        target_tokens = int(original_tokens * config.detailed_ratio)
    elif level == CompressionLevel.BRIEF:
        target_tokens = int(original_tokens * config.brief_ratio)
    else:  # REFERENCE
        target_tokens = int(original_tokens * config.reference_ratio)

    target_tokens = max(target_tokens, config.min_compressed_tokens)

    # Apply compression
    if config.preserve_key_sentences:
        compressed_content = _compress_preserving_key_sentences(
            content,
            target_tokens,
            level,
        )
    else:
        compressed_content = _simple_truncate(content, target_tokens)

    # Calculate actual tokens saved
    from .budget_manager import TokenBudgetManager

    budget_manager = TokenBudgetManager()
    compressed_tokens = budget_manager.count_tokens(compressed_content)
    tokens_saved = original_tokens - compressed_tokens

    # Create compressed item
    compressed_item = BudgetItem(
        content=compressed_content,
        relevance_score=item.relevance_score,
        token_count=compressed_tokens,
        source_id=item.source_id,
        level=item.level,
        metadata={
            **item.metadata,
            "compressed": True,
            "compression_level": level.name,
            "original_tokens": original_tokens,
            "tokens_saved": tokens_saved,
        },
    )

    return compressed_item, tokens_saved


def _compress_preserving_key_sentences(
    content: str,
    target_tokens: int,
    level: CompressionLevel,
) -> str:
    """Intelligently compress content by preserving key sentences."""
    sentences = _split_into_sentences(content)

    if not sentences:
        return content[:target_tokens * 4]  # Rough approximation

    # For DETAILED: keep first and last sentences, sample middle
    if level == CompressionLevel.DETAILED:
        if len(sentences) <= 3:
            return content

        # Keep first, last, and most important middle sentences
        result = [sentences[0]]
        middle_count = max(1, len(sentences) - 3)
        step = max(1, middle_count // 2)
        result.extend(sentences[1:-1:step])
        result.append(sentences[-1])

        return " ".join(result)

    # For BRIEF: keep first and last sentence only
    elif level == CompressionLevel.BRIEF:
        if len(sentences) <= 2:
            return content

        return f"{sentences[0]} ... {sentences[-1]}"

    # For REFERENCE: keep first sentence + metadata
    else:  # REFERENCE
        first_sentence = sentences[0] if sentences else content[:100]
        summary_note = f"[{len(sentences)} sentences, compressed to reference]"
        return f"{first_sentence} {summary_note}"


def _simple_truncate(content: str, target_tokens: int) -> str:
    """Simple truncation fallback."""
    # Rough approximation: 1 token ≈ 4 characters
    target_chars = target_tokens * 4
    if len(content) <= target_chars:
        return content

    truncated = content[:target_chars]
    # Try to end at sentence boundary
    last_period = truncated.rfind(".")
    if last_period > target_chars // 2:
        truncated = truncated[: last_period + 1]

    return truncated + "..."


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences (simple implementation)."""
    # Simple sentence splitting on period, exclamation, question mark
    sentences = re.split(r"[.!?]+", text)
    return [s.strip() for s in sentences if s.strip()]


__all__ = [
    "CompressionLevel",
    "CompressionMetrics",
    "CompressionConfig",
    "compress_candidates",
]

