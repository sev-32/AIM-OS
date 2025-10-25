"""
Automated Line Removal Detection System

This system provides comprehensive protection against accidental content loss
by detecting when lines are removed and alerting users before proceeding.
"""

import os
import hashlib
import json
import shutil
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LineRemoval:
    """Represents a removed line with context"""
    line_number: int
    content: str
    context: str
    importance: float
    type: str  # 'code', 'text', 'header', 'link', etc.


@dataclass
class ContentAnalysis:
    """Results of content analysis"""
    file_path: str
    old_size: int
    new_size: int
    size_reduction: int
    size_reduction_percent: float
    old_lines: int
    new_lines: int
    line_reduction: int
    line_reduction_percent: float
    line_removals: List[LineRemoval]
    missing_elements: List[str]
    content_loss_detected: bool
    warnings: List[str]
    recommendations: List[str]


class LineRemovalDetector:
    """Main class for detecting line removals and content loss"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.snapshots_dir = Path("snapshots/pre_edit")
        self.backups_dir = Path("backups/automated")
        self.logs_dir = Path("logs/line_removal")
        
        # Create directories
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def _default_config(self) -> Dict:
        """Default configuration for the detector"""
        return {
            'size_reduction_threshold_percent': 20.0,
            'line_removal_threshold': 5,
            'line_removal_threshold_percent': 20.0,
            'importance_threshold': 0.7,
            'important_removal_count': 3,
            'backup_large_files_threshold': 100000,  # 100KB
            'enable_automatic_backup': True,
            'enable_snapshots': True,
            'enable_logging': True
        }
    
    def safe_modify_file(self, file_path: str, new_content: str, operation: str, reason: str = "") -> bool:
        """
        Safely modify a file with full line removal detection and safety protocols
        
        Args:
            file_path: Path to the file to modify
            new_content: New content to write
            operation: Type of operation (e.g., 'update', 'create', 'reorganize')
            reason: Reason for the modification
            
        Returns:
            bool: True if modification was successful and safe, False otherwise
        """
        try:
            # Step 1: Capture pre-edit snapshot
            snapshot_id = None
            if self.config['enable_snapshots'] and os.path.exists(file_path):
                snapshot_id = self._capture_snapshot(file_path, operation)
            
            # Step 2: Create backup if needed
            backup_id = None
            if self.config['enable_automatic_backup'] and os.path.exists(file_path):
                backup_id = self._create_backup(file_path, operation, reason)
            
            # Step 3: Analyze changes if file exists
            analysis = None
            if os.path.exists(file_path):
                old_content = self._read_file(file_path)
                analysis = self._analyze_changes(old_content, new_content, file_path)
                
                # Step 4: Check for content loss and generate alerts
                if analysis.content_loss_detected:
                    response = self._generate_content_loss_alert(analysis, operation)
                    if response == "no":
                        self._log_operation(file_path, operation, "CANCELLED", "User cancelled due to content loss")
                        return False
                    elif response == "merge":
                        new_content = self._merge_content(old_content, new_content)
                        analysis = self._analyze_changes(old_content, new_content, file_path)
                    elif response == "backup":
                        if not backup_id:
                            backup_id = self._create_backup(file_path, operation, "User requested backup")
            
            # Step 5: Proceed with modification
            self._write_file(file_path, new_content)
            
            # Step 6: Log the operation
            self._log_operation(file_path, operation, "SUCCESS", reason, analysis, snapshot_id, backup_id)
            
            # Step 7: Verify the modification
            if not self._verify_modification(file_path, new_content):
                self._log_operation(file_path, operation, "VERIFICATION_FAILED", "File verification failed")
                return False
            
            print(f"✅ File {file_path} safely modified")
            return True
            
        except Exception as e:
            self._log_operation(file_path, operation, "ERROR", f"Exception: {str(e)}")
            print(f"❌ Error modifying file {file_path}: {str(e)}")
            return False
    
    def _capture_snapshot(self, file_path: str, operation: str) -> str:
        """Capture a snapshot of the file before modification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        snapshot_id = f"{operation}_{timestamp}"
        
        snapshot_path = self.snapshots_dir / snapshot_id
        snapshot_path.mkdir(parents=True, exist_ok=True)
        
        content = self._read_file(file_path)
        snapshot_file = snapshot_path / Path(file_path).name
        
        self._write_file(str(snapshot_file), content)
        
        # Create metadata
        metadata = {
            'snapshot_id': snapshot_id,
            'timestamp': timestamp,
            'file_path': file_path,
            'operation': operation,
            'file_size': len(content),
            'content_hash': hashlib.sha256(content.encode()).hexdigest(),
            'line_count': len(content.splitlines()),
            'snapshot_path': str(snapshot_file)
        }
        
        metadata_file = snapshot_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"📸 Pre-edit snapshot captured: {snapshot_id}")
        return snapshot_id
    
    def _create_backup(self, file_path: str, operation: str, reason: str) -> str:
        """Create a backup of the file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"{operation}_{timestamp}"
        
        backup_path = self.backups_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)
        
        content = self._read_file(file_path)
        backup_file = backup_path / Path(file_path).name
        
        self._write_file(str(backup_file), content)
        
        # Create metadata
        metadata = {
            'backup_id': backup_id,
            'timestamp': timestamp,
            'file_path': file_path,
            'operation': operation,
            'reason': reason,
            'file_size': len(content),
            'content_hash': hashlib.sha256(content.encode()).hexdigest(),
            'backup_path': str(backup_file)
        }
        
        metadata_file = backup_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Compress if large
        if len(content) > self.config['backup_large_files_threshold']:
            compressed_file = self._compress_file(str(backup_file))
            metadata['compressed_path'] = compressed_file
        
        print(f"💾 Backup created: {backup_id}")
        return backup_id
    
    def _analyze_changes(self, old_content: str, new_content: str, file_path: str) -> ContentAnalysis:
        """Analyze changes between old and new content"""
        old_size = len(old_content)
        new_size = len(new_content)
        size_reduction = old_size - new_size
        size_reduction_percent = (size_reduction / old_size) * 100 if old_size > 0 else 0
        
        old_lines = len(old_content.splitlines())
        new_lines = len(new_content.splitlines())
        line_reduction = old_lines - new_lines
        line_reduction_percent = (line_reduction / old_lines) * 100 if old_lines > 0 else 0
        
        # Detect line removals
        line_removals = self._detect_line_removals(old_content, new_content)
        
        # Detect missing elements
        missing_elements = self._detect_missing_elements(old_content, new_content)
        
        # Determine if content loss is detected
        content_loss_detected = self._is_content_loss_detected(
            size_reduction_percent, line_reduction_percent, line_removals, missing_elements
        )
        
        # Generate warnings
        warnings = self._generate_warnings(size_reduction_percent, line_reduction_percent, line_removals, missing_elements)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(content_loss_detected, warnings)
        
        return ContentAnalysis(
            file_path=file_path,
            old_size=old_size,
            new_size=new_size,
            size_reduction=size_reduction,
            size_reduction_percent=size_reduction_percent,
            old_lines=old_lines,
            new_lines=new_lines,
            line_reduction=line_reduction,
            line_reduction_percent=line_reduction_percent,
            line_removals=line_removals,
            missing_elements=missing_elements,
            content_loss_detected=content_loss_detected,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def _detect_line_removals(self, old_content: str, new_content: str) -> List[LineRemoval]:
        """Detect specific lines that were removed"""
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        line_removals = []
        
        # Simple diff algorithm to find removed lines
        old_set = set(old_lines)
        new_set = set(new_lines)
        removed_lines = old_set - new_set
        
        for removed_line in removed_lines:
            # Find line number in original content
            for i, line in enumerate(old_lines):
                if line == removed_line:
                    line_removals.append(LineRemoval(
                        line_number=i + 1,
                        content=removed_line,
                        context=self._get_line_context(old_lines, i),
                        importance=self._calculate_line_importance(removed_line),
                        type=self._classify_line_type(removed_line)
                    ))
                    break
        
        return line_removals
    
    def _detect_missing_elements(self, old_content: str, new_content: str) -> List[str]:
        """Detect key elements that might be missing"""
        missing_elements = []
        
        # Check for code blocks
        if '```' in old_content and '```' not in new_content:
            missing_elements.append("Code blocks")
        
        # Check for specific patterns
        patterns = [
            (r'```python', "Python code blocks"),
            (r'```bash', "Bash code blocks"),
            (r'```yaml', "YAML code blocks"),
            (r'```json', "JSON code blocks"),
            (r'^#+ ', "Header sections"),
            (r'\*\*.*\*\*', "Bold text"),
            (r'\*.*\*', "Italic text"),
            (r'http[s]?://', "URLs/links"),
            (r'/[a-zA-Z0-9_/.-]+', "File paths")
        ]
        
        for pattern, description in patterns:
            if re.search(pattern, old_content, re.MULTILINE) and not re.search(pattern, new_content, re.MULTILINE):
                missing_elements.append(description)
        
        return missing_elements
    
    def _is_content_loss_detected(self, size_reduction_percent: float, line_reduction_percent: float, 
                                 line_removals: List[LineRemoval], missing_elements: List[str]) -> bool:
        """Determine if content loss is detected based on thresholds"""
        
        # Check size reduction threshold
        if size_reduction_percent > self.config['size_reduction_threshold_percent']:
            return True
        
        # Check line reduction threshold
        if line_reduction_percent > self.config['line_removal_threshold_percent']:
            return True
        
        # Check number of removed lines
        if len(line_removals) > self.config['line_removal_threshold']:
            return True
        
        # Check for important removals
        important_removals = [r for r in line_removals if r.importance > self.config['importance_threshold']]
        if len(important_removals) > self.config['important_removal_count']:
            return True
        
        # Check for missing key elements
        if missing_elements:
            return True
        
        return False
    
    def _generate_warnings(self, size_reduction_percent: float, line_reduction_percent: float,
                          line_removals: List[LineRemoval], missing_elements: List[str]) -> List[str]:
        """Generate warnings based on detected issues"""
        warnings = []
        
        if size_reduction_percent > self.config['size_reduction_threshold_percent']:
            warnings.append(f"Size reduction: {size_reduction_percent:.1f}%")
        
        if line_reduction_percent > self.config['line_removal_threshold_percent']:
            warnings.append(f"Line reduction: {line_reduction_percent:.1f}%")
        
        if len(line_removals) > self.config['line_removal_threshold']:
            warnings.append(f"Line removals: {len(line_removals)} lines")
        
        important_removals = [r for r in line_removals if r.importance > self.config['importance_threshold']]
        if important_removals:
            warnings.append(f"Important removals: {len(important_removals)} lines")
        
        if missing_elements:
            warnings.append(f"Missing elements: {', '.join(missing_elements)}")
        
        return warnings
    
    def _generate_recommendations(self, content_loss_detected: bool, warnings: List[str]) -> List[str]:
        """Generate recommendations based on detected issues"""
        recommendations = []
        
        if content_loss_detected:
            recommendations.append("Consider creating a backup before proceeding")
            recommendations.append("Review removed content to ensure nothing important is lost")
            recommendations.append("Consider merging content instead of replacing")
        
        if warnings:
            recommendations.append("Verify that all changes are intentional")
            recommendations.append("Check if removed content should be preserved elsewhere")
        
        return recommendations
    
    def _generate_content_loss_alert(self, analysis: ContentAnalysis, operation: str) -> str:
        """Generate alert for content loss and get user response"""
        print(f"🚨 ALERT: Potential content loss in {analysis.file_path}")
        print(f"📊 Analysis Results:")
        print(f"  - Size reduction: {analysis.size_reduction} characters ({analysis.size_reduction_percent:.1f}%)")
        print(f"  - Line reduction: {analysis.line_reduction} lines ({analysis.line_reduction_percent:.1f}%)")
        
        if analysis.line_removals:
            print(f"  - Removed lines: {len(analysis.line_removals)}")
            print("  - Removed content preview:")
            for i, removal in enumerate(analysis.line_removals[:5]):
                print(f"    {i+1}. Line {removal.line_number}: {removal.content[:80]}...")
            if len(analysis.line_removals) > 5:
                print(f"    ... and {len(analysis.line_removals) - 5} more lines")
        
        if analysis.missing_elements:
            print(f"  - Missing elements: {', '.join(analysis.missing_elements)}")
        
        if analysis.warnings:
            print("  - Warnings:")
            for warning in analysis.warnings:
                print(f"    - {warning}")
        
        if analysis.recommendations:
            print("  - Recommendations:")
            for rec in analysis.recommendations:
                print(f"    - {rec}")
        
        print("\n🤔 What would you like to do?")
        print("  yes    - Proceed with the modification")
        print("  no     - Cancel the operation")
        print("  merge  - Merge old and new content")
        print("  backup - Create backup and proceed")
        
        while True:
            response = input("Enter your choice (yes/no/merge/backup): ").lower().strip()
            if response in ['yes', 'no', 'merge', 'backup']:
                return response
            print("Invalid choice. Please enter yes, no, merge, or backup.")
    
    def _merge_content(self, old_content: str, new_content: str) -> str:
        """Merge old and new content intelligently"""
        # Simple merge strategy - append new content to old content with separator
        merged_content = old_content + "\n\n" + "="*50 + "\n"
        merged_content += f"# New Content Added at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        merged_content += "="*50 + "\n\n" + new_content
        
        return merged_content
    
    def _get_line_context(self, lines: List[str], line_index: int, context_size: int = 2) -> str:
        """Get context around a line"""
        start = max(0, line_index - context_size)
        end = min(len(lines), line_index + context_size + 1)
        context_lines = lines[start:end]
        
        context = []
        for i, line in enumerate(context_lines):
            line_num = start + i + 1
            marker = ">>> " if line_num == line_index + 1 else "    "
            context.append(f"{marker}{line_num:4d}: {line}")
        
        return "\n".join(context)
    
    def _calculate_line_importance(self, line: str) -> float:
        """Calculate importance score for a line"""
        importance = 0.0
        
        # Code blocks are very important
        if '```' in line:
            importance += 0.8
        
        # Headers are important
        if line.strip().startswith('#'):
            importance += 0.7
        
        # URLs and links are important
        if 'http' in line or 'www.' in line:
            importance += 0.6
        
        # File paths are important
        if '/' in line and ('.' in line or '\\' in line):
            importance += 0.5
        
        # Bold or italic text is important
        if '**' in line or '*' in line:
            importance += 0.4
        
        # Long lines are more likely to be important
        if len(line.strip()) > 50:
            importance += 0.2
        
        # Non-empty lines have base importance
        if line.strip():
            importance += 0.1
        
        return min(importance, 1.0)
    
    def _classify_line_type(self, line: str) -> str:
        """Classify the type of a line"""
        line = line.strip()
        
        if line.startswith('#'):
            return 'header'
        elif line.startswith('```'):
            return 'code_block'
        elif line.startswith('-') or line.startswith('*'):
            return 'list_item'
        elif 'http' in line or 'www.' in line:
            return 'link'
        elif '/' in line and ('.' in line or '\\' in line):
            return 'file_path'
        elif '**' in line or '*' in line:
            return 'formatted_text'
        elif not line:
            return 'empty'
        else:
            return 'text'
    
    def _read_file(self, file_path: str) -> str:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _write_file(self, file_path: str, content: str):
        """Write file content safely"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _verify_modification(self, file_path: str, expected_content: str) -> bool:
        """Verify that the modification was successful"""
        try:
            actual_content = self._read_file(file_path)
            return actual_content == expected_content
        except Exception:
            return False
    
    def _compress_file(self, file_path: str) -> str:
        """Compress a file to save space"""
        import gzip
        compressed_path = file_path + '.gz'
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return compressed_path
    
    def _log_operation(self, file_path: str, operation: str, status: str, reason: str, 
                      analysis: Optional[ContentAnalysis] = None, snapshot_id: Optional[str] = None,
                      backup_id: Optional[str] = None):
        """Log the operation for audit trail"""
        if not self.config['enable_logging']:
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'operation': operation,
            'status': status,
            'reason': reason,
            'snapshot_id': snapshot_id,
            'backup_id': backup_id
        }
        
        if analysis:
            log_entry['analysis'] = {
                'size_reduction_percent': analysis.size_reduction_percent,
                'line_reduction_percent': analysis.line_reduction_percent,
                'line_removals_count': len(analysis.line_removals),
                'missing_elements': analysis.missing_elements,
                'content_loss_detected': analysis.content_loss_detected
            }
        
        log_file = self.logs_dir / f"operations_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


# Convenience function for easy usage
def safe_modify_file(file_path: str, new_content: str, operation: str = "modify", reason: str = "") -> bool:
    """
    Convenience function to safely modify a file with line removal detection
    
    Args:
        file_path: Path to the file to modify
        new_content: New content to write
        operation: Type of operation (e.g., 'update', 'create', 'reorganize')
        reason: Reason for the modification
        
    Returns:
        bool: True if modification was successful and safe, False otherwise
    """
    detector = LineRemovalDetector()
    return detector.safe_modify_file(file_path, new_content, operation, reason)
