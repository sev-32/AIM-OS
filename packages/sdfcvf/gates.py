"""Parity Gates - Block commits/deploys if quartet parity too low

Gates ensure code, docs, tests, and traces stay aligned before:
- Committing to version control
- Merging pull requests
- Deploying to production
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class GateType(str, Enum):
    """Type of parity gate"""
    PRE_COMMIT = "pre_commit"      # Git pre-commit hook
    PRE_PUSH = "pre_push"          # Git pre-push hook
    PR_REVIEW = "pr_review"        # Pull request gate
    DEPLOYMENT = "deployment"      # Production deployment gate


@dataclass
class GateConfig:
    """Configuration for a parity gate
    
    Attributes:
        gate_type: Type of gate
        parity_threshold: Minimum parity score to pass
        require_complete_quartet: Block if quartet incomplete
        allow_override: Allow human override
        strict_mode: Fail on any warnings
    """
    gate_type: GateType
    parity_threshold: float = 0.90
    require_complete_quartet: bool = True
    allow_override: bool = False
    strict_mode: bool = False


@dataclass
class GateResult:
    """Result of parity gate evaluation
    
    Attributes:
        passed: Whether gate passed
        parity_score: Calculated parity score
        threshold: Gate threshold
        reasons: List of reasons for pass/fail
        can_override: Whether human can override
        warnings: List of warnings
    """
    passed: bool
    parity_score: float
    threshold: float
    reasons: List[str]
    can_override: bool = False
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "passed": self.passed,
            "parity_score": self.parity_score,
            "threshold": self.threshold,
            "reasons": self.reasons,
            "can_override": self.can_override,
            "warnings": self.warnings,
        }


class ParityGate:
    """Parity gate that blocks operations if quartet alignment too low
    
    Examples:
        >>> from sdfcvf import Quartet, ParityCalculator, ParityGate, GateConfig, GateType
        >>> 
        >>> # Setup gate
        >>> config = GateConfig(
        ...     gate_type=GateType.PRE_COMMIT,
        ...     parity_threshold=0.90,
        ...     require_complete_quartet=True
        ... )
        >>> gate = ParityGate(config)
        >>> 
        >>> # Check quartet
        >>> quartet = Quartet(...)
        >>> result = gate.check(quartet)
        >>> 
        >>> if result.passed:
        ...     print("✅ Commit allowed")
        ... else:
        ...     print(f"❌ Blocked: {result.reasons}")
    """
    
    def __init__(self, config: GateConfig):
        """Initialize parity gate
        
        Args:
            config: Gate configuration
        """
        self.config = config
        self.parity_calculator = None  # Set externally if needed
    
    def check(self, quartet: any, parity_result: Optional[any] = None) -> GateResult:
        """Check if quartet passes gate
        
        Args:
            quartet: Quartet to check
            parity_result: Pre-calculated parity (optional, will calculate if None)
            
        Returns:
            GateResult with pass/fail status
        """
        from .parity import ParityCalculator
        from .quartet import Quartet
        
        reasons = []
        warnings = []
        
        # Calculate parity if not provided
        if parity_result is None:
            calc = self.parity_calculator or ParityCalculator()
            parity_result = calc.calculate(quartet)
        
        # Check 1: Quartet completeness
        if self.config.require_complete_quartet and not parity_result.complete:
            reasons.append(f"Incomplete quartet: missing {', '.join(parity_result.warnings)}")
        
        # Check 2: Parity threshold
        if parity_result.parity_score < self.config.parity_threshold:
            reasons.append(
                f"Parity {parity_result.parity_score:.2f} below threshold {self.config.parity_threshold:.2f}"
            )
        
        # Check 3: Strict mode (any warnings = fail)
        if self.config.strict_mode and parity_result.warnings:
            reasons.append(f"Strict mode: {len(parity_result.warnings)} warnings present")
            warnings.extend(parity_result.warnings)
        
        # Determine pass/fail
        passed = len(reasons) == 0
        
        return GateResult(
            passed=passed,
            parity_score=parity_result.parity_score,
            threshold=self.config.parity_threshold,
            reasons=reasons if not passed else ["Parity gate passed"],
            can_override=self.config.allow_override and not passed,
            warnings=parity_result.warnings,
        )
    
    def get_failure_message(self, result: GateResult) -> str:
        """Generate human-readable failure message
        
        Args:
            result: Gate result
            
        Returns:
            Formatted failure message
        """
        if result.passed:
            return "✅ Parity gate PASSED"
        
        msg = f"""
❌ Parity Gate BLOCKED ({self.config.gate_type.value})

Parity Score: {result.parity_score:.2f} (threshold: {result.threshold:.2f})

Reasons:
"""
        for reason in result.reasons:
            msg += f"  - {reason}\n"
        
        if result.warnings:
            msg += "\nWarnings:\n"
            for warning in result.warnings:
                msg += f"  ⚠️ {warning}\n"
        
        if result.can_override:
            msg += "\n💡 Override available: Use --force flag (not recommended)\n"
        else:
            msg += "\n🚫 No override available: Fix quartet parity before proceeding\n"
        
        return msg.strip()


def create_pre_commit_gate() -> ParityGate:
    """Create pre-commit gate with standard config
    
    Returns:
        ParityGate for pre-commit hooks
    """
    config = GateConfig(
        gate_type=GateType.PRE_COMMIT,
        parity_threshold=0.85,  # Slightly relaxed for commits
        require_complete_quartet=False,  # Can commit incomplete
        allow_override=True,  # Can force commit
        strict_mode=False,
    )
    return ParityGate(config)


def create_deployment_gate() -> ParityGate:
    """Create deployment gate with strict config
    
    Returns:
        ParityGate for production deployment
    """
    config = GateConfig(
        gate_type=GateType.DEPLOYMENT,
        parity_threshold=0.95,  # Very strict for production
        require_complete_quartet=True,  # Must be complete
        allow_override=False,  # No override allowed
        strict_mode=True,  # No warnings allowed
    )
    return ParityGate(config)


def create_pr_gate() -> ParityGate:
    """Create pull request gate with moderate config
    
    Returns:
        ParityGate for PR reviews
    """
    config = GateConfig(
        gate_type=GateType.PR_REVIEW,
        parity_threshold=0.90,  # Moderate strictness
        require_complete_quartet=True,  # Should be complete for PR
        allow_override=True,  # Reviewer can override
        strict_mode=False,
    )
    return ParityGate(config)

