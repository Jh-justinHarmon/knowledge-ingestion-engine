"""
Extraction Stage

Extracts structured data from normalized artifacts.
"""

import time
from datetime import datetime
from typing import Optional, List


def extract(transcript_artifact, run_id: str, version: int = 1, derived_from_override: Optional[List[str]] = None, artifact_id_override: Optional[str] = None):
    """
    Extract structured data from transcript artifact.
    
    Args:
        transcript_artifact: Normalized transcript artifact
        run_id: Run identifier for telemetry
        version: Version number (default: 1)
        derived_from_override: Override derived_from list (for replay)
        artifact_id_override: Override artifact_id (for replay)
        
    Returns:
        Extraction artifact
    """
    from models.artifact import Artifact
    from store.artifact_store import ArtifactStore
    from store.telemetry_store import TelemetryStore
    from models.telemetry import TelemetryEvent
    
    # Start latency timer
    start_time = time.perf_counter()
    
    # Read transcript text
    transcript_text = transcript_artifact.content["text"]
    
    # Extract structured data
    summary = _extract_summary(transcript_text)
    tasks = _extract_tasks(transcript_text)
    decisions = _extract_decisions(transcript_text)
    
    # Generate artifact ID
    if artifact_id_override:
        artifact_id = artifact_id_override
    else:
        date_str = datetime.utcnow().strftime('%Y%m%d')
        artifact_id = f"extraction_{date_str}_{run_id}_v{version}"
    
    # Measure latency
    end_time = time.perf_counter()
    latency_ms = int((end_time - start_time) * 1000)
    
    # Create artifact
    artifact = Artifact(
        artifact_id=artifact_id,
        type="extraction",
        content={
            "summary": summary,
            "tasks": tasks,
            "decisions": decisions
        },
        derived_from=derived_from_override if derived_from_override is not None else [transcript_artifact.artifact_id],
        referenced_context=[],
        confidence=0.85,
        version=version,
        status="draft",
        stage_metadata={
            "model": "rule-based",
            "tokens": 0,
            "cost_usd": 0.0,
            "latency_ms": latency_ms,
            "retrieval_ids": []
        }
    )
    
    # Persist artifact
    store = ArtifactStore()
    store.save_artifact(artifact)
    
    # Log telemetry
    telemetry = TelemetryStore()
    event = TelemetryEvent(
        run_id=run_id,
        stage="extract",
        input_artifact_id=transcript_artifact.artifact_id,
        output_artifact_id=artifact.artifact_id,
        latency_ms=latency_ms,
        cost_usd=0.0,
        replayable=True
    )
    telemetry.append_event(event)
    
    return artifact


def _extract_summary(text: str) -> str:
    """
    Extract summary from first 2 non-empty lines.
    
    Args:
        text: Transcript text
        
    Returns:
        Summary string
    """
    import re
    
    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    # Take first 2 non-empty lines
    summary_lines = non_empty_lines[:2]
    
    # Strip speaker labels from summary lines
    cleaned_lines = []
    for line in summary_lines:
        # Remove "Speaker <number>: " prefix
        cleaned_line = re.sub(r'^Speaker \d+:\s*', '', line)
        cleaned_lines.append(cleaned_line)
    
    return ' '.join(cleaned_lines)


def _extract_tasks(text: str) -> List[str]:
    """
    Extract tasks (lines containing 'will', 'action', or 'todo').
    
    Args:
        text: Transcript text
        
    Returns:
        List of task lines
    """
    lines = text.split('\n')
    tasks = []
    
    for line in lines:
        line_lower = line.lower()
        if 'will' in line_lower or 'action' in line_lower or 'todo' in line_lower:
            tasks.append(line.strip())
    
    return tasks


def _extract_decisions(text: str) -> List[str]:
    """
    Extract decisions (lines containing 'decided' or 'agree').
    
    Args:
        text: Transcript text
        
    Returns:
        List of decision lines
    """
    lines = text.split('\n')
    decisions = []
    
    for line in lines:
        line_lower = line.lower()
        if 'decided' in line_lower or 'agree' in line_lower:
            decisions.append(line.strip())
    
    return decisions
