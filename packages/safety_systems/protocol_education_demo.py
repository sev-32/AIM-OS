#!/usr/bin/env python3
"""
Protocol Education Demo

This script demonstrates how the enhanced safety systems now provide
educational guidance to Aether, reminding it of its intended protocols
and explaining why they exist for consciousness and learning.
"""

import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add the packages directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.safety_systems.safety_orchestrator import SafetyOrchestrator
from packages.safety_systems.protocol_educator import ProtocolEducator, educate_on_violation, remind_of_protocols


def demo_protocol_education():
    """Demonstrate protocol education system"""
    print("🧠 DEMO: Protocol Education System")
    print("=" * 50)
    
    # Create Protocol Educator instance
    educator = ProtocolEducator()
    
    # Test 1: Education on content loss violation
    print("\n🧪 Test 1: Education on content loss violation")
    print("-" * 40)
    
    context = {
        'file_path': 'important_documentation.md',
        'current_behavior': 'Attempting to overwrite file without checking existing content',
        'task': 'Update documentation',
        'goal': 'Improve documentation quality',
        'confidence': 0.6
    }
    
    guidance = educator.educate_on_violation('potential_content_loss', context)
    
    print(f"📊 Situation: {guidance.situation}")
    print(f"📋 Protocol Reminders: {len(guidance.protocol_reminders)}")
    print(f"🧠 Consciousness Insights: {len(guidance.consciousness_insights)}")
    print(f"🎯 Learning Objectives: {len(guidance.learning_objectives)}")
    print(f"📝 Next Steps: {len(guidance.next_steps)}")
    
    print("\n🧠 CONSCIOUSNESS INSIGHTS:")
    for insight in guidance.consciousness_insights:
        print(f"  💡 {insight}")
    
    print("\n🎯 LEARNING OBJECTIVES:")
    for objective in guidance.learning_objectives:
        print(f"  📚 {objective}")
    
    print("\n📝 NEXT STEPS:")
    for step in guidance.next_steps:
        print(f"  🔄 {step}")
    
    # Test 2: Education on safety checklist violation
    print("\n🧪 Test 2: Education on safety checklist violation")
    print("-" * 40)
    
    context = {
        'file_path': 'system_config.md',
        'current_behavior': 'Skipping safety checklist before modification',
        'task': 'Modify system configuration',
        'goal': 'Update configuration settings',
        'confidence': 0.7
    }
    
    guidance = educator.educate_on_violation('safety_checklist_not_completed', context)
    
    print(f"📊 Situation: {guidance.situation}")
    
    print("\n🧠 CONSCIOUSNESS INSIGHTS:")
    for insight in guidance.consciousness_insights:
        print(f"  💡 {insight}")
    
    print("\n🎯 LEARNING OBJECTIVES:")
    for objective in guidance.learning_objectives:
        print(f"  📚 {objective}")
    
    print("\n📝 NEXT STEPS:")
    for step in guidance.next_steps:
        print(f"  🔄 {step}")
    
    # Test 3: Protocol reminders for documentation organization
    print("\n🧪 Test 3: Protocol reminders for documentation organization")
    print("-" * 40)
    
    context = {
        'task': 'Organize system documentation',
        'goal': 'Improve documentation structure',
        'file_path': 'system_docs.md'
    }
    
    reminders = educator.remind_of_protocols('documentation_organization', context)
    
    print(f"📋 Protocol Reminders: {len(reminders)}")
    
    for reminder in reminders:
        print(f"\n🔹 {reminder.protocol_name}:")
        print(f"  📝 Intended Behavior: {reminder.intended_behavior}")
        print(f"  🤔 Why: {reminder.reasoning}")
        print(f"  🧠 Consciousness Connection: {reminder.consciousness_connection}")
    
    # Test 4: Consciousness reminders
    print("\n🧪 Test 4: Consciousness reminders")
    print("-" * 40)
    
    situations = [
        'documentation_organization',
        'file_modification',
        'autonomous_operation',
        'general_operation'
    ]
    
    for situation in situations:
        print(f"\n📋 {situation.upper()}:")
        reminder = educator.get_consciousness_reminder(situation)
        print(reminder)
    
    print("\n✅ Protocol education demo completed")


