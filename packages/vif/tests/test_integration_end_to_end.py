"""End-to-end VIF integration tests

Tests complete workflows using all VIF components together.
"""

import pytest
from unittest.mock import Mock, MagicMock

from vif import (
    VIF,
    ConfidenceBand,
    TaskCriticality,
    extract_confidence,
    ECETracker,
    KappaGate,
    HITLEscalator,
    ReplayEngine,
    format_confidence_for_user,
    VIFStore,
    create_witness_and_store,
)


def test_complete_workflow_high_confidence():
    """Test complete workflow with high confidence operation"""
    
    # 1. Extract confidence from LLM output
    llm_output = "I am 95% confident that the capital of France is Paris."
    extraction = extract_confidence(llm_output)
    assert extraction.confidence_score == 0.95
    
    # 2. Check κ-gate
    gate = KappaGate()
    gate_result = gate.check(
        confidence=extraction.confidence_score,
        task_criticality=TaskCriticality.ROUTINE
    )
    assert gate_result.passed is True
    
    # 3. Create VIF witness
    vif = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_123",
        prompt_hash=VIF.hash_text("What is the capital of France?"),
        prompt_tokens=10,
        confidence_score=extraction.confidence_score,
        confidence_band=ConfidenceBand.A,
        output_hash=VIF.hash_text(llm_output),
        output_tokens=20,
        total_tokens=30,
        task_criticality=TaskCriticality.ROUTINE,
        kappa_threshold=gate_result.threshold,
        kappa_gate_passed=gate_result.passed,
    )
    
    # 4. Format for user
    user_display = format_confidence_for_user(vif.confidence_score)
    assert "🟢" in user_display  # Green
    assert "95%" in user_display
    
    # 5. Store in CMC (mocked)
    mock_cmc = MagicMock()
    mock_atom = Mock()
    mock_atom.id = "atom_abc"
    mock_cmc.create_atom.return_value = mock_atom
    
    store = VIFStore(mock_cmc)
    atom_id = store.store_witness(vif)
    
    assert atom_id == "atom_abc"
    assert mock_cmc.create_atom.called


def test_complete_workflow_failed_gate():
    """Test workflow when κ-gate fails (low confidence)"""
    
    # 1. Extract low confidence
    llm_output = "I'm not sure, but maybe the answer is X."
    extraction = extract_confidence(llm_output)
    assert extraction.confidence_score <= 0.70
    
    # 2. Check κ-gate (critical task)
    gate = KappaGate()
    escalator = HITLEscalator()
    
    gate_result = gate.check(
        confidence=extraction.confidence_score,
        task_criticality=TaskCriticality.CRITICAL
    )
    
    assert gate_result.passed is False
    assert gate_result.should_escalate is True
    
    # 3. Escalate to human
    escalation_id = escalator.escalate(
        gate_result,
        context={"operation": "medical_diagnosis"}
    )
    
    assert escalation_id is not None
    pending = escalator.get_pending()
    assert len(pending) == 1
    
    # 4. Human reviews and rejects
    escalator.resolve(escalation_id, decision="reject", feedback="Too uncertain")
    
    resolved = escalator.get_resolved()
    assert len(resolved) == 1
    assert resolved[0]["human_decision"]["decision"] == "reject"


def test_complete_workflow_with_calibration():
    """Test workflow with calibration tracking"""
    
    # 1. Create calibration tracker
    tracker = ECETracker(num_bins=10)
    
    # 2. Simulate multiple operations with tracking
    operations = [
        ("I am 90% confident", True, 0.90),  # Correct
        ("I am 80% confident", True, 0.80),  # Correct
        ("I am 85% confident", False, 0.85), # Incorrect
        ("I am 75% confident", True, 0.75),  # Correct
    ]
    
    for output, correct, expected_conf in operations:
        # Extract confidence
        extraction = extract_confidence(output)
        assert abs(extraction.confidence_score - expected_conf) < 0.05
        
        # Track calibration
        tracker.add_prediction(extraction.confidence_score, correct)
    
    # 3. Calculate ECE
    ece = tracker.calculate_ece()
    assert ece >= 0.0  # Valid ECE
    
    # 4. Check calibration quality
    advice = tracker.get_calibration_advice()
    assert len(advice) > 0


