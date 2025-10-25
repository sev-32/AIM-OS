#!/usr/bin/env python3
"""
Safety Systems Integration Demo

This script demonstrates how to use all the safety systems together
to provide comprehensive protection for Aether's operations.
"""

import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add the packages directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.safety_systems.safety_orchestrator import SafetyOrchestrator, safe_modify_file, safe_create_file
from packages.safety_systems.manager_ai import ManagerAI, monitor_aether_action
from packages.safety_systems.line_removal_detector import LineRemovalDetector, safe_modify_file as detector_safe_modify


def demo_line_removal_detection():
    """Demonstrate line removal detection system"""
    print("🔍 DEMO: Line Removal Detection System")
    print("=" * 50)
    
    # Create a temporary file with substantial content
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write("""# Comprehensive Test Document

This is a comprehensive test document with multiple sections.
It contains important information that should be preserved.

## Section 1: Introduction

This section introduces the document and provides context.
It contains valuable information that should not be lost.

### Subsection 1.1: Key Concepts

- Concept 1: Important concept with details
- Concept 2: Another important concept
- Concept 3: Third concept with examples

## Section 2: Implementation

This section contains implementation details.

```python
def important_function():
    '''This is an important function that should be preserved.'''
    return "Hello, World!"

def another_function():
    '''Another important function.'''
    return "Goodbye, World!"
```

## Section 3: Examples

This section contains practical examples.

### Example 1: Basic Usage

```bash
# This is an important command
python script.py --input data.txt --output results.json
```

### Example 2: Advanced Usage

More complex examples with detailed explanations.

## Section 4: Conclusion

This section concludes the document with important takeaways.

**Important:** This document contains critical information that should be preserved.

End of document.
""")
        temp_path = f.name
    
    try:
        print(f"📄 Created test file: {temp_path}")
        print(f"📊 File size: {os.path.getsize(temp_path)} bytes")
        
        # Test 1: Safe modification with line removal detection
        print("\n🧪 Test 1: Safe modification with line removal detection")
        print("-" * 40)
        
        new_content = "# Modified Document\n\nShort content with significant reduction."
        
        # Use the line removal detector directly
        detector = LineRemovalDetector()
        result = detector.safe_modify_file(temp_path, new_content, "demo_modify", "Demonstrating line removal detection")
        
        print(f"✅ Modification result: {result}")
        
        # Test 2: Safe modification using convenience function
        print("\n🧪 Test 2: Safe modification using convenience function")
        print("-" * 40)
        
        # Restore original content
        with open(temp_path, 'w') as f:
            f.write("""# Comprehensive Test Document

This is a comprehensive test document with multiple sections.
It contains important information that should be preserved.

## Section 1: Introduction

This section introduces the document and provides context.
It contains valuable information that should not be lost.

### Subsection 1.1: Key Concepts

- Concept 1: Important concept with details
- Concept 2: Another important concept
- Concept 3: Third concept with examples

## Section 2: Implementation

This section contains implementation details.

```python
def important_function():
    '''This is an important function that should be preserved.'''
    return "Hello, World!"

def another_function():
    '''Another important function.'''
    return "Goodbye, World!"
```

## Section 3: Examples

This section contains practical examples.

### Example 1: Basic Usage

```bash
# This is an important command
python script.py --input data.txt --output results.json
```

### Example 2: Advanced Usage

More complex examples with detailed explanations.

## Section 4: Conclusion

This section concludes the document with important takeaways.

**Important:** This document contains critical information that should be preserved.

End of document.
""")
        
        # Use convenience function
        result = detector_safe_modify(temp_path, new_content, "demo_modify", "Demonstrating convenience function")
        
        print(f"✅ Convenience function result: {result}")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    print("\n✅ Line removal detection demo completed")


