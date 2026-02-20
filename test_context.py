#!/usr/bin/env python3
"""
Test context stage.
"""

from stages.normalize import normalize
from stages.extract import extract
from stages.context import contextualize


def test_context():
    """Test context stage with extraction artifact."""
    
    # Create sample transcript with words that match context store
    raw_text = """
John Smith: We will implement the new feature for the meeting next week.

Jane Doe: I agree with that project timeline.

John Smith: The conversation about action items is clear.
"""
    
    print("=" * 80)
    print("CONTEXT STAGE TEST")
    print("=" * 80)
    
    # Step 1: Normalize
    print("\nStep 1: Normalize transcript")
    transcript = normalize(raw_text, run_id="test_context")
    print(f"  ✅ Created transcript: {transcript.artifact_id}")
    
    # Step 2: Extract
    print("\nStep 2: Extract structured data")
    extraction = extract(transcript, run_id="test_context")
    print(f"  ✅ Created extraction: {extraction.artifact_id}")
    print(f"     Summary: {extraction.content['summary']}")
    print(f"     Base confidence: {extraction.confidence}")
    
    # Step 3: Contextualize
    print("\nStep 3: Contextualize extraction")
    contextualized = contextualize(extraction, run_id="test_context")
    
    print("\n" + "=" * 80)
    print("CONTEXTUALIZED ARTIFACT")
    print("=" * 80)
    print(f"Artifact ID: {contextualized.artifact_id}")
    print(f"Type: {contextualized.type}")
    print(f"Status: {contextualized.status}")
    print(f"Version: {contextualized.version}")
    print(f"Confidence: {contextualized.confidence} (was {extraction.confidence})")
    print(f"Derived from: {contextualized.derived_from}")
    print(f"Referenced context: {contextualized.referenced_context}")
    
    print("\nStage metadata:")
    for key, value in contextualized.stage_metadata.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("CONTENT PRESERVATION CHECK")
    print("=" * 80)
    print(f"Summary: {contextualized.content['summary']}")
    print(f"Tasks: {len(contextualized.content['tasks'])} items")
    print(f"Decisions: {len(contextualized.content['decisions'])} items")
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Check artifact structure
    assert contextualized.type == "contextualized_extraction", "Incorrect type"
    assert contextualized.status == "draft", "Incorrect status"
    assert contextualized.version == 1, "Incorrect version"
    print("✅ Artifact structure correct")
    
    # Check derived_from
    assert len(contextualized.derived_from) == 1, "Should have 1 parent"
    assert contextualized.derived_from[0] == extraction.artifact_id, "Incorrect parent ID"
    print("✅ Derived_from tracking correct")
    
    # Check stage metadata
    assert contextualized.stage_metadata["model"] == "deterministic_context_injection", "Incorrect model"
    assert contextualized.stage_metadata["tokens"] == 0, "Incorrect token count"
    assert contextualized.stage_metadata["cost_usd"] == 0.0, "Incorrect cost"
    assert contextualized.stage_metadata["latency_ms"] >= 0, "Invalid latency"
    print("✅ Stage metadata correct")
    
    # Check content preservation
    assert contextualized.content == extraction.content, "Content was modified!"
    print("✅ Extraction content preserved (not modified)")
    
    # Check confidence adjustment
    num_contexts = len(contextualized.referenced_context)
    expected_confidence = min(extraction.confidence + (num_contexts * 0.02), 0.95)
    assert abs(contextualized.confidence - expected_confidence) < 0.001, "Confidence calculation incorrect"
    print(f"✅ Confidence adjusted correctly (+{num_contexts * 0.02:.2f} for {num_contexts} contexts)")
    
    # Check referenced_context
    assert isinstance(contextualized.referenced_context, list), "referenced_context should be list"
    print(f"✅ Referenced {len(contextualized.referenced_context)} context(s)")
    
    # Check retrieval_ids match referenced_context
    assert contextualized.stage_metadata["retrieval_ids"] == contextualized.referenced_context, "retrieval_ids mismatch"
    print("✅ retrieval_ids matches referenced_context")
    
    # Check that extraction was not mutated
    assert extraction.type == "extraction", "Extraction type changed"
    assert extraction.confidence == 0.85, "Extraction confidence changed"
    print("✅ Original extraction not mutated")
    
    print("\n✅ All context stage tests passed")


if __name__ == '__main__':
    test_context()