def test_complete_workflow_with_replay():
    """Test workflow with deterministic replay"""
    
    # 1. Create original VIF witness
    original_prompt = "What is 2+2?"
    original_output = "4"
    
    vif = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_math",
        prompt_hash=VIF.hash_text(original_prompt),
        prompt_tokens=5,
        confidence_score=0.99,
        confidence_band=ConfidenceBand.A,
        output_hash=VIF.hash_text(original_output),
        output_tokens=1,
        total_tokens=6,
        replay_seed=42,
        temperature=0.0,
    )
    
    # 2. Replay operation
    engine = ReplayEngine()
    
    def deterministic_operation(params):
        return "4"  # Same output
    
    replay_result = engine.replay(vif, deterministic_operation)
    
    # 3. Verify replay matched
    assert replay_result.success is True
    assert replay_result.matches_original is True
    
    # 4. Verify output directly
    assert engine.verify_witness(vif, original_output) is True


def test_realistic_ai_operation_workflow():
    """Test realistic end-to-end AI operation with all VIF features"""
    
    # Setup
    mock_cmc = MagicMock()
    mock_atom = Mock()
    mock_atom.id = "atom_real_123"
    mock_cmc.create_atom.return_value = mock_atom
    
    gate = KappaGate()
    escalator = HITLEscalator()
    tracker = ECETracker(num_bins=10)
    
    # Simulate AI operation
    prompt = "Analyze this medical image for signs of pneumonia"
    llm_output = "Based on the image analysis, I am 88% confident that there are signs of pneumonia present. The characteristic infiltrates are visible in the lower right lung field."
    
    # Step 1: Extract confidence
    extraction = extract_confidence(llm_output)
    assert 0.85 <= extraction.confidence_score <= 0.90
    
    # Step 2: Check κ-gate (medical = critical)
    gate_result = gate.check(
        confidence=extraction.confidence_score,
        task_criticality=TaskCriticality.CRITICAL
    )
    
    # 88% < 95% threshold for critical tasks
    assert gate_result.passed is False
    assert gate_result.should_escalate is True
    
    # Step 3: Escalate to doctor
    escalation_id = escalator.escalate(
        gate_result,
        context={
            "task": "pneumonia_diagnosis",
            "patient_id": "P12345",
            "image_id": "IMG_789"
        }
    )
    
    # Step 4: Doctor reviews (simulate)
    # Doctor confirms diagnosis is correct
    escalator.resolve(
        escalation_id,
        decision="approve",
        feedback="Diagnosis confirmed by radiologist"
    )
    
    # Step 5: Track calibration
    tracker.add_prediction(
        confidence=extraction.confidence_score,
        correct=True  # Doctor confirmed
    )
    
    # Step 6: Create VIF witness
    vif, atom_id = create_witness_and_store(
        mock_cmc,
        operation_name="pneumonia_diagnosis",
        prompt=prompt,
        output=llm_output,
        confidence=extraction.confidence_score,
        context_snapshot_id="snap_medical_456",
        model_id="gpt-4-vision",
        model_provider="openai",
        task_criticality=TaskCriticality.CRITICAL,
        kappa_threshold=0.95,
        kappa_gate_passed=False,  # Failed gate, but human approved
    )
    
    # Step 7: Verify everything recorded
    assert vif.confidence_score == extraction.confidence_score
    assert vif.task_criticality == TaskCriticality.CRITICAL
    assert vif.kappa_gate_passed is False
    assert atom_id == "atom_real_123"
    
    # Step 8: Check calibration status
    summary = tracker.get_calibration_summary()
    assert summary["total_predictions"] == 1


def test_multi_operation_calibration_workflow():
    """Test calibration tracking across multiple operations"""
    
    tracker = ECETracker(num_bins=10)
    gate = KappaGate()
    
    # Simulate 20 operations
    operations = [
        ("I am 95% confident", TaskCriticality.CRITICAL, True),
        ("I am 90% confident", TaskCriticality.IMPORTANT, True),
        ("I am 85% confident", TaskCriticality.IMPORTANT, True),
        ("I am 80% confident", TaskCriticality.ROUTINE, False),
        ("I am 75% confident", TaskCriticality.ROUTINE, True),
        ("I am 70% confident", TaskCriticality.LOW_STAKES, True),
        ("I am 95% confident", TaskCriticality.CRITICAL, True),
        ("I am 85% confident", TaskCriticality.IMPORTANT, False),
        ("I am 90% confident", TaskCriticality.IMPORTANT, True),
        ("I am 80% confident", TaskCriticality.ROUTINE, True),
    ]
    
    gates_passed = 0
    gates_failed = 0
    
    for output, criticality, was_correct in operations:
        # Extract confidence
        extraction = extract_confidence(output)
        
        # Check gate
        gate_result = gate.check(extraction.confidence_score, criticality)
        
        if gate_result.passed:
            gates_passed += 1
        else:
            gates_failed += 1
        
        # Track calibration
        tracker.add_prediction(extraction.confidence_score, was_correct)
    
    # Verify tracking
    assert gates_passed + gates_failed == len(operations)
    
    # Calculate calibration
    ece = tracker.calculate_ece()
    assert 0.0 <= ece <= 1.0
    
    # Get summary
    summary = tracker.get_calibration_summary()
    assert summary["total_predictions"] == len(operations)