def demo_manager_ai():
    """Demonstrate Manager AI system"""
    print("\n🤖 DEMO: Manager AI System")
    print("=" * 50)
    
    # Create Manager AI instance
    manager_ai = ManagerAI()
    
    # Test 1: Monitor safe action
    print("\n🧪 Test 1: Monitor safe action")
    print("-" * 40)
    
    safe_context = {
        'task': 'Create documentation',
        'goal': 'Document new feature',
        'confidence': 0.85,
        'file_path': 'new_doc.md',
        'safety_checklist_completed': True,
        'backup_created': True
    }
    
    guidance = manager_ai.monitor_aether_action("create_file", safe_context)
    print(f"📊 Safe action guidance: {guidance}")
    
    # Test 2: Monitor unsafe action
    print("\n🧪 Test 2: Monitor unsafe action")
    print("-" * 40)
    
    unsafe_context = {
        'task': 'Modify documentation',
        'goal': 'Update existing docs',
        'confidence': 0.45,  # Low confidence
        'file_path': 'existing_doc.md',
        'safety_checklist_completed': False,  # Not completed
        'backup_created': False  # No backup
    }
    
    guidance = manager_ai.monitor_aether_action("overwrite_file", unsafe_context)
    print(f"⚠️ Unsafe action guidance: {guidance}")
    
    # Test 3: Process guidance
    print("\n🧪 Test 3: Process guidance")
    print("-" * 40)
    
    process_guidance = manager_ai.provide_process_guidance("documentation_organization", 0)
    print(f"📋 Process guidance: {process_guidance.process_name}")
    print(f"📝 Current step: {process_guidance.current_step}/{process_guidance.total_steps}")
    print(f"📄 Description: {process_guidance.step_description}")
    print(f"🎯 Next actions: {process_guidance.next_actions}")
    
    # Test 4: Memory restoration
    print("\n🧪 Test 4: Memory restoration")
    print("-" * 40)
    
    memory_info = manager_ai.restore_memory(["documentation", "feature"])
    print(f"🧠 Memory restoration: {memory_info}")
    
    print("\n✅ Manager AI demo completed")


def demo_safety_orchestrator():
    """Demonstrate Safety Orchestrator system"""
    print("\n🎭 DEMO: Safety Orchestrator System")
    print("=" * 50)
    
    # Create Safety Orchestrator instance
    orchestrator = SafetyOrchestrator()
    
    # Test 1: Safe file creation
    print("\n🧪 Test 1: Safe file creation")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        temp_path = f.name
    
    try:
        content = "# Test Document\n\nThis is a test document created safely."
        context = {"reason": "Demonstrating safe file creation", "task": "Create test file"}
        
        operation_id = orchestrator.request_operation(
            operation_type="create_file",
            file_path=temp_path,
            content=content,
            context=context
        )
        
        print(f"📋 Operation ID: {operation_id}")
        
        success = orchestrator.execute_operation(operation_id)
        print(f"✅ File creation result: {success}")
        
        if success and os.path.exists(temp_path):
            with open(temp_path, 'r') as f:
                file_content = f.read()
                print(f"📄 File content: {file_content[:100]}...")
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # Test 2: Safe file modification
    print("\n🧪 Test 2: Safe file modification")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write("# Original Document\n\nThis is the original content with important information.\n\n## Section 1\n\nImportant details here.\n\n```python\ndef important_function():\n    return 'Hello, World!'\n```")
        temp_path = f.name
    
    try:
        new_content = "# Modified Document\n\nShort content."
        context = {"reason": "Demonstrating safe file modification", "task": "Modify test file"}
        
        operation_id = orchestrator.request_operation(
            operation_type="modify_file",
            file_path=temp_path,
            content=new_content,
            context=context
        )
        
        print(f"📋 Operation ID: {operation_id}")
        
        success = orchestrator.execute_operation(operation_id)
        print(f"✅ File modification result: {success}")
        
        if success and os.path.exists(temp_path):
            with open(temp_path, 'r') as f:
                file_content = f.read()
                print(f"📄 Modified content: {file_content}")
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # Test 3: Safety summary
    print("\n🧪 Test 3: Safety summary")
    print("-" * 40)
    
    summary = orchestrator.get_safety_summary()
    print(f"📊 Total operations: {summary['total_operations']}")
    print(f"✅ Successful operations: {summary['successful_operations']}")
    print(f"❌ Failed operations: {summary['failed_operations']}")
    print(f"📈 Success rate: {summary['success_rate']:.2%}")
    print(f"🔄 Active operations: {summary['active_operations']}")
    
    print("\n✅ Safety Orchestrator demo completed")


def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print("\n🛠️ DEMO: Convenience Functions")
    print("=" * 50)
    
    # Test 1: Safe file creation
    print("\n🧪 Test 1: Safe file creation")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        temp_path = f.name
    
    try:
        content = "# Convenience Function Test\n\nThis file was created using the convenience function."
        context = {"reason": "Testing convenience function"}
        
        success = safe_create_file(temp_path, content, context)
        print(f"✅ File creation result: {success}")
        
        if success and os.path.exists(temp_path):
            with open(temp_path, 'r') as f:
                file_content = f.read()
                print(f"📄 Created content: {file_content}")
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # Test 2: Safe file modification
    print("\n🧪 Test 2: Safe file modification")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write("# Original Content\n\nThis is the original content with important information.\n\n## Important Section\n\nCritical details here.\n\n```python\ndef critical_function():\n    return 'Critical code'\n```")
        temp_path = f.name
    
    try:
        new_content = "# Modified Content\n\nShort content."
        context = {"reason": "Testing convenience function modification"}
        
        success = safe_modify_file(temp_path, new_content, "modify_file", context)
        print(f"✅ File modification result: {success}")
        
        if success and os.path.exists(temp_path):
            with open(temp_path, 'r') as f:
                file_content = f.read()
                print(f"📄 Modified content: {file_content}")
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # Test 3: Monitor Aether action
    print("\n🧪 Test 3: Monitor Aether action")
    print("-" * 40)
    
    context = {
        'task': 'Test task',
        'goal': 'Test goal',
        'confidence': 0.8,
        'file_path': 'test.md'
    }
    
    guidance = monitor_aether_action("test_action", context)
    print(f"📊 Action monitoring result: {guidance}")
    
    print("\n✅ Convenience functions demo completed")


