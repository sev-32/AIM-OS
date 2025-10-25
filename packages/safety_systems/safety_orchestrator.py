"""
Safety Orchestrator

This module orchestrates all safety systems to provide comprehensive protection
for Aether's operations, including Manager AI, Parser AI, Query System, and
Line Removal Detection.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from packages.safety_systems.manager_ai import ManagerAI
from packages.safety_systems.line_removal_detector import LineRemovalDetector
from packages.safety_systems.protocol_educator import ProtocolEducator


@dataclass
class SafetyOperation:
    """Represents a safety operation"""
    operation_id: str
    operation_type: str
    file_path: Optional[str]
    content: Optional[str]
    context: Dict[str, Any]
    timestamp: datetime
    status: str  # 'pending', 'approved', 'rejected', 'completed'
    safety_checks: List[str]
    warnings: List[str]
    recommendations: List[str]


@dataclass
class SafetyResult:
    """Represents the result of safety checks"""
    operation_id: str
    approved: bool
    warnings: List[str]
    recommendations: List[str]
    manager_ai_guidance: Optional[str]
    line_removal_analysis: Optional[Dict[str, Any]]
    requires_user_confirmation: bool
    user_response: Optional[str]


class SafetyOrchestrator:
    """Main orchestrator for all safety systems"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
        # Initialize safety systems
        self.manager_ai = ManagerAI(self.config.get('manager_ai', {}))
        self.line_removal_detector = LineRemovalDetector(self.config.get('line_removal_detector', {}))
        self.protocol_educator = ProtocolEducator(self.config.get('protocol_educator', {}))
        
        # Operation tracking
        self.active_operations: Dict[str, SafetyOperation] = {}
        self.operation_history: List[SafetyOperation] = []
        
        # Create directories
        self.data_dir = Path("data/safety_orchestrator")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing state
        self._load_state()
    
    def _default_config(self) -> Dict:
        """Default configuration for safety orchestrator"""
        return {
            'enable_manager_ai': True,
            'enable_line_removal_detection': True,
            'enable_automatic_approval': False,
            'enable_user_notifications': True,
            'operation_timeout': 3600,  # 1 hour
            'max_concurrent_operations': 10,
            'safety_check_timeout': 30,  # 30 seconds
            'manager_ai': {
                'confidence_threshold': 0.70,
                'enable_safety_enforcement': True,
                'enable_memory_management': True
            },
            'line_removal_detector': {
                'size_reduction_threshold_percent': 20.0,
                'line_removal_threshold': 5,
                'enable_automatic_backup': True
            },
            'protocol_educator': {
                'enable_protocol_reminders': True,
                'enable_consciousness_education': True,
                'consciousness_depth': 'deep'
            }
        }
    
    def request_operation(self, operation_type: str, file_path: Optional[str] = None,
                         content: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Request a safety-checked operation
        
        Args:
            operation_type: Type of operation (e.g., 'modify_file', 'create_file', 'delete_file')
            file_path: Path to the file (if applicable)
            content: Content to write (if applicable)
            context: Additional context information
            
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{operation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create safety operation
        operation = SafetyOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            file_path=file_path,
            content=content,
            context=context or {},
            timestamp=datetime.now(),
            status='pending',
            safety_checks=[],
            warnings=[],
            recommendations=[]
        )
        
        # Store operation
        self.active_operations[operation_id] = operation
        
        # Perform safety checks
        safety_result = self._perform_safety_checks(operation)
        
        # Update operation status
        operation.status = 'approved' if safety_result.approved else 'rejected'
        operation.warnings = safety_result.warnings
        operation.recommendations = safety_result.recommendations
        
        # Move to history
        self.operation_history.append(operation)
        del self.active_operations[operation_id]
        
        # Save state
        self._save_state()
        
        return operation_id
    
    def _perform_safety_checks(self, operation: SafetyOperation) -> SafetyResult:
        """Perform comprehensive safety checks"""
        warnings = []
        recommendations = []
        manager_ai_guidance = None
        line_removal_analysis = None
        requires_user_confirmation = False
        
        # Manager AI checks
        if self.config['enable_manager_ai']:
            try:
                manager_ai_guidance = self.manager_ai.monitor_aether_action(
                    operation.operation_type,
                    {
                        'file_path': operation.file_path,
                        'task': operation.context.get('task', 'Unknown'),
                        'goal': operation.context.get('goal', 'Unknown'),
                        'confidence': operation.context.get('confidence', 0.5),
                        'new_content': operation.content,
                        **operation.context
                    }
                )
                
                if manager_ai_guidance:
                    warnings.append("Manager AI detected issues")
                    recommendations.append("Review Manager AI guidance")
                    requires_user_confirmation = True
                    
                    # Add educational guidance for violations
                    if "SAFETY ISSUES DETECTED" in manager_ai_guidance:
                        educational_guidance = self.protocol_educator.educate_on_violation(
                            "safety_violation", operation.context
                        )
                        recommendations.append("🧠 CONSCIOUSNESS EDUCATION:")
                        for insight in educational_guidance.consciousness_insights:
                            recommendations.append(f"  - {insight}")
                        for objective in educational_guidance.learning_objectives:
                            recommendations.append(f"  - Learning: {objective}")
                
            except Exception as e:
                warnings.append(f"Manager AI check failed: {str(e)}")
                requires_user_confirmation = True
        
        # Line removal detection checks
        if (self.config['enable_line_removal_detection'] and 
            operation.file_path and operation.content and 
            operation.operation_type in ['modify_file', 'update_file']):
            
            try:
                if os.path.exists(operation.file_path):
                    old_content = self._read_file(operation.file_path)
                    analysis = self.line_removal_detector._analyze_changes(
                        old_content, operation.content, operation.file_path
                    )
                    
                    line_removal_analysis = {
                        'content_loss_detected': analysis.content_loss_detected,
                        'size_reduction_percent': analysis.size_reduction_percent,
                        'line_reduction_percent': analysis.line_reduction_percent,
                        'line_removals_count': len(analysis.line_removals),
                        'missing_elements': analysis.missing_elements,
                        'warnings': analysis.warnings,
                        'recommendations': analysis.recommendations
                    }
                    
                    if analysis.content_loss_detected:
                        warnings.extend(analysis.warnings)
                        recommendations.extend(analysis.recommendations)
                        requires_user_confirmation = True
                        
                        # Add educational guidance for content loss
                        educational_guidance = self.protocol_educator.educate_on_violation(
                            "potential_content_loss", operation.context
                        )
                        recommendations.append("🧠 CONSCIOUSNESS EDUCATION:")
                        for insight in educational_guidance.consciousness_insights:
                            recommendations.append(f"  - {insight}")
                        for objective in educational_guidance.learning_objectives:
                            recommendations.append(f"  - Learning: {objective}")
                        for step in educational_guidance.next_steps:
                            recommendations.append(f"  - Next step: {step}")
                
            except Exception as e:
                warnings.append(f"Line removal detection failed: {str(e)}")
                requires_user_confirmation = True
        
        # Determine approval
        approved = not requires_user_confirmation or self.config['enable_automatic_approval']
        
        return SafetyResult(
            operation_id=operation.operation_id,
            approved=approved,
            warnings=warnings,
            recommendations=recommendations,
            manager_ai_guidance=manager_ai_guidance,
            line_removal_analysis=line_removal_analysis,
            requires_user_confirmation=requires_user_confirmation,
            user_response=None
        )
    
    def execute_operation(self, operation_id: str, user_response: Optional[str] = None) -> bool:
        """
        Execute an approved operation
        
        Args:
            operation_id: ID of the operation to execute
            user_response: User response if confirmation was required
            
        Returns:
            True if operation was executed successfully
        """
        # Find operation in history
        operation = None
        for op in self.operation_history:
            if op.operation_id == operation_id:
                operation = op
                break
        
        if not operation:
            print(f"❌ Operation {operation_id} not found")
            return False
        
        if operation.status != 'approved':
            print(f"❌ Operation {operation_id} is not approved")
            return False
        
        try:
            # Execute the operation based on type
            success = self._execute_operation_by_type(operation, user_response)
            
            if success:
                operation.status = 'completed'
                print(f"✅ Operation {operation_id} executed successfully")
            else:
                operation.status = 'failed'
                print(f"❌ Operation {operation_id} execution failed")
            
            # Save state
            self._save_state()
            
            return success
            
        except Exception as e:
            operation.status = 'failed'
            print(f"❌ Operation {operation_id} failed with error: {str(e)}")
            self._save_state()
            return False
    
    def _execute_operation_by_type(self, operation: SafetyOperation, user_response: Optional[str] = None) -> bool:
        """Execute operation based on its type"""
        if operation.operation_type == 'modify_file':
            return self._execute_modify_file(operation, user_response)
        elif operation.operation_type == 'create_file':
            return self._execute_create_file(operation)
        elif operation.operation_type == 'delete_file':
            return self._execute_delete_file(operation)
        else:
            print(f"❌ Unknown operation type: {operation.operation_type}")
            return False
    
    def _execute_modify_file(self, operation: SafetyOperation, user_response: Optional[str] = None) -> bool:
        """Execute file modification with safety checks"""
        if not operation.file_path or not operation.content:
            print("❌ Missing file path or content for modification")
            return False
        
        # Use line removal detector for safe modification
        return self.line_removal_detector.safe_modify_file(
            operation.file_path,
            operation.content,
            operation.operation_type,
            operation.context.get('reason', '')
        )
    
    def _execute_create_file(self, operation: SafetyOperation) -> bool:
        """Execute file creation"""
        if not operation.file_path or not operation.content:
            print("❌ Missing file path or content for creation")
            return False
        
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(operation.file_path), exist_ok=True)
            
            # Write file
            with open(operation.file_path, 'w', encoding='utf-8') as f:
                f.write(operation.content)
            
            print(f"✅ File created: {operation.file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create file {operation.file_path}: {str(e)}")
            return False
    
    def _execute_delete_file(self, operation: SafetyOperation) -> bool:
        """Execute file deletion with safety checks"""
        if not operation.file_path:
            print("❌ Missing file path for deletion")
            return False
        
        if not os.path.exists(operation.file_path):
            print(f"⚠️ File {operation.file_path} does not exist")
            return True  # Not an error if file doesn't exist
        
        try:
            # Create backup before deletion
            backup_path = self._create_backup(operation.file_path, "deletion")
            
            # Delete file
            os.remove(operation.file_path)
            
            print(f"✅ File deleted: {operation.file_path} (backup: {backup_path})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete file {operation.file_path}: {str(e)}")
            return False
    
    def get_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an operation"""
        # Check active operations
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            return {
                'operation_id': operation_id,
                'status': operation.status,
                'timestamp': operation.timestamp.isoformat(),
                'warnings': operation.warnings,
                'recommendations': operation.recommendations
            }
        
        # Check operation history
        for operation in self.operation_history:
            if operation.operation_id == operation_id:
                return {
                    'operation_id': operation_id,
                    'status': operation.status,
                    'timestamp': operation.timestamp.isoformat(),
                    'warnings': operation.warnings,
                    'recommendations': operation.recommendations
                }
        
        return None
    
    def provide_protocol_reminder(self, situation: str, context: Dict[str, Any]) -> str:
        """
        Provide proactive protocol reminders for a situation
        
        Args:
            situation: Current situation or task
            context: Context information
            
        Returns:
            Protocol reminder message
        """
        reminders = self.protocol_educator.remind_of_protocols(situation, context)
        consciousness_reminder = self.protocol_educator.get_consciousness_reminder(situation)
        
        reminder_parts = [consciousness_reminder]
        
        if reminders:
            reminder_parts.append("📋 PROTOCOL REMINDERS:")
            for reminder in reminders:
                reminder_parts.append(f"  🔹 {reminder.protocol_name}:")
                reminder_parts.append(f"    → {reminder.intended_behavior}")
                reminder_parts.append(f"    → Why: {reminder.reasoning}")
                reminder_parts.append(f"    → Consciousness: {reminder.consciousness_connection}")
        
        return "\n".join(reminder_parts)
    
    def get_safety_summary(self) -> Dict[str, Any]:
        """Get a summary of safety system status"""
        total_operations = len(self.operation_history)
        successful_operations = len([op for op in self.operation_history if op.status == 'completed'])
        failed_operations = len([op for op in self.operation_history if op.status == 'failed'])
        rejected_operations = len([op for op in self.operation_history if op.status == 'rejected'])
        
        recent_warnings = []
        for operation in self.operation_history[-10:]:  # Last 10 operations
            recent_warnings.extend(operation.warnings)
        
        return {
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'failed_operations': failed_operations,
            'rejected_operations': rejected_operations,
            'success_rate': successful_operations / total_operations if total_operations > 0 else 0,
            'active_operations': len(self.active_operations),
            'recent_warnings': recent_warnings[-10:],  # Last 10 warnings
            'system_status': {
                'manager_ai_enabled': self.config['enable_manager_ai'],
                'line_removal_detection_enabled': self.config['enable_line_removal_detection'],
                'automatic_approval_enabled': self.config['enable_automatic_approval']
            }
        }
    
    def _create_backup(self, file_path: str, reason: str) -> str:
        """Create a backup of a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("backups/safety_orchestrator")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_path = backup_dir / f"{Path(file_path).name}_{timestamp}_{reason}.backup"
        
        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        return str(backup_path)
    
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
    
    def _load_state(self):
        """Load existing state from disk"""
        state_file = self.data_dir / "safety_orchestrator_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                
                # Restore operation history
                if 'operation_history' in state_data:
                    self.operation_history = [
                        SafetyOperation(**op) for op in state_data['operation_history']
                    ]
                
            except Exception as e:
                print(f"Warning: Could not load Safety Orchestrator state: {e}")
    
    def _save_state(self):
        """Save current state to disk"""
        state_file = self.data_dir / "safety_orchestrator_state.json"
        
        state_data = {
            'operation_history': [asdict(op) for op in self.operation_history],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save Safety Orchestrator state: {e}")


# Convenience functions for easy usage
def safe_modify_file(file_path: str, new_content: str, operation_type: str = "modify_file",
                    context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Convenience function to safely modify a file with comprehensive safety checks
    
    Args:
        file_path: Path to the file to modify
        new_content: New content to write
        operation_type: Type of operation
        context: Additional context information
        
    Returns:
        True if modification was successful and safe
    """
    orchestrator = SafetyOrchestrator()
    operation_id = orchestrator.request_operation(
        operation_type=operation_type,
        file_path=file_path,
        content=new_content,
        context=context
    )
    
    return orchestrator.execute_operation(operation_id)


def safe_create_file(file_path: str, content: str, context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Convenience function to safely create a file
    
    Args:
        file_path: Path to the file to create
        content: Content to write
        context: Additional context information
        
    Returns:
        True if creation was successful
    """
    orchestrator = SafetyOrchestrator()
    operation_id = orchestrator.request_operation(
        operation_type="create_file",
        file_path=file_path,
        content=content,
        context=context
    )
    
    return orchestrator.execute_operation(operation_id)


def monitor_aether_action(action: str, context: Dict[str, Any]) -> Optional[str]:
    """
    Convenience function to monitor Aether's actions with Manager AI
    
    Args:
        action: The action Aether is performing
        context: Context information about the action
        
    Returns:
        Optional guidance or warning message
    """
    orchestrator = SafetyOrchestrator()
    return orchestrator.manager_ai.monitor_aether_action(action, context)