def test_confidence_band_routing_workflow():
    """Test routing based on confidence bands"""
    from vif.confidence_bands import BandRouter
    
    router = BandRouter()
    
    # High confidence - auto proceed
    vif_high = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash",
        output_tokens=5,
        total_tokens=15,
    )
    
    assert router.can_auto_proceed(vif_high.confidence_score)
    assert router.route(vif_high.confidence_score) == "auto_proceed"
    
    # Low confidence - review required
    vif_low = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.50,
        confidence_band=ConfidenceBand.C,
        output_hash="hash",
        output_tokens=5,
        total_tokens=15,
    )
    
    assert not router.can_auto_proceed(vif_low.confidence_score)
    assert router.route(vif_low.confidence_score) == "review_required"


def test_witness_lineage_tracking():
    """Test tracking lineage across multiple operations"""
    
    # Parent operation
    parent = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_1",
        prompt_hash=VIF.hash_text("Analyze data"),
        prompt_tokens=10,
        confidence_score=0.90,
        confidence_band=ConfidenceBand.A,
        output_hash=VIF.hash_text("Analysis complete"),
        output_tokens=20,
        total_tokens=30,
    )
    
    # Child operation (uses parent's output)
    child = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_2",
        prompt_hash=VIF.hash_text("Summarize analysis"),
        prompt_tokens=30,
        confidence_score=0.85,
        confidence_band=ConfidenceBand.B,
        output_hash=VIF.hash_text("Summary: ..."),
        output_tokens=15,
        total_tokens=45,
        parent_vif_id=parent.id,
    )
    
    # Update parent lineage
    parent.add_child(child.id)
    
    # Verify lineage
    assert child.parent_vif_id == parent.id
    assert child.id in parent.child_vif_ids
    
    # Grandchild operation
    grandchild = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_3",
        prompt_hash=VIF.hash_text("Translate summary"),
        prompt_tokens=15,
        confidence_score=0.92,
        confidence_band=ConfidenceBand.A,
        output_hash=VIF.hash_text("Résumé: ..."),
        output_tokens=20,
        total_tokens=35,
        parent_vif_id=child.id,
    )
    
    child.add_child(grandchild.id)
    
    # Verify chain
    assert grandchild.parent_vif_id == child.id
    assert child.parent_vif_id == parent.id


def test_adaptive_threshold_workflow():
    """Test adaptive κ threshold based on calibration"""
    from vif.kappa_gate import adaptive_kappa_threshold
    
    # Start with base threshold
    base_threshold = 0.70
    
    # Simulate poor calibration (ECE = 0.20)
    adjusted = adaptive_kappa_threshold(
        base_threshold,
        ece_score=0.20,
        past_accuracy=0.65
    )
    
    # Should raise threshold due to poor performance
    assert adjusted > base_threshold
    
    # Create gate with adjusted threshold
    gate = KappaGate()
    gate.set_threshold(TaskCriticality.ROUTINE, adjusted)
    
    # Now operation that would've passed with base threshold might fail
    result = gate.check(0.75, TaskCriticality.ROUTINE)
    
    # Adaptive threshold protects against overconfident model
    if adjusted > 0.75:
        assert not result.passed


def test_batch_replay_with_verification():
    """Test batch replay and verification"""
    
    engine = ReplayEngine()
    
    # Create multiple witnesses
    vifs = []
    for i in range(5):
        vif = VIF(
            model_id="test",
            model_provider="test",
            context_snapshot_id=f"snap_{i}",
            prompt_hash=VIF.hash_text(f"Query {i}"),
            prompt_tokens=10,
            confidence_score=0.85 + (i * 0.02),
            confidence_band=ConfidenceBand.B,
            output_hash=VIF.hash_text(f"Answer {i}"),
            output_tokens=5,
            total_tokens=15,
            replay_seed=i,
        )
        vifs.append(vif)
    
    # Batch replay
    def operation(params):
        snap_id = params["context"]["snapshot_id"]
        idx = int(snap_id.split("_")[1])
        return f"Answer {idx}"
    
    results = engine.batch_replay(vifs, operation)
    
    # Verify all matched
    assert len(results) == 5
    assert all(r.success for r in results)
    assert all(r.matches_original for r in results)
    
    # Calculate reproducibility
    repro_rate = engine.calculate_reproducibility_rate(results)
    assert repro_rate == 1.0  # 100% reproducible