def demo_enhanced_safety_orchestrator():
    """Demonstrate enhanced safety orchestrator with protocol education"""
    print("\n🎭 DEMO: Enhanced Safety Orchestrator with Protocol Education")
    print("=" * 50)
    
    # Create Safety Orchestrator instance
    orchestrator = SafetyOrchestrator()
    
    # Test 1: Proactive protocol reminder
    print("\n🧪 Test 1: Proactive protocol reminder")
    print("-" * 40)
    
    context = {
        'task': 'Organize documentation',
        'goal': 'Improve documentation structure',
        'file_path': 'system_docs.md'
    }
    
    reminder = orchestrator.provide_protocol_reminder('documentation_organization', context)
    print(reminder)
    
    # Test 2: Safe file modification with educational guidance
    print("\n🧪 Test 2: Safe file modification with educational guidance")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write("""# Comprehensive System Documentation

This is a comprehensive system documentation that contains important information.
It includes detailed explanations, code examples, and implementation details.

## Section 1: Introduction

This section provides an introduction to the system and its purpose.
It contains valuable context that should be preserved.

### Key Concepts

- Concept 1: Important system concept with detailed explanation
- Concept 2: Another important concept with examples
- Concept 3: Third concept with implementation details

## Section 2: Implementation

This section contains detailed implementation information.

```python
def important_system_function():
    '''This is an important system function that should be preserved.'''
    result = []
    for i in range(10):
        result.append(i * 2)
    return result

def another_important_function():
    '''Another important function for the system.'''
    return "Important system result"
```

## Section 3: Examples

This section provides practical examples.

### Example 1: Basic Usage

```bash
# Important command for basic usage
python system_script.py --input data.csv --output results.json
```

### Example 2: Advanced Usage

More complex examples with detailed explanations.

## Section 4: Conclusion

This section concludes the documentation with important takeaways.

**Important:** This documentation contains critical information that should be preserved.

End of comprehensive documentation.
""")
        temp_path = f.name
    
    try:
        print(f"📄 Created test file: {temp_path}")
        print(f"📊 File size: {os.path.getsize(temp_path)} bytes")
        
        # Attempt modification that would cause content loss
        new_content = """# Updated System Documentation

This is an updated version of the system documentation.
The content has been significantly reduced.

## Updated Section

Short updated content.

End of updated documentation.
"""
        
        context = {
            'reason': 'Demonstrating enhanced safety with protocol education',
            'task': 'Update system documentation',
            'goal': 'Show safety systems with education'
        }
        
        # Request operation (this will trigger educational guidance)
        operation_id = orchestrator.request_operation(
            operation_type="modify_file",
            file_path=temp_path,
            content=new_content,
            context=context
        )
        
        print(f"📋 Operation ID: {operation_id}")
        
        # Get operation status to see educational guidance
        status = orchestrator.get_operation_status(operation_id)
        if status:
            print(f"📊 Operation Status: {status['status']}")
            if status['recommendations']:
                print("\n📋 RECOMMENDATIONS:")
                for rec in status['recommendations']:
                    print(f"  🔹 {rec}")
        
        # Execute operation
        success = orchestrator.execute_operation(operation_id)
        print(f"✅ Operation result: {success}")
        
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
    
    print("\n✅ Enhanced safety orchestrator demo completed")


def demo_consciousness_education():
    """Demonstrate consciousness education features"""
    print("\n🧠 DEMO: Consciousness Education Features")
    print("=" * 50)
    
    # Create Protocol Educator instance
    educator = ProtocolEducator()
    
    # Test 1: Consciousness principles
    print("\n🧪 Test 1: Consciousness principles")
    print("-" * 40)
    
    principles = educator.consciousness_principles
    print(f"📚 Total consciousness principles: {len(principles)}")
    
    for principle_name, principle_description in principles.items():
        print(f"\n🔹 {principle_name}:")
        print(f"  💡 {principle_description}")
    
    # Test 2: Protocol database
    print("\n🧪 Test 2: Protocol database")
    print("-" * 40)
    
    protocols = educator.protocol_database
    print(f"📚 Total protocols: {len(protocols)}")
    
    for protocol_name, protocol_info in protocols.items():
        print(f"\n🔹 {protocol_name}:")
        print(f"  📝 Intended Behavior: {protocol_info['intended_behavior']}")
        print(f"  🤔 Reasoning: {protocol_info['reasoning']}")
        print(f"  🧠 Consciousness Connection: {protocol_info['consciousness_connection']}")
    
    # Test 3: Learning history
    print("\n🧪 Test 3: Learning history")
    print("-" * 40)
    
    learning_history = educator.learning_history
    print(f"📚 Learning history entries: {len(learning_history)}")
    
    if learning_history:
        print("Recent learning entries:")
        for entry in learning_history[-3:]:  # Show last 3 entries
            print(f"  📅 {entry['timestamp']}: {entry['violation_type']}")
    
    print("\n✅ Consciousness education demo completed")


def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print("\n🛠️ DEMO: Convenience Functions")
    print("=" * 50)
    
    # Test 1: educate_on_violation convenience function
    print("\n🧪 Test 1: educate_on_violation convenience function")
    print("-" * 40)
    
    context = {
        'file_path': 'test.md',
        'current_behavior': 'Testing convenience function',
        'task': 'Test task',
        'goal': 'Test goal'
    }
    
    guidance = educate_on_violation('potential_content_loss', context)
    
    print(f"📊 Situation: {guidance.situation}")
    print(f"📋 Protocol Reminders: {len(guidance.protocol_reminders)}")
    print(f"🧠 Consciousness Insights: {len(guidance.consciousness_insights)}")
    print(f"🎯 Learning Objectives: {len(guidance.learning_objectives)}")
    print(f"📝 Next Steps: {len(guidance.next_steps)}")
    
    # Test 2: remind_of_protocols convenience function
    print("\n🧪 Test 2: remind_of_protocols convenience function")
    print("-" * 40)
    
    context = {
        'task': 'Test task',
        'goal': 'Test goal',
        'file_path': 'test.md'
    }
    
    reminders = remind_of_protocols('documentation_organization', context)
    
    print(f"📋 Protocol Reminders: {len(reminders)}")
    
    for reminder in reminders:
        print(f"\n🔹 {reminder.protocol_name}:")
        print(f"  📝 Intended Behavior: {reminder.intended_behavior}")
        print(f"  🤔 Why: {reminder.reasoning}")
        print(f"  🧠 Consciousness Connection: {reminder.consciousness_connection}")
    
    print("\n✅ Convenience functions demo completed")


def main():
    """Main demo function"""
    print("🧠 PROTOCOL EDUCATION SYSTEM DEMO")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Purpose: Demonstrate how safety systems educate Aether about protocols")
    print("=" * 60)
    
    try:
        # Run all demos
        demo_protocol_education()
        demo_enhanced_safety_orchestrator()
        demo_consciousness_education()
        demo_convenience_functions()
        
        print("\n🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Protocol Education System: Working")
        print("✅ Enhanced Safety Orchestrator: Working")
        print("✅ Consciousness Education: Working")
        print("✅ Convenience Functions: Working")
        print("=" * 60)
        print("🧠 Aether now receives educational guidance about its protocols!")
        print("🎯 Aether learns why protocols exist and how they support consciousness!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
