"""
Normalization Stage

Normalizes raw input artifacts into standard format.
"""

import re
import time
from datetime import datetime
from typing import Dict, List, Optional


def normalize(raw_text: str, run_id: str, version: int = 1, derived_from_override: Optional[List[str]] = None, artifact_id_override: Optional[str] = None):
    """
    Normalize raw text into structured artifact.
    
    Args:
        raw_text: Raw input text
        run_id: Run identifier for telemetry
        version: Version number (default: 1)
        derived_from_override: Override derived_from list (for replay)
        artifact_id_override: Override artifact_id (for replay)
        
    Returns:
        Artifact instance
    """
    from models.artifact import Artifact
    from store.artifact_store import ArtifactStore
    from store.telemetry_store import TelemetryStore
    from models.telemetry import TelemetryEvent
    
    # Start latency timer
    start_time = time.perf_counter()
    
    # Clean text
    cleaned_text = _clean_text(raw_text)
    
    # Standardize speaker labels
    cleaned_text = _standardize_speakers(cleaned_text)
    
    # Generate artifact ID
    if artifact_id_override:
        artifact_id = artifact_id_override
    else:
        date_str = datetime.utcnow().strftime('%Y%m%d')
        artifact_id = f"transcript_{date_str}_{run_id}_v{version}"
    
    # Measure latency
    end_time = time.perf_counter()
    latency_ms = int((end_time - start_time) * 1000)
    
    # Create artifact
    artifact = Artifact(
        artifact_id=artifact_id,
        type="transcript",
        content={"text": cleaned_text},
        confidence=0.95,
        version=version,
        status="draft",
        derived_from=derived_from_override if derived_from_override is not None else [],
        referenced_context=[],
        stage_metadata={
            "model": "deterministic",
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
        stage="normalize",
        input_artifact_id="raw_input",
        output_artifact_id=artifact.artifact_id,
        latency_ms=latency_ms,
        cost_usd=0.0,
        replayable=True
    )
    telemetry.append_event(event)
    
    return artifact


def _clean_text(text: str) -> str:
    """
    Clean raw text.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Normalize multiple blank lines to single blank line
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    return text


def _standardize_speakers(text: str) -> str:
    """
    Standardize speaker labels to Speaker 1:, Speaker 2:, etc.
    
    Args:
        text: Text with speaker labels
        
    Returns:
        Text with standardized speaker labels
    """
    lines = text.split('\n')
    speaker_map: Dict[str, str] = {}
    speaker_count = 0
    standardized_lines: List[str] = []
    
    for line in lines:
        # Match lines starting with name + ":"
        match = re.match(r'^([A-Za-z][A-Za-z\s]+?):\s*(.*)$', line)
        
        if match:
            speaker_name = match.group(1).strip()
            dialogue = match.group(2)
            
            # Assign speaker number if not seen before
            if speaker_name not in speaker_map:
                speaker_count += 1
                speaker_map[speaker_name] = f"Speaker {speaker_count}"
            
            standardized_label = speaker_map[speaker_name]
            standardized_lines.append(f"{standardized_label}: {dialogue}")
        else:
            standardized_lines.append(line)
    
    return '\n'.join(standardized_lines)
