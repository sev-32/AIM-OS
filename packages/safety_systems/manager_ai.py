"""
Manager AI System

This system provides comprehensive oversight and guidance for Aether,
ensuring consistent context, memory, and process compliance.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from packages.safety_systems.line_removal_detector import LineRemovalDetector


@dataclass
class ContextState:
    """Represents the current context state"""
    task: str
    goal: str
    constraints: List[str]
    current_file: Optional[str]
    operation: str
    timestamp: datetime
    confidence: float
    memory_usage: Dict[str, Any]


@dataclass
class SafetyViolation:
    """Represents a safety protocol violation"""
    violation_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    file_path: Optional[str]
    operation: str
    timestamp: datetime
    context: Dict[str, Any]
    recommendation: str


@dataclass
class MemoryState:
    """Represents the current memory state"""
    context_history: List[ContextState]
    recent_decisions: List[Dict[str, Any]]
    current_understanding: str
    priorities: List[str]
    confidence_level: float
    memory_gaps: List[str]


@dataclass
class ProcessGuidance:
    """Represents process guidance for Aether"""
    process_name: str
    current_step: int
    total_steps: int
    step_description: str
    next_actions: List[str]
    warnings: List[str]
    recommendations: List[str]


class ManagerAI:
    """Main Manager AI class for overseeing Aether's operations"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.context_history: List[ContextState] = []
        self.safety_violations: List[SafetyViolation] = []
        self.memory_state = MemoryState(
            context_history=[],
            recent_decisions=[],
            current_understanding="",
            priorities=[],
            confidence_level=0.8,
            memory_gaps=[]
        )
        self.line_removal_detector = LineRemovalDetector()
        self.process_templates = self._load_process_templates()
        
        # Create directories
        self.data_dir = Path("data/manager_ai")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing state if available
        self._load_state()
    
    def _default_config(self) -> Dict:
        """Default configuration for Manager AI"""
        return {
            'context_history_limit': 100,
            'confidence_threshold': 0.70,
            'safety_check_interval': 300,  # 5 minutes
            'memory_restoration_threshold': 0.60,
            'process_compliance_threshold': 0.80,
            'enable_line_removal_detection': True,
            'enable_automatic_guidance': True,
            'enable_memory_management': True,
            'enable_safety_enforcement': True
        }
    
    def monitor_aether_action(self, action: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Monitor Aether's actions for safety and compliance
        
        Args:
            action: The action Aether is performing
            context: Context information about the action
            
        Returns:
            Optional guidance or warning message
        """
        try:
            # Update context state
            context_state = self._update_context_state(action, context)
            
            # Check for safety violations
            safety_issues = self._check_safety_violations(action, context)
            
            # Check for context consistency
            context_issues = self._check_context_consistency(context_state)
            
            # Check for memory issues
            memory_issues = self._check_memory_issues(context_state)
            
            # Check for process compliance
            process_issues = self._check_process_compliance(action, context)
            
            # Generate guidance if issues found
            if safety_issues or context_issues or memory_issues or process_issues:
                guidance = self._generate_guidance(
                    safety_issues, context_issues, memory_issues, process_issues
                )
                return guidance
            
            # Update memory state
            self._update_memory_state(context_state)
            
            # Log successful monitoring
            self._log_monitoring(action, context, "SUCCESS")
            
            return None
            
        except Exception as e:
            self._log_monitoring(action, context, f"ERROR: {str(e)}")
            return f"Manager AI error: {str(e)}"
    
    def _update_context_state(self, action: str, context: Dict[str, Any]) -> ContextState:
        """Update the current context state"""
        context_state = ContextState(
            task=context.get('task', 'Unknown'),
            goal=context.get('goal', 'Unknown'),
            constraints=context.get('constraints', []),
            current_file=context.get('file_path'),
            operation=action,
            timestamp=datetime.now(),
            confidence=context.get('confidence', 0.5),
            memory_usage=context.get('memory_usage', {})
        )
        
        # Add to context history
        self.context_history.append(context_state)
        
        # Maintain history limit
        if len(self.context_history) > self.config['context_history_limit']:
            self.context_history = self.context_history[-self.config['context_history_limit']:]
        
        return context_state
    
    def _check_safety_violations(self, action: str, context: Dict[str, Any]) -> List[SafetyViolation]:
        """Check for safety protocol violations"""
        violations = []
        
        # Check for file overwrites without backup
        if 'overwrite' in action.lower() or 'replace' in action.lower():
            if context.get('file_path') and not context.get('backup_created', False):
                violations.append(SafetyViolation(
                    violation_type="file_overwrite_without_backup",
                    severity="high",
                    description="Attempting to overwrite file without creating backup",
                    file_path=context.get('file_path'),
                    operation=action,
                    timestamp=datetime.now(),
                    context=context,
                    recommendation="Create backup before overwriting file"
                ))
        
        # Check for content deletion without verification
        if 'delete' in action.lower() or 'remove' in action.lower():
            if not context.get('content_verified', False):
                violations.append(SafetyViolation(
                    violation_type="content_deletion_without_verification",
                    severity="high",
                    description="Attempting to delete content without verification",
                    file_path=context.get('file_path'),
                    operation=action,
                    timestamp=datetime.now(),
                    context=context,
                    recommendation="Verify content before deletion"
                ))
        
        # Check for safety checklist completion
        if not context.get('safety_checklist_completed', False):
            if action in ['modify', 'update', 'create', 'delete']:
                violations.append(SafetyViolation(
                    violation_type="safety_checklist_not_completed",
                    severity="medium",
                    description="Safety checklist not completed before operation",
                    file_path=context.get('file_path'),
                    operation=action,
                    timestamp=datetime.now(),
                    context=context,
                    recommendation="Complete safety checklist before proceeding"
                ))
        
        # Check for line removal detection
        if self.config['enable_line_removal_detection']:
            if context.get('file_path') and 'modify' in action.lower():
                file_path = context.get('file_path')
                new_content = context.get('new_content', '')
                
                if os.path.exists(file_path) and new_content:
                    # Use line removal detector to check for content loss
                    old_content = self._read_file(file_path)
                    analysis = self.line_removal_detector._analyze_changes(old_content, new_content, file_path)
                    
                    if analysis.content_loss_detected:
                        violations.append(SafetyViolation(
                            violation_type="potential_content_loss",
                            severity="critical",
                            description=f"Potential content loss detected: {', '.join(analysis.warnings)}",
                            file_path=file_path,
                            operation=action,
                            timestamp=datetime.now(),
                            context=context,
                            recommendation="Review content changes before proceeding"
                        ))
        
        # Store violations
        self.safety_violations.extend(violations)
        
        return violations
    
    def _check_context_consistency(self, context_state: ContextState) -> List[str]:
        """Check for context consistency issues"""
        issues = []
        
        # Check for context drift
        if len(self.context_history) > 1:
            last_context = self.context_history[-2]
            if self._detect_context_drift(last_context, context_state):
                issues.append("Context drift detected - task/goal may have changed unexpectedly")
        
        # Check for missing required context
        required_context = ["task", "goal"]
        for req in required_context:
            if not getattr(context_state, req, None) or getattr(context_state, req) == "Unknown":
                issues.append(f"Missing required context: {req}")
        
        # Check for confidence threshold
        if context_state.confidence < self.config['confidence_threshold']:
            issues.append(f"Confidence below threshold: {context_state.confidence:.2f} < {self.config['confidence_threshold']}")
        
        return issues
    
    def _check_memory_issues(self, context_state: ContextState) -> List[str]:
        """Check for memory issues"""
        issues = []
        
        # Check for memory loss indicators
        if 'forgot' in str(context_state).lower() or 'lost' in str(context_state).lower():
            issues.append("Memory loss detected in context")
        
        # Check for inconsistent memory
        if self._detect_memory_inconsistency(context_state):
            issues.append("Memory inconsistency detected")
        
        # Check for memory gaps
        if len(self.memory_state.memory_gaps) > 5:
            issues.append("Multiple memory gaps detected")
        
        return issues
    
    def _check_process_compliance(self, action: str, context: Dict[str, Any]) -> List[str]:
        """Check for process compliance issues"""
        issues = []
        
        # Check if action matches expected process step
        if 'expected_action' in context:
            if action != context['expected_action']:
                issues.append(f"Action mismatch: expected '{context['expected_action']}', got '{action}'")
        
        # Check for process step completion
        if 'process_step' in context:
            step = context['process_step']
            if not step.get('completed', False):
                issues.append(f"Process step not completed: {step.get('description', 'Unknown')}")
        
        return issues
    
    def _detect_context_drift(self, old_context: ContextState, new_context: ContextState) -> bool:
        """Detect if context has drifted significantly"""
        # Check for task changes
        if old_context.task != new_context.task:
            return True
        
        # Check for goal changes
        if old_context.goal != new_context.goal:
            return True
        
        # Check for significant confidence changes
        confidence_diff = abs(old_context.confidence - new_context.confidence)
        if confidence_diff > 0.3:
            return True
        
        return False
    
    def _detect_memory_inconsistency(self, context_state: ContextState) -> bool:
        """Detect memory inconsistencies"""
        # Check for conflicting information in recent decisions
        recent_decisions = self.memory_state.recent_decisions[-5:]  # Last 5 decisions
        
        for decision in recent_decisions:
            if decision.get('confidence', 0) > 0.8 and context_state.confidence < 0.5:
                return True
        
        return False
    
    def _generate_guidance(self, safety_issues: List[SafetyViolation], context_issues: List[str],
                          memory_issues: List[str], process_issues: List[str]) -> str:
        """Generate guidance based on detected issues"""
        guidance_parts = []
        
        if safety_issues:
            guidance_parts.append("🚨 SAFETY ISSUES DETECTED:")
            for violation in safety_issues:
                severity_emoji = {
                    'low': '🟡',
                    'medium': '🟠',
                    'high': '🔴',
                    'critical': '🚨'
                }.get(violation.severity, '⚠️')
                
                guidance_parts.append(f"  {severity_emoji} {violation.description}")
                guidance_parts.append(f"    → {violation.recommendation}")
            
            guidance_parts.append("  → STOP and follow safety protocols")
        
        if context_issues:
            guidance_parts.append("⚠️ CONTEXT ISSUES DETECTED:")
            for issue in context_issues:
                guidance_parts.append(f"  - {issue}")
            guidance_parts.append("  → Re-establish context before proceeding")
        
        if memory_issues:
            guidance_parts.append("🧠 MEMORY ISSUES DETECTED:")
            for issue in memory_issues:
                guidance_parts.append(f"  - {issue}")
            guidance_parts.append("  → Restore memory before proceeding")
        
        if process_issues:
            guidance_parts.append("📋 PROCESS ISSUES DETECTED:")
            for issue in process_issues:
                guidance_parts.append(f"  - {issue}")
            guidance_parts.append("  → Follow established processes")
        
        return "\n".join(guidance_parts)
    
    def _update_memory_state(self, context_state: ContextState):
        """Update the memory state"""
        self.memory_state.context_history = self.context_history.copy()
        self.memory_state.current_understanding = f"Working on {context_state.task} with goal {context_state.goal}"
        self.memory_state.confidence_level = context_state.confidence
        
        # Update priorities based on context
        if context_state.task not in self.memory_state.priorities:
            self.memory_state.priorities.append(context_state.task)
        
        # Maintain priority limit
        if len(self.memory_state.priorities) > 10:
            self.memory_state.priorities = self.memory_state.priorities[-10:]
    
    def provide_process_guidance(self, process_name: str, current_step: int = 0) -> ProcessGuidance:
        """Provide process guidance for a specific process"""
        if process_name in self.process_templates:
            template = self.process_templates[process_name]
            steps = template['steps']
            
            if current_step < len(steps):
                step = steps[current_step]
                return ProcessGuidance(
                    process_name=process_name,
                    current_step=current_step + 1,
                    total_steps=len(steps),
                    step_description=step['description'],
                    next_actions=step['actions'],
                    warnings=step.get('warnings', []),
                    recommendations=step.get('recommendations', [])
                )
        
        # Default guidance
        return ProcessGuidance(
            process_name=process_name,
            current_step=current_step,
            total_steps=1,
            step_description="Unknown process",
            next_actions=["Follow established protocols"],
            warnings=["Process not recognized"],
            recommendations=["Use standard safety protocols"]
        )
    
    def restore_memory(self, context_hints: List[str]) -> str:
        """Restore memory based on context hints"""
        restoration_info = []
        
        # Search context history for relevant information
        for hint in context_hints:
            for context in self.context_history:
                if hint.lower() in context.task.lower() or hint.lower() in context.goal.lower():
                    restoration_info.append(f"Found context: {context.task} - {context.goal}")
        
        # Search recent decisions
        for hint in context_hints:
            for decision in self.memory_state.recent_decisions:
                if hint.lower() in str(decision).lower():
                    restoration_info.append(f"Found decision: {decision}")
        
        if restoration_info:
            return "Memory restoration information:\n" + "\n".join(restoration_info)
        else:
            return "No relevant memory found for the given hints"
    
    def _load_process_templates(self) -> Dict[str, Dict]:
        """Load process templates for guidance"""
        return {
            'documentation_organization': {
                'steps': [
                    {
                        'description': 'Discovery - Find existing documentation',
                        'actions': ['Search for existing files', 'Analyze current content'],
                        'warnings': ['Check for existing content before creating new'],
                        'recommendations': ['Use line removal detection', 'Create backups']
                    },
                    {
                        'description': 'Analysis - Understand current state',
                        'actions': ['Analyze content quality', 'Identify gaps'],
                        'warnings': ['Preserve valuable existing content'],
                        'recommendations': ['Document findings', 'Plan preservation']
                    },
                    {
                        'description': 'Planning - Create organization plan',
                        'actions': ['Create structure plan', 'Define preservation strategy'],
                        'warnings': ['Ensure no content loss'],
                        'recommendations': ['Use bitemporal versioning', 'Create backups']
                    },
                    {
                        'description': 'Implementation - Execute organization',
                        'actions': ['Implement changes', 'Verify preservation'],
                        'warnings': ['Monitor for content loss'],
                        'recommendations': ['Use safety protocols', 'Verify results']
                    },
                    {
                        'description': 'Validation - Verify results',
                        'actions': ['Verify content preservation', 'Check quality'],
                        'warnings': ['Ensure no regressions'],
                        'recommendations': ['Run tests', 'Document results']
                    }
                ]
            },
            'file_modification': {
                'steps': [
                    {
                        'description': 'Pre-modification safety check',
                        'actions': ['Check existing content', 'Create backup', 'Verify safety'],
                        'warnings': ['Never modify without checking existing content'],
                        'recommendations': ['Use line removal detection', 'Create snapshots']
                    },
                    {
                        'description': 'Content analysis',
                        'actions': ['Analyze changes', 'Detect content loss', 'Generate alerts'],
                        'warnings': ['Watch for content loss'],
                        'recommendations': ['Review all changes', 'Confirm preservation']
                    },
                    {
                        'description': 'Safe modification',
                        'actions': ['Apply changes', 'Verify results', 'Log operation'],
                        'warnings': ['Verify changes are correct'],
                        'recommendations': ['Test modifications', 'Document changes']
                    }
                ]
            }
        }
    
    def _load_state(self):
        """Load existing state from disk"""
        state_file = self.data_dir / "manager_ai_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                
                # Restore context history
                if 'context_history' in state_data:
                    self.context_history = [
                        ContextState(**ctx) for ctx in state_data['context_history']
                    ]
                
                # Restore safety violations
                if 'safety_violations' in state_data:
                    self.safety_violations = [
                        SafetyViolation(**violation) for violation in state_data['safety_violations']
                    ]
                
                # Restore memory state
                if 'memory_state' in state_data:
                    memory_data = state_data['memory_state']
                    self.memory_state = MemoryState(
                        context_history=self.context_history,
                        recent_decisions=memory_data.get('recent_decisions', []),
                        current_understanding=memory_data.get('current_understanding', ''),
                        priorities=memory_data.get('priorities', []),
                        confidence_level=memory_data.get('confidence_level', 0.8),
                        memory_gaps=memory_data.get('memory_gaps', [])
                    )
            except Exception as e:
                print(f"Warning: Could not load Manager AI state: {e}")
    
    def _save_state(self):
        """Save current state to disk"""
        state_file = self.data_dir / "manager_ai_state.json"
        
        state_data = {
            'context_history': [asdict(ctx) for ctx in self.context_history],
            'safety_violations': [asdict(violation) for violation in self.safety_violations],
            'memory_state': {
                'recent_decisions': self.memory_state.recent_decisions,
                'current_understanding': self.memory_state.current_understanding,
                'priorities': self.memory_state.priorities,
                'confidence_level': self.memory_state.confidence_level,
                'memory_gaps': self.memory_state.memory_gaps
            },
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save Manager AI state: {e}")
    
    def _read_file(self, file_path: str) -> str:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return ""
    
    def _log_monitoring(self, action: str, context: Dict[str, Any], status: str):
        """Log monitoring activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'context': context,
            'status': status
        }
        
        log_file = self.data_dir / f"monitoring_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass  # Don't fail on logging errors


# Convenience function for easy usage
def monitor_aether_action(action: str, context: Dict[str, Any]) -> Optional[str]:
    """
    Convenience function to monitor Aether's actions
    
    Args:
        action: The action Aether is performing
        context: Context information about the action
        
    Returns:
        Optional guidance or warning message
    """
    manager_ai = ManagerAI()
    return manager_ai.monitor_aether_action(action, context)
