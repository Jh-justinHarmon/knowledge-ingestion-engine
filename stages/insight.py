"""
Insight Stage

Generates insights from enriched artifacts.
"""

import time
from datetime import datetime
from typing import List, Optional


def generate_insight(contextualized_artifact, run_id: str, version: int = 1, derived_from_override: Optional[List[str]] = None, artifact_id_override: Optional[str] = None):
    """
    Generate insights from contextualized artifact.
    
    Args:
        contextualized_artifact: Contextualized extraction artifact
        run_id: Run identifier for telemetry
        version: Version number (default: 1)
        derived_from_override: Override derived_from list (for replay)
        artifact_id_override: Override artifact_id (for replay)
        
    Returns:
        Insight artifact
    """
    from models.artifact import Artifact
    from store.artifact_store import ArtifactStore
    from store.telemetry_store import TelemetryStore
    from models.telemetry import TelemetryEvent
    
    # Start latency timer
    start_time = time.perf_counter()
    
    # Read content and referenced context
    content = contextualized_artifact.content
    referenced_context = contextualized_artifact.referenced_context
    
    # Generate recommendations
    recommendations = _generate_recommendations(content)
    
    # Generate risk flags
    risk_flags = _generate_risk_flags(contextualized_artifact.confidence)
    
    # Compute new confidence
    base_confidence = contextualized_artifact.confidence
    new_confidence = _compute_confidence(base_confidence)
    
    # Generate artifact ID
    if artifact_id_override:
        artifact_id = artifact_id_override
    else:
        date_str = datetime.utcnow().strftime('%Y%m%d')
        artifact_id = f"insight_{date_str}_{run_id}_v{version}"
    
    # Measure latency
    end_time = time.perf_counter()
    latency_ms = int((end_time - start_time) * 1000)
    
    # Create artifact
    artifact = Artifact(
        artifact_id=artifact_id,
        type="insight",
        content={
            "recommendations": recommendations,
            "risk_flags": risk_flags,
            "source_summary": content.get("summary", "")
        },
        derived_from=derived_from_override if derived_from_override is not None else [contextualized_artifact.artifact_id],
        referenced_context=referenced_context,
        confidence=new_confidence,
        version=version,
        status="draft",
        stage_metadata={
            "model": "deterministic_interpretation",
            "tokens": 0,
            "cost_usd": 0.0,
            "latency_ms": latency_ms,
            "retrieval_ids": referenced_context
        }
    )
    
    # Persist artifact
    store = ArtifactStore()
    store.save_artifact(artifact)
    
    # Log telemetry
    telemetry = TelemetryStore()
    event = TelemetryEvent(
        run_id=run_id,
        stage="insight",
        input_artifact_id=contextualized_artifact.artifact_id,
        output_artifact_id=artifact.artifact_id,
        latency_ms=latency_ms,
        cost_usd=0.0,
        replayable=True
    )
    telemetry.append_event(event)
    
    return artifact


def _generate_recommendations(content: dict) -> List[str]:
    """
    Generate recommendations based on content.
    
    Args:
        content: Artifact content with tasks and decisions
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    tasks = content.get("tasks", [])
    decisions = content.get("decisions", [])
    
    if tasks:
        recommendations.append("Review task ownership and deadlines.")
    
    if decisions:
        recommendations.append("Validate decision impact on project timeline.")
    
    if not tasks:
        recommendations.append("No action items detected.")
    
    return recommendations


def _generate_risk_flags(confidence: float) -> List[str]:
    """
    Generate risk flags based on confidence.
    
    Args:
        confidence: Confidence score
        
    Returns:
        List of risk flags
    """
    risk_flags = []
    
    if confidence < 0.88:
        risk_flags.append("low_confidence")
    
    return risk_flags


def _compute_confidence(base_confidence: float) -> float:
    """
    Compute new confidence (reduce by 0.03, floor at 0.70).
    
    Args:
        base_confidence: Original confidence score
        
    Returns:
        New confidence score (floored at 0.70)
    """
    new_confidence = base_confidence - 0.03
    
    # Floor at 0.70
    return max(new_confidence, 0.70)