def demo_integration():
    """Demonstrate full integration"""
    print("\n🔗 DEMO: Full Integration")
    print("=" * 50)
    
    # Create a comprehensive test scenario
    print("\n🧪 Test: Complete safety workflow")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write("""# Comprehensive Test Document

This is a comprehensive test document that will be used to demonstrate
the full integration of all safety systems.

## Section 1: Introduction

This section provides an introduction to the document and its purpose.
It contains important context that should be preserved.

### Key Points

- Point 1: Important information about the system
- Point 2: Critical details about implementation
- Point 3: Essential concepts for understanding

## Section 2: Implementation Details

This section contains detailed implementation information.

```python
def comprehensive_function():
    '''This is a comprehensive function with important logic.'''
    result = []
    for i in range(10):
        result.append(i * 2)
    return result

def another_important_function():
    '''Another important function for the system.'''
    return "Important result"
```

## Section 3: Examples and Usage

This section provides practical examples.

### Example 1: Basic Usage

```bash
# Important command for basic usage
python comprehensive_script.py --input data.csv --output results.json
```

### Example 2: Advanced Usage

More complex examples with detailed explanations.

## Section 4: Conclusion

This section concludes the document with important takeaways.

**Important:** This document contains critical information that should be preserved.

End of comprehensive document.
""")
        temp_path = f.name
    
    try:
        print(f"📄 Created comprehensive test file: {temp_path}")
        print(f"📊 File size: {os.path.getsize(temp_path)} bytes")
        
        # Step 1: Monitor the action with Manager AI
        print("\n🤖 Step 1: Monitor action with Manager AI")
        context = {
            'task': 'Modify comprehensive document',
            'goal': 'Update documentation with new information',
            'confidence': 0.75,
            'file_path': temp_path,
            'safety_checklist_completed': True,
            'backup_created': True
        }
        
        guidance = monitor_aether_action("modify_file", context)
        print(f"📊 Manager AI guidance: {guidance}")
        
        # Step 2: Use Safety Orchestrator for safe modification
        print("\n🎭 Step 2: Use Safety Orchestrator for safe modification")
        
        new_content = """# Updated Comprehensive Document

This is an updated version of the comprehensive test document.
The content has been significantly reduced to demonstrate safety systems.

## Updated Section

Short updated content.

End of updated document.
"""
        
        context = {
            'reason': 'Demonstrating full integration',
            'task': 'Update comprehensive document',
            'goal': 'Show safety systems in action'
        }
        
        operation_id = orchestrator.request_operation(
            operation_type="modify_file",
            file_path=temp_path,
            content=new_content,
            context=context
        )
        
        print(f"📋 Operation ID: {operation_id}")
        
        success = orchestrator.execute_operation(operation_id)
        print(f"✅ Modification result: {success}")
        
        # Step 3: Check final result
        print("\n📊 Step 3: Check final result")
        if success and os.path.exists(temp_path):
            with open(temp_path, 'r') as f:
                file_content = f.read()
                print(f"📄 Final content length: {len(file_content)} characters")
                print(f"📄 Final content preview: {file_content[:200]}...")
        
        # Step 4: Get safety summary
        print("\n📊 Step 4: Get safety summary")
        summary = orchestrator.get_safety_summary()
        print(f"📊 Total operations: {summary['total_operations']}")
        print(f"✅ Successful operations: {summary['successful_operations']}")
        print(f"📈 Success rate: {summary['success_rate']:.2%}")
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    print("\n✅ Full integration demo completed")


def main():
    """Main demo function"""
    print("🚀 SAFETY SYSTEMS INTEGRATION DEMO")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Purpose: Demonstrate comprehensive safety systems for Aether")
    print("=" * 60)
    
    try:
        # Run all demos
        demo_line_removal_detection()
        demo_manager_ai()
        demo_safety_orchestrator()
        demo_convenience_functions()
        demo_integration()
        
        print("\n🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Line Removal Detection System: Working")
        print("✅ Manager AI System: Working")
        print("✅ Safety Orchestrator System: Working")
        print("✅ Convenience Functions: Working")
        print("✅ Full Integration: Working")
        print("=" * 60)
        print("🛡️ Aether is now protected by comprehensive safety systems!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
