"""Tests for Streaming Results"""

from __future__ import annotations
import pytest
import asyncio
from datetime import datetime

from apoe.streaming import (
    StreamEventType,
    StreamEvent,
    StreamingExecutor,
    stream_plan_execution,
    ProgressTracker
)
from apoe.models import Step, RoleType, Budget
from apoe.acl_parser import ExecutionPlan


def create_simple_plan():
    """Create simple test plan."""
    plan = ExecutionPlan(name="test_plan")
    
    s1 = Step(id="s1", name="step1", role=RoleType.OPERATOR, role_name="op", description="First")
    s2 = Step(id="s2", name="step2", role=RoleType.OPERATOR, role_name="op", description="Second")
    
    plan.steps = [s1, s2]
    return plan


def test_stream_event_creation():
    """Test creating stream event."""
    event = StreamEvent(
        type=StreamEventType.STEP_START,
        timestamp=datetime.utcnow(),
        data={"step_id": "s1"}
    )
    
    assert event.type == StreamEventType.STEP_START
    assert event.data["step_id"] == "s1"


def test_stream_event_to_dict():
    """Test converting event to dict."""
    now = datetime.utcnow()
    event = StreamEvent(
        type=StreamEventType.STEP_COMPLETE,
        timestamp=now,
        data={"result": "success"}
    )
    
    d = event.to_dict()
    
    assert d["type"] == "step_complete"
    assert d["timestamp"] == now.isoformat()
    assert d["data"]["result"] == "success"


def test_streaming_executor_emit():
    """Test emitting events."""
    events_received = []
    
    def on_event(event):
        events_received.append(event)
    
    executor = StreamingExecutor(on_event=on_event)
    
    executor.emit(StreamEventType.PLAN_START, {"plan_name": "test"})
    
    assert len(events_received) == 1
    assert events_received[0].type == StreamEventType.PLAN_START
    assert len(executor.events) == 1


def test_streaming_executor_cancel():
    """Test cancellation."""
    executor = StreamingExecutor()
    
    assert not executor.is_cancelled()
    
    executor.cancel()
    
    assert executor.is_cancelled()


def test_executor_get_events():
    """Test getting all events."""
    executor = StreamingExecutor()
    
    executor.emit(StreamEventType.PLAN_START, {"plan": "test"})
    executor.emit(StreamEventType.STEP_START, {"step": "s1"})
    
    events = executor.get_events()
    
    assert len(events) == 2
    assert events[0].type == StreamEventType.PLAN_START
    assert events[1].type == StreamEventType.STEP_START


def test_executor_get_progress():
    """Test progress tracking."""
    executor = StreamingExecutor()
    
    executor.emit(StreamEventType.PLAN_START, {"step_count": 3})
    executor.emit(StreamEventType.STEP_COMPLETE, {"step_id": "s1"})
    executor.emit(StreamEventType.STEP_COMPLETE, {"step_id": "s2"})
    
    progress = executor.get_progress()
    
    assert progress["total_steps"] == 3
    assert progress["completed"] == 2
    assert progress["errors"] == 0
    assert progress["progress_pct"] == pytest.approx(66.66, rel=0.1)


def test_execute_plan_streaming():
    """Test streaming plan execution."""
    plan = create_simple_plan()
    
    events_received = []
    
    def on_event(event):
        events_received.append(event)
    
    def step_executor(step):
        return {"step_id": step.id, "result": "done"}
    
    executor = StreamingExecutor(on_event=on_event)
    result = asyncio.run(executor.execute_plan_streaming(plan, step_executor))
    
    assert result["success"]
    assert len(result["results"]) == 2
    
    # Check events emitted
    event_types = [e.type for e in events_received]
    assert StreamEventType.PLAN_START in event_types
    assert StreamEventType.STEP_START in event_types
    assert StreamEventType.STEP_COMPLETE in event_types
    assert StreamEventType.PLAN_COMPLETE in event_types


