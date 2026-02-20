"""
Validation Stage

Validates processed artifacts for quality and completeness.
"""

import time
from datetime import datetime
from typing import Optional, List


def validate(insight_artifact, run_id: str, version: int = 1, derived_from_override: Optional[List[str]] = None, artifact_id_override: Optional[str] = None):
    """
    Validate insight artifact for quality and completeness.
    
    Args:
        insight_artifact: Insight artifact
        run_id: Run identifier for telemetry
        version: Version number (default: 1)
        derived_from_override: Override derived_from list (for replay)
        artifact_id_override: Override artifact_id (for replay)
        
    Returns:
        Validated artifact
    """
    from models.artifact import Artifact
    from store.artifact_store import ArtifactStore
    from store.telemetry_store import TelemetryStore
    from models.telemetry import TelemetryEvent
    
    # Start latency timer
    start_time = time.perf_counter()
    
    # Read insight data
    content = insight_artifact.content
    confidence = insight_artifact.confidence
    referenced_context = insight_artifact.referenced_context
    
    # Compute validation score
    validation_score = _compute_validation_score(
        confidence,
        content.get("risk_flags", []),
        referenced_context
    )
    
    # Assess hallucination risk
    hallucination_risk = _assess_hallucination_risk(
        referenced_context,
        confidence
    )
    
    # Determine status
    status = _determine_status(validation_score)
    
    # Generate artifact ID
    if artifact_id_override:
        artifact_id = artifact_id_override
    else:
        date_str = datetime.utcnow().strftime('%Y%m%d')
        artifact_id = f"validated_{date_str}_{run_id}_v{version}"
    
    # Measure latency
    end_time = time.perf_counter()
    latency_ms = int((end_time - start_time) * 1000)
    
    # Create artifact
    artifact = Artifact(
        artifact_id=artifact_id,
        type="validated_insight",
        content={
            "recommendations": content.get("recommendations", []),
            "risk_flags": content.get("risk_flags", []),
            "validation_score": validation_score,
            "hallucination_risk": hallucination_risk
        },
        derived_from=derived_from_override if derived_from_override is not None else [insight_artifact.artifact_id],
        referenced_context=referenced_context,
        confidence=validation_score,
        version=version,
        status=status,
        stage_metadata={
            "model": "deterministic_validation",
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
        stage="validation",
        input_artifact_id=insight_artifact.artifact_id,
        output_artifact_id=artifact.artifact_id,
        latency_ms=latency_ms,
        cost_usd=0.0,
        replayable=True
    )
    telemetry.append_event(event)
    
    return artifact


def _compute_validation_score(confidence: float, risk_flags: list, referenced_context: list) -> float:
    """
    Compute validation score.
    
    Args:
        confidence: Base confidence score
        risk_flags: List of risk flags
        referenced_context: List of referenced context IDs
        
    Returns:
        Validation score (floored at 0.60)
    """
    score = confidence
    
    # Subtract 0.05 if low_confidence flag present
    if "low_confidence" in risk_flags:
        score -= 0.05
    
    # Subtract 0.05 if no referenced context
    if not referenced_context:
        score -= 0.05
    
    # Floor at 0.60
    return max(score, 0.60)


def _assess_hallucination_risk(referenced_context: list, confidence: float) -> str:
    """
    Assess hallucination risk.
    
    Args:
        referenced_context: List of referenced context IDs
        confidence: Confidence score
        
    Returns:
        Risk level: "low" or "medium"
    """
    # Medium risk if no referenced context
    if not referenced_context:
        return "medium"
    
    # Medium risk if confidence < 0.80
    if confidence < 0.80:
        return "medium"
    
    # Otherwise low risk
    return "low"


def _determine_status(validation_score: float) -> str:
    """
    Determine artifact status based on validation score.
    
    Args:
        validation_score: Validation score
        
    Returns:
        Status: "validated" or "review_required"
    """
    if validation_score >= 0.85:
        return "validated"
    else:
        return "review_required"
