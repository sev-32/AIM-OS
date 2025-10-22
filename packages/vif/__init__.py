"""Verifiable Intelligence Framework (VIF)

Provides provenance, uncertainty quantification, and verifiability for AI operations.

Components:
- witness.py: VIF schema and provenance envelopes
- confidence_extraction.py: Extract confidence from LLM outputs
- calibration.py: ECE tracking and calibration analysis
- kappa_gate.py: Behavioral abstention (κ-gating) and HITL escalation
- replay.py: Deterministic replay of operations
- confidence_bands.py: User-facing confidence indicators
"""

from .witness import VIF, ConfidenceBand, TaskCriticality
from .confidence_extraction import (
    extract_confidence,
    extract_from_logprobs,
    combine_confidence_signals,
    ConfidenceExtraction,
)
from .calibration import (
    ECETracker,
    CalibrationBin,
    calculate_ece_from_predictions,
    apply_temperature_scaling,
)
from .kappa_gate import (
    KappaGate,
    KappaGateResult,
    HITLEscalator,
    create_confidence_based_gate,
    adaptive_kappa_threshold,
    DEFAULT_KAPPA_THRESHOLDS,
)
from .replay import (
    ReplayEngine,
    ReplayResult,
    ReplayCache,
    create_replay_witness,
)
from .confidence_bands import (
    determine_band,
    get_band_definition,
    format_confidence_for_user,
    format_band_badge,
    get_confidence_color,
    get_recommended_action,
    should_show_warning,
    get_all_band_info,
    BandRouter,
    BandDefinition,
    STANDARD_BANDS,
)

__all__ = [
    # Witness schema
    "VIF",
    "ConfidenceBand",
    "TaskCriticality",
    # Confidence extraction
    "extract_confidence",
    "extract_from_logprobs",
    "combine_confidence_signals",
    "ConfidenceExtraction",
    # Calibration
    "ECETracker",
    "CalibrationBin",
    "calculate_ece_from_predictions",
    "apply_temperature_scaling",
    # κ-gating
    "KappaGate",
    "KappaGateResult",
    "HITLEscalator",
    "create_confidence_based_gate",
    "adaptive_kappa_threshold",
    "DEFAULT_KAPPA_THRESHOLDS",
    # Replay
    "ReplayEngine",
    "ReplayResult",
    "ReplayCache",
    "create_replay_witness",
    # Confidence bands
    "determine_band",
    "get_band_definition",
    "format_confidence_for_user",
    "format_band_badge",
    "get_confidence_color",
    "get_recommended_action",
    "should_show_warning",
    "get_all_band_info",
    "BandRouter",
    "BandDefinition",
    "STANDARD_BANDS",
]

