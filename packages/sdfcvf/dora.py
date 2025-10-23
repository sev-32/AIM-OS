"""DORA Metrics Tracking

Tracks Four Key Metrics from DevOps Research and Assessment (DORA):
1. Deployment Frequency
2. Lead Time for Changes
3. Change Failure Rate
4. Mean Time to Recovery (MTTR)

Correlates parity scores with deployment outcomes.
"""

from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, List, Tuple
import statistics


@dataclass
class DORAMetrics:
    """DORA Four Key Metrics."""
    deployment_frequency: float  # deployments per day
    lead_time_minutes: float     # average lead time
    change_failure_rate: float   # % of deployments that fail
    mttr_minutes: float          # average time to recover
    classification: str          # "ELITE" | "HIGH" | "MEDIUM" | "LOW"
    period_days: int             # measurement window


@dataclass
class CorrelationAnalysis:
    """Parity-DORA correlation results."""
    insufficient_data: bool
    high_parity_deployments: int = 0
    low_parity_deployments: int = 0
    high_parity_failure_rate: float = 0.0
    low_parity_failure_rate: float = 0.0
    correlation_coefficient: float = 0.0
    insight: str = ""


class DORAMetricsCollector:
    """
    Collect and track DORA metrics.
    
    Stores deployment events, incidents, and parity scores in SQLite
    for trend analysis and correlation studies.
    """
    
    def __init__(self, db_path: str = "dora_metrics.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                version TEXT,
                commit_sha TEXT,
                parity_score REAL,
                success BOOLEAN,
                lead_time_minutes INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                deployment_id INTEGER,
                resolved_at DATETIME,
                mttr_minutes INTEGER,
                caused_by_deployment BOOLEAN,
                FOREIGN KEY (deployment_id) REFERENCES deployments(id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_deployments_timestamp 
            ON deployments(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incidents_timestamp 
            ON incidents(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def record_deployment(
        self,
        version: str,
        commit_sha: str,
        parity_score: float,
        success: bool,
        lead_time_minutes: int
    ) -> int:
        """
        Record a deployment event.
        
        Args:
            version: Deployment version (e.g., "v1.2.3")
            commit_sha: Git commit SHA
            parity_score: Quartet parity score (0.0-1.0)
            success: Whether deployment succeeded
            lead_time_minutes: Minutes from commit to deployment
            
        Returns:
            Deployment ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO deployments (timestamp, version, commit_sha, parity_score, success, lead_time_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now(timezone.utc), version, commit_sha, parity_score, success, lead_time_minutes))
        
        deployment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return deployment_id
    
    def record_incident(
        self,
        deployment_id: int,
        resolved_at: datetime,
        caused_by_deployment: bool = True
    ):
        """
        Record an incident (production issue).
        
        Args:
            deployment_id: ID of deployment that caused incident
            resolved_at: When incident was resolved
            caused_by_deployment: Whether incident was caused by this deployment
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get deployment timestamp to calculate MTTR
        cursor.execute("SELECT timestamp FROM deployments WHERE id = ?", (deployment_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Deployment ID {deployment_id} not found")
        
        deployment_time = datetime.fromisoformat(row[0])
        mttr_minutes = int((resolved_at - deployment_time).total_seconds() / 60)
        
        cursor.execute("""
            INSERT INTO incidents (timestamp, deployment_id, resolved_at, mttr_minutes, caused_by_deployment)
            VALUES (?, ?, ?, ?, ?)
        """, (deployment_time, deployment_id, resolved_at, mttr_minutes, caused_by_deployment))
        
        conn.commit()
        conn.close()
    
    def calculate_dora_metrics(self, days: int = 30) -> DORAMetrics:
        """
        Calculate DORA metrics for time window.
        
        Four key metrics:
        1. Deployment Frequency (deployments per day)
        2. Lead Time for Changes (average minutes)
        3. Change Failure Rate (% of deployments causing incidents)
        4. Mean Time to Recovery (average minutes to fix)
        
        Args:
            days: Time window for calculation
            
        Returns:
            DORAMetrics with all four metrics and classification
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        # 1. Deployment Frequency
        cursor.execute("""
            SELECT COUNT(*) FROM deployments
            WHERE timestamp > ? AND success = 1
        """, (since.isoformat(),))
        successful_deployments = cursor.fetchone()[0]
        deployment_frequency = successful_deployments / days  # per day
        
        # 2. Lead Time (average)
        cursor.execute("""
            SELECT AVG(lead_time_minutes) FROM deployments
            WHERE timestamp > ? AND success = 1
        """, (since.isoformat(),))
        avg_lead_time = cursor.fetchone()[0] or 0.0
        
        # 3. Change Failure Rate
        cursor.execute("""
            SELECT COUNT(*) FROM deployments
            WHERE timestamp > ?
        """, (since.isoformat(),))
        total_deployments = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT deployment_id) FROM incidents
            WHERE timestamp > ? AND caused_by_deployment = 1
        """, (since.isoformat(),))
        failed_deployments = cursor.fetchone()[0]
        
        change_failure_rate = failed_deployments / total_deployments if total_deployments > 0 else 0.0
        
        # 4. MTTR (average)
        cursor.execute("""
            SELECT AVG(mttr_minutes) FROM incidents
            WHERE timestamp > ?
        """, (since.isoformat(),))
        avg_mttr = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        # Classify performance (elite/high/medium/low)
        classification = self._classify_performance(
            deployment_frequency,
            avg_lead_time,
            change_failure_rate,
            avg_mttr
        )
        
        return DORAMetrics(
            deployment_frequency=deployment_frequency,
            lead_time_minutes=avg_lead_time,
            change_failure_rate=change_failure_rate,
            mttr_minutes=avg_mttr,
            classification=classification,
            period_days=days
        )
    
    def _classify_performance(
        self,
        deploy_freq: float,
        lead_time: float,
        cfr: float,
        mttr: float
    ) -> str:
        """
        Classify DORA performance level.
        
        Based on 2021 State of DevOps Report thresholds.
        
        Returns:
            "ELITE" | "HIGH" | "MEDIUM" | "LOW"
        """
        # Elite: Deploy multiple times per day, LT < 1 hour, CFR < 15%, MTTR < 1 hour
        if deploy_freq >= 1.0 and lead_time <= 60 and cfr <= 0.15 and mttr <= 60:
            return "ELITE"
        
        # High: Deploy weekly-monthly, LT < 1 week, CFR 16-30%, MTTR < 1 day
        elif deploy_freq >= 0.14 and lead_time <= 10080 and cfr <= 0.30 and mttr <= 1440:
            return "HIGH"
        
        # Medium: Deploy monthly-semi-annually, LT < 6 months, CFR 31-45%
        elif deploy_freq >= 0.03 and lead_time <= 43200 and cfr <= 0.45:
            return "MEDIUM"
        
        # Low: Less frequent or slower
        else:
            return "LOW"


class ParityDORACorrelator:
    """
    Analyze correlation between parity scores and DORA metrics.
    
    Hypothesis: Higher parity → lower change failure rate, lower MTTR.
    Validates that quartet alignment improves deployment quality.
    """
    
    def __init__(self, db_path: str = "dora_metrics.db"):
        self.db_path = db_path
    
    def analyze_correlation(self, days: int = 90) -> CorrelationAnalysis:
        """
        Analyze correlation between parity scores and outcomes.
        
        Args:
            days: Time window for analysis
            
        Returns:
            CorrelationAnalysis with correlation coefficient and insights
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get all deployments with parity scores
        cursor.execute("""
            SELECT parity_score, success, lead_time_minutes
            FROM deployments
            WHERE timestamp > ? AND parity_score IS NOT NULL
        """, (since.isoformat(),))
        
        deployments = cursor.fetchall()
        
        if len(deployments) < 10:
            conn.close()
            return CorrelationAnalysis(
                insufficient_data=True,
                insight="Need at least 10 deployments with parity scores for meaningful analysis"
            )
        
        # Split into high parity (>0.85) and low parity (<0.85)
        high_parity = [d for d in deployments if d[0] > 0.85]
        low_parity = [d for d in deployments if d[0] <= 0.85]
        
        # Calculate failure rates
        high_failures = sum(1 for d in high_parity if not d[1])  # success=0
        low_failures = sum(1 for d in low_parity if not d[1])
        
        high_parity_failure_rate = high_failures / len(high_parity) if high_parity else 0.0
        low_parity_failure_rate = low_failures / len(low_parity) if low_parity else 0.0
        
        # Calculate correlation coefficient
        parity_scores = [d[0] for d in deployments]
        success_binary = [1 if d[1] else 0 for d in deployments]
        
        try:
            correlation = statistics.correlation(parity_scores, success_binary)
        except statistics.StatisticsError:
            correlation = 0.0
        
        # Generate insight
        if correlation > 0.3:
            insight = f"Strong positive correlation: Higher parity → higher success rate ({correlation:.2f})"
        elif correlation > 0.1:
            insight = f"Moderate correlation: Higher parity somewhat improves success ({correlation:.2f})"
        elif correlation < -0.1:
            insight = f"Negative correlation detected: Investigate parity calculation ({correlation:.2f})"
        else:
            insight = f"Weak correlation: Parity may not strongly predict success ({correlation:.2f})"
        
        conn.close()
        
        return CorrelationAnalysis(
            insufficient_data=False,
            high_parity_deployments=len(high_parity),
            low_parity_deployments=len(low_parity),
            high_parity_failure_rate=high_parity_failure_rate,
            low_parity_failure_rate=low_parity_failure_rate,
            correlation_coefficient=correlation,
            insight=insight
        )
    
    def get_parity_impact(self, min_parity: float = 0.85) -> Dict[str, float]:
        """
        Calculate impact of maintaining high parity.
        
        Args:
            min_parity: Threshold for "high parity"
            
        Returns:
            Dictionary with improvement metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get deployments above threshold
        cursor.execute("""
            SELECT AVG(CAST(success AS FLOAT)), COUNT(*)
            FROM deployments
            WHERE parity_score >= ?
        """, (min_parity,))
        high_success_rate, high_count = cursor.fetchone()
        high_success_rate = high_success_rate or 0.0
        
        # Get deployments below threshold
        cursor.execute("""
            SELECT AVG(CAST(success AS FLOAT)), COUNT(*)
            FROM deployments
            WHERE parity_score < ? AND parity_score IS NOT NULL
        """, (min_parity,))
        low_success_rate, low_count = cursor.fetchone()
        low_success_rate = low_success_rate or 0.0
        
        conn.close()
        
        if high_count == 0 or low_count == 0:
            return {
                "improvement": 0.0,
                "high_success_rate": high_success_rate,
                "low_success_rate": low_success_rate,
                "note": "Insufficient data"
            }
        
        improvement = high_success_rate - low_success_rate
        
        return {
            "improvement": improvement,
            "high_success_rate": high_success_rate,
            "low_success_rate": low_success_rate,
            "high_count": high_count,
            "low_count": low_count,
            "insight": f"High parity (≥{min_parity}) improves success rate by {improvement*100:.1f}%"
        }


def initialize_dora_db(db_path: str = "dora_metrics.db"):
    """
    Initialize DORA metrics database.
    
    Creates tables and indexes for tracking deployments and incidents.
    """
    collector = DORAMetricsCollector(db_path)
    print(f"✅ DORA metrics database initialized at {db_path}")


def report_dora_metrics(db_path: str = "dora_metrics.db", days: int = 30):
    """
    Generate DORA metrics report for time window.
    
    Args:
        db_path: Path to DORA database
        days: Time window for metrics
    """
    collector = DORAMetricsCollector(db_path)
    metrics = collector.calculate_dora_metrics(days)
    
    print(f"=== DORA Metrics ({days} days) ===")
    print(f"Classification: {metrics.classification}")
    print(f"\n1. Deployment Frequency: {metrics.deployment_frequency:.2f} per day")
    print(f"2. Lead Time for Changes: {metrics.lead_time_minutes:.0f} minutes")
    print(f"3. Change Failure Rate: {metrics.change_failure_rate*100:.1f}%")
    print(f"4. Mean Time to Recovery: {metrics.mttr_minutes:.0f} minutes")
    
    # Parity correlation
    correlator = ParityDORACorrelator(db_path)
    correlation = correlator.analyze_correlation(days=days)
    
    if not correlation.insufficient_data:
        print(f"\n=== Parity Correlation ===")
        print(f"High parity (>0.85): {correlation.high_parity_deployments} deployments, {correlation.high_parity_failure_rate*100:.1f}% failures")
        print(f"Low parity (≤0.85): {correlation.low_parity_deployments} deployments, {correlation.low_parity_failure_rate*100:.1f}% failures")
        print(f"Correlation coefficient: {correlation.correlation_coefficient:.3f}")
        print(f"Insight: {correlation.insight}")

