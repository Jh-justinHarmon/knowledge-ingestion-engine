"""
Context Stage

Enriches artifacts with contextual information.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


def contextualize(extraction_artifact, run_id: str, version: int = 1, derived_from_override: Optional[List[str]] = None, artifact_id_override: Optional[str] = None):
    """
    Enrich extraction artifact with contextual information.
    
    Args:
        extraction_artifact: Extraction artifact
        run_id: Run identifier for telemetry
        version: Version number (default: 1)
        derived_from_override: Override derived_from list (for replay)
        artifact_id_override: Override artifact_id (for replay)
        
    Returns:
        Contextualized artifact
    """
    from models.artifact import Artifact
    from store.artifact_store import ArtifactStore
    from store.telemetry_store import TelemetryStore
    from models.telemetry import TelemetryEvent
    
    # Start latency timer
    start_time = time.perf_counter()
    
    # Load context files
    context_store_dir = Path("context_store")
    context_files = _load_context_files(context_store_dir)
    
    # Extract summary for matching
    summary = extraction_artifact.content.get("summary", "")
    
    # Deterministic retrieval
    referenced_context, retrieval_ids = _retrieve_contexts(summary, context_files)
    
    # Compute new confidence
    base_confidence = extraction_artifact.confidence
    new_confidence = _compute_confidence(base_confidence, len(referenced_context))
    
    # Generate artifact ID
    if artifact_id_override:
        artifact_id = artifact_id_override
    else:
        date_str = datetime.utcnow().strftime('%Y%m%d')
        artifact_id = f"contextualized_{date_str}_{run_id}_v{version}"
    
    # Measure latency
    end_time = time.perf_counter()
    latency_ms = int((end_time - start_time) * 1000)
    
    # Create artifact (preserve extraction content)
    artifact = Artifact(
        artifact_id=artifact_id,
        type="contextualized_extraction",
        content=extraction_artifact.content,  
        derived_from=derived_from_override if derived_from_override is not None else [extraction_artifact.artifact_id],
        referenced_context=referenced_context,
        confidence=new_confidence,
        version=version,
        status="draft",
        stage_metadata={
            "model": "deterministic_context_injection",
            "tokens": 0,
            "cost_usd": 0.0,
            "latency_ms": latency_ms,
            "retrieval_ids": retrieval_ids
        }
    )
    
    # Persist artifact
    store = ArtifactStore()
    store.save_artifact(artifact)
    
    # Log telemetry
    telemetry = TelemetryStore()
    event = TelemetryEvent(
        run_id=run_id,
        stage="context_injection",
        input_artifact_id=extraction_artifact.artifact_id,
        output_artifact_id=artifact.artifact_id,
        latency_ms=latency_ms,
        cost_usd=0.0,
        replayable=True
    )
    telemetry.append_event(event)
    
    return artifact


def _load_context_files(context_dir: Path) -> List[Dict[str, Any]]:
    """
    Load all JSON context files from directory.
    
    Args:
        context_dir: Path to context store directory
        
    Returns:
        List of context dictionaries
    """
    contexts = []
    
    if not context_dir.exists():
        return contexts
    
    for json_file in context_dir.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                context = json.load(f)
                contexts.append(context)
        except (json.JSONDecodeError, IOError):
            # Skip invalid files
            pass
    
    return contexts


def _retrieve_contexts(summary: str, context_files: List[Dict[str, Any]]) -> tuple:
    """
    Deterministically retrieve contexts based on word containment.
    
    Args:
        summary: Summary text from extraction
        context_files: List of context dictionaries
        
    Returns:
        Tuple of (referenced_context_ids, retrieval_ids)
    """
    # Stopwords to filter out
    stopwords = {
        "the", "a", "an", "and", "or", "for", "to", "of",
        "in", "on", "at", "with", "we", "i", "it",
        "that", "this", "is", "are", "was", "were"
    }
    
    # Split summary into lowercase words and filter
    raw_words = summary.lower().split()
    summary_words = []
    
    for word in raw_words:
        # Strip punctuation
        cleaned_word = word.strip('.,!?;:()[]{}"\'-')
        
        # Filter: remove stopwords and words shorter than 3 characters
        if cleaned_word and len(cleaned_word) >= 3 and cleaned_word not in stopwords:
            summary_words.append(cleaned_word)
    
    retrieved_ids = []
    
    for context in context_files:
        context_content = context.get("content", "").lower()
        context_id = context.get("context_id", "")
        
        # Check if ANY summary word appears in context content
        for word in summary_words:
            if word in context_content:
                retrieved_ids.append(context_id)
                break  # Only add once per context
    
    # Both lists are the same
    return retrieved_ids, retrieved_ids


def _compute_confidence(base_confidence: float, num_contexts: int) -> float:
    """
    Compute new confidence based on retrieved contexts.
    
    Args:
        base_confidence: Original confidence score
        num_contexts: Number of retrieved contexts
        
    Returns:
        New confidence score (capped at 0.95)
    """
    # Add 0.02 per retrieved context
    new_confidence = base_confidence + (num_contexts * 0.02)
    
    # Cap at 0.95
    return min(new_confidence, 0.95)