def test_execute_plan_streaming_with_error():
    """Test streaming with step error."""
    plan = create_simple_plan()
    
    events_received = []
    
    def on_event(event):
        events_received.append(event)
    
    def step_executor(step):
        if step.id == "s2":
            raise ValueError("Step failed")
        return {"result": "done"}
    
    executor = StreamingExecutor(on_event=on_event)
    result = asyncio.run(executor.execute_plan_streaming(plan, step_executor))
    
    assert not result["success"]
    assert len(result["results"]) == 1  # Only s1 completed
    assert len(result["errors"]) == 1
    
    # Check error event emitted
    error_events = [e for e in events_received if e.type == StreamEventType.STEP_ERROR]
    assert len(error_events) == 1
    assert error_events[0].data["step_id"] == "s2"


def test_execute_plan_streaming_cancellation():
    """Test cancelling execution."""
    plan = create_simple_plan()
    
    def step_executor(step):
        return {"result": "done"}
    
    executor = StreamingExecutor()
    
    # Cancel before execution
    executor.cancel()
    
    result = asyncio.run(executor.execute_plan_streaming(plan, step_executor))
    
    assert not result["success"]
    assert result["error"] == "Cancelled"


def test_progress_tracker():
    """Test progress tracker."""
    tracker = ProgressTracker()
    
    # Plan start
    tracker.on_event(StreamEvent(
        type=StreamEventType.PLAN_START,
        timestamp=datetime.utcnow(),
        data={"step_count": 3}
    ))
    
    assert tracker.steps_total == 3
    assert tracker.start_time is not None
    
    # Step complete
    tracker.on_event(StreamEvent(
        type=StreamEventType.STEP_COMPLETE,
        timestamp=datetime.utcnow(),
        data={"step_id": "s1"}
    ))
    
    assert tracker.steps_completed == 1
    
    # Step error
    tracker.on_event(StreamEvent(
        type=StreamEventType.STEP_ERROR,
        timestamp=datetime.utcnow(),
        data={"step_id": "s2", "error": "failed"}
    ))
    
    assert tracker.steps_failed == 1
    
    # Plan complete
    tracker.on_event(StreamEvent(
        type=StreamEventType.PLAN_COMPLETE,
        timestamp=datetime.utcnow(),
        data={}
    ))
    
    assert tracker.end_time is not None


def test_progress_tracker_stats():
    """Test progress tracker statistics."""
    tracker = ProgressTracker()
    
    tracker.on_event(StreamEvent(
        type=StreamEventType.PLAN_START,
        timestamp=datetime.utcnow(),
        data={"step_count": 5}
    ))
    
    tracker.on_event(StreamEvent(
        type=StreamEventType.STEP_COMPLETE,
        timestamp=datetime.utcnow(),
        data={"step_id": "s1"}
    ))
    
    tracker.on_event(StreamEvent(
        type=StreamEventType.STEP_COMPLETE,
        timestamp=datetime.utcnow(),
        data={"step_id": "s2"}
    ))
    
    stats = tracker.get_stats()
    
    assert stats["total"] == 5
    assert stats["completed"] == 2
    assert stats["failed"] == 0
    assert stats["remaining"] == 3
    assert stats["progress_pct"] == 40.0
    assert "start_time" in stats
    assert "duration_seconds" in stats


def test_stream_event_types():
    """Test all stream event types."""
    assert StreamEventType.PLAN_START == "plan_start"
    assert StreamEventType.STEP_START == "step_start"
    assert StreamEventType.STEP_PROGRESS == "step_progress"
    assert StreamEventType.STEP_COMPLETE == "step_complete"
    assert StreamEventType.STEP_ERROR == "step_error"
    assert StreamEventType.GATE_CHECK == "gate_check"
    assert StreamEventType.PLAN_COMPLETE == "plan_complete"
    assert StreamEventType.PLAN_ERROR == "plan_error"


def test_execute_with_async_executor():
    """Test execution with async step executor."""
    plan = create_simple_plan()
    
    async def async_executor(step):
        await asyncio.sleep(0.01)
        return {"step_id": step.id, "result": "async_done"}
    
    executor = StreamingExecutor()
    result = asyncio.run(executor.execute_plan_streaming(plan, async_executor))
    
    assert result["success"]
    assert len(result["results"]) == 2
    assert result["results"]["s1"]["result"] == "async_done"

