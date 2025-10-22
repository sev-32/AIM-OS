"""Confidence Bands for User Trust

Provides user-friendly confidence indicators:
- Band A (🟢 Green): High confidence (≥0.90) - "Trust this"
- Band B (🟡 Yellow): Medium confidence (0.70-0.89) - "Review this"
- Band C (🔴 Red): Low confidence (<0.70) - "Don't trust this"
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ConfidenceBand(str, Enum):
    """Confidence band levels"""
    A = "A"  # High confidence (green)
    B = "B"  # Medium confidence (yellow)
    C = "C"  # Low confidence (red)


@dataclass
class BandDefinition:
    """Definition of a confidence band"""
    band: ConfidenceBand
    name: str
    color: str
    emoji: str
    min_confidence: float
    max_confidence: float
    user_message: str
    recommended_action: str


# Standard band definitions
STANDARD_BANDS = {
    ConfidenceBand.A: BandDefinition(
        band=ConfidenceBand.A,
        name="High Confidence",
        color="green",
        emoji="🟢",
        min_confidence=0.90,
        max_confidence=1.00,
        user_message="This answer is highly reliable",
        recommended_action="Trust this response"
    ),
    ConfidenceBand.B: BandDefinition(
        band=ConfidenceBand.B,
        name="Medium Confidence",
        color="yellow",
        emoji="🟡",
        min_confidence=0.70,
        max_confidence=0.89,
        user_message="This answer is moderately reliable",
        recommended_action="Review before acting on this"
    ),
    ConfidenceBand.C: BandDefinition(
        band=ConfidenceBand.C,
        name="Low Confidence",
        color="red",
        emoji="🔴",
        min_confidence=0.00,
        max_confidence=0.69,
        user_message="This answer may be unreliable",
        recommended_action="Verify independently before using"
    ),
}


def determine_band(confidence: float) -> ConfidenceBand:
    """Determine confidence band from score
    
    Args:
        confidence: Confidence score (0.0-1.0)
        
    Returns:
        ConfidenceBand (A, B, or C)
        
    Examples:
        >>> determine_band(0.95)
        <ConfidenceBand.A: 'A'>
        >>> determine_band(0.75)
        <ConfidenceBand.B: 'B'>
        >>> determine_band(0.50)
        <ConfidenceBand.C: 'C'>
    """
    if confidence >= 0.90:
        return ConfidenceBand.A
    elif confidence >= 0.70:
        return ConfidenceBand.B
    else:
        return ConfidenceBand.C


def get_band_definition(band: ConfidenceBand) -> BandDefinition:
    """Get definition for a band
    
    Args:
        band: ConfidenceBand
        
    Returns:
        BandDefinition with all UI info
    """
    return STANDARD_BANDS[band]


def format_confidence_for_user(
    confidence: float,
    *,
    include_emoji: bool = True,
    include_percentage: bool = True,
    include_message: bool = True,
) -> str:
    """Format confidence score for user display
    
    Args:
        confidence: Confidence score (0.0-1.0)
        include_emoji: Include emoji indicator
        include_percentage: Include percentage value
        include_message: Include user message
        
    Returns:
        Formatted string for user
        
    Examples:
        >>> format_confidence_for_user(0.95)
        '🟢 95% - This answer is highly reliable'
        
        >>> format_confidence_for_user(0.75, include_message=False)
        '🟡 75%'
    """
    band = determine_band(confidence)
    definition = get_band_definition(band)
    
    parts = []
    
    if include_emoji:
        parts.append(definition.emoji)
    
    if include_percentage:
        parts.append(f"{confidence * 100:.0f}%")
    
    if include_message:
        parts.append(f"- {definition.user_message}")
    
    return " ".join(parts)


def format_band_badge(band: ConfidenceBand) -> str:
    """Format band as badge (for UI)
    
    Args:
        band: ConfidenceBand
        
    Returns:
        Badge string
        
    Examples:
        >>> format_band_badge(ConfidenceBand.A)
        '🟢 Band A'
    """
    definition = get_band_definition(band)
    return f"{definition.emoji} Band {band.value}"


def get_confidence_color(confidence: float) -> str:
    """Get color for confidence score
    
    Args:
        confidence: Confidence score
        
    Returns:
        Color name ('green', 'yellow', 'red')
    """
    band = determine_band(confidence)
    return get_band_definition(band).color


def get_recommended_action(confidence: float) -> str:
    """Get recommended user action for confidence level
    
    Args:
        confidence: Confidence score
        
    Returns:
        Recommended action string
    """
    band = determine_band(confidence)
    return get_band_definition(band).recommended_action


def should_show_warning(confidence: float) -> bool:
    """Determine if UI should show warning
    
    Args:
        confidence: Confidence score
        
    Returns:
        True if Band C (low confidence)
    """
    return determine_band(confidence) == ConfidenceBand.C


def get_all_band_info() -> List[Dict]:
    """Get info for all bands (for UI documentation)
    
    Returns:
        List of band definitions as dicts
    """
    return [
        {
            "band": band.value,
            "name": defn.name,
            "color": defn.color,
            "emoji": defn.emoji,
            "range": f"{defn.min_confidence:.0%} - {defn.max_confidence:.0%}",
            "message": defn.user_message,
            "action": defn.recommended_action,
        }
        for band, defn in STANDARD_BANDS.items()
    ]


class BandRouter:
    """Route operations based on confidence bands
    
    Different bands can trigger different workflows:
    - Band A: Proceed automatically
    - Band B: Proceed with user notification
    - Band C: Request user review before proceeding
    """
    
    def __init__(
        self,
        auto_proceed_bands: Optional[List[ConfidenceBand]] = None,
        review_required_bands: Optional[List[ConfidenceBand]] = None,
    ):
        """Initialize band router
        
        Args:
            auto_proceed_bands: Bands that can proceed automatically
            review_required_bands: Bands that require human review
        """
        self.auto_proceed_bands = auto_proceed_bands or [ConfidenceBand.A]
        self.review_required_bands = review_required_bands or [ConfidenceBand.C]
    
    def route(self, confidence: float) -> str:
        """Determine routing for confidence score
        
        Args:
            confidence: Confidence score
            
        Returns:
            Routing decision: 'auto_proceed', 'notify', or 'review_required'
        """
        band = determine_band(confidence)
        
        if band in self.auto_proceed_bands:
            return "auto_proceed"
        elif band in self.review_required_bands:
            return "review_required"
        else:
            return "notify"
    
    def can_auto_proceed(self, confidence: float) -> bool:
        """Check if can proceed automatically
        
        Args:
            confidence: Confidence score
            
        Returns:
            True if band allows auto-proceed
        """
        return self.route(confidence) == "auto_proceed"

