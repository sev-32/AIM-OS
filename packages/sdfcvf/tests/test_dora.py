"""Tests for DORA Metrics"""

from __future__ import annotations
import pytest
from datetime import datetime, timedelta, timezone
import os
import tempfile

from sdfcvf.dora import (
    DORAMetricsCollector,
    DORAMetrics,
    ParityDORACorrelator,
    CorrelationAnalysis,
    initialize_dora_db,
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


def test_dora_db_initialization(temp_db):
    """Test database initialization."""
    collector = DORAMetricsCollector(temp_db)
    
    # Check that tables were created
    import sqlite3
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert "deployments" in tables
    assert "incidents" in tables
    
    conn.close()


def test_record_deployment(temp_db):
    """Test recording a deployment."""
    collector = DORAMetricsCollector(temp_db)
    
    deployment_id = collector.record_deployment(
        version="v1.0.0",
        commit_sha="abc123",
        parity_score=0.92,
        success=True,
        lead_time_minutes=45
    )
    
    assert deployment_id > 0


def test_record_incident(temp_db):
    """Test recording an incident."""
    collector = DORAMetricsCollector(temp_db)
    
    # Create deployment first
    deployment_id = collector.record_deployment(
        version="v1.0.0",
        commit_sha="abc123",
        parity_score=0.75,
        success=False,
        lead_time_minutes=60
    )
    
    # Record incident
    resolved_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    collector.record_incident(deployment_id, resolved_at)
    
    # Should not raise exception
    assert True


def test_calculate_dora_metrics_empty(temp_db):
    """Test DORA metrics with no data."""
    collector = DORAMetricsCollector(temp_db)
    
    metrics = collector.calculate_dora_metrics(days=30)
    
    assert metrics.deployment_frequency == 0.0
    assert metrics.lead_time_minutes == 0.0
    assert metrics.change_failure_rate == 0.0
    assert metrics.mttr_minutes == 0.0
    assert metrics.classification == "LOW"


def test_calculate_dora_metrics_with_data(temp_db):
    """Test DORA metrics calculation with sample data."""
    collector = DORAMetricsCollector(temp_db)
    
    # Add sample deployments
    for i in range(5):
        collector.record_deployment(
            version=f"v1.{i}.0",
            commit_sha=f"sha{i}",
            parity_score=0.90,
            success=True,
            lead_time_minutes=60
        )
    
    # Add one failure
    failed_id = collector.record_deployment(
        version="v2.0.0",
        commit_sha="sha_fail",
        parity_score=0.70,
        success=False,
        lead_time_minutes=120
    )
    
    # Record incident for failure
    collector.record_incident(failed_id, datetime.now(timezone.utc) + timedelta(minutes=45))
    
    # Calculate metrics
    metrics = collector.calculate_dora_metrics(days=30)
    
    assert metrics.deployment_frequency > 0
    assert metrics.lead_time_minutes > 0
    assert 0 <= metrics.change_failure_rate <= 1.0
    assert metrics.classification in ["ELITE", "HIGH", "MEDIUM", "LOW"]


def test_classification_elite():
    """Test ELITE classification."""
    collector = DORAMetricsCollector(":memory:")
    
    # Elite: Deploy >1/day, LT<1hr, CFR<15%, MTTR<1hr
    classification = collector._classify_performance(
        deploy_freq=2.0,
        lead_time=30.0,
        cfr=0.10,
        mttr=30.0
    )
    
    assert classification == "ELITE"


def test_classification_high():
    """Test HIGH classification."""
    collector = DORAMetricsCollector(":memory:")
    
    # High: Deploy weekly, LT<1week, CFR<30%, MTTR<1day
    classification = collector._classify_performance(
        deploy_freq=0.2,  # ~weekly
        lead_time=1440.0,  # 1 day
        cfr=0.25,
        mttr=720.0  # 12 hours
    )
    
    assert classification == "HIGH"


def test_classification_medium():
    """Test MEDIUM classification."""
    collector = DORAMetricsCollector(":memory:")
    
    classification = collector._classify_performance(
        deploy_freq=0.05,  # ~monthly
        lead_time=10000.0,
        cfr=0.40,
        mttr=2000.0
    )
    
    assert classification == "MEDIUM"


def test_classification_low():
    """Test LOW classification."""
    collector = DORAMetricsCollector(":memory:")
    
    classification = collector._classify_performance(
        deploy_freq=0.01,  # rare
        lead_time=50000.0,
        cfr=0.60,
        mttr=5000.0
    )
    
    assert classification == "LOW"


def test_parity_correlation_insufficient_data(temp_db):
    """Test correlation analysis with insufficient data."""
    # Initialize database first
    collector = DORAMetricsCollector(temp_db)
    
    # Now use correlator on empty database
    correlator = ParityDORACorrelator(temp_db)
    
    # Empty database
    result = correlator.analyze_correlation(days=90)
    
    assert result.insufficient_data
    assert "at least 10" in result.insight.lower()


def test_parity_correlation_with_data(temp_db):
    """Test correlation analysis with sample data."""
    collector = DORAMetricsCollector(temp_db)
    
    # Add 10 high-parity successful deployments
    for i in range(10):
        collector.record_deployment(
            version=f"v1.{i}",
            commit_sha=f"high_{i}",
            parity_score=0.92,
            success=True,
            lead_time_minutes=50
        )
    
    # Add 5 low-parity deployments (some failures)
    for i in range(5):
        success = (i % 2 == 0)  # 60% failure rate for low parity
        collector.record_deployment(
            version=f"v2.{i}",
            commit_sha=f"low_{i}",
            parity_score=0.70,
            success=success,
            lead_time_minutes=90
        )
    
    # Analyze correlation
    correlator = ParityDORACorrelator(temp_db)
    result = correlator.analyze_correlation(days=90)
    
    assert not result.insufficient_data
    assert result.high_parity_deployments == 10
    assert result.low_parity_deployments == 5
    assert result.high_parity_failure_rate < result.low_parity_failure_rate  # Higher parity = fewer failures
    assert result.correlation_coefficient != 0.0


def test_initialize_dora_db_convenience(temp_db):
    """Test convenience function for DB initialization."""
    initialize_dora_db(temp_db)
    
    # Verify database exists and has tables
    import sqlite3
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    assert "deployments" in tables
    assert "incidents" in tables

