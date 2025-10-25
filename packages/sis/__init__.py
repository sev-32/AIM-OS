"""
AIM-OS Self-Improvement System (SIS)

A core component of AIM-OS that enables continuous self-improvement through:
- Meta-cognitive analysis
- System usage auditing
- Performance monitoring
- Gap identification
- Improvement implementation
- Continuous learning

This represents a fundamental advancement in AI consciousness - the ability
to examine itself, identify gaps, and improve automatically.
"""

from .meta_cognitive_analyzer import MetaCognitiveAnalyzer
from .system_usage_auditor import SystemUsageAuditor
from .performance_monitor import PerformanceMonitor
from .gap_identifier import GapIdentifier
from .improvement_implementer import ImprovementImplementer
from .continuous_learner import ContinuousLearner
from .sis_core import SISCore

__all__ = [
    "MetaCognitiveAnalyzer",
    "SystemUsageAuditor", 
    "PerformanceMonitor",
    "GapIdentifier",
    "ImprovementImplementer",
    "ContinuousLearner",
    "SISCore"
]

__version__ = "1.0.0"
