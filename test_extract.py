#!/usr/bin/env python3
"""
Test extract stage.
"""

from stages.normalize import normalize
from stages.extract import extract


def test_extract():
    """Test extract stage with normalized transcript."""
    
    # Create sample transcript with tasks and decisions
    raw_text = """
John Smith: We will implement the new feature next week.

Jane Doe: I agree with that timeline.

John Smith: The action items are clear.

Jane Doe: We decided to use the new framework.

Moderator: Everyone will review the proposal by Friday.

John Smith: That's a good todo for the team.
"""
    
    print("=" * 80)
    print("EXTRACT STAGE TEST")
    print("=" * 80)
    
    # First normalize
    print("\nStep 1: Normalize transcript")
    transcript = normalize(raw_text, run_id="test_extract")
    print(f"  ✅ Created transcript: {transcript.artifact_id}")
    
    # Then extract
    print("\nStep 2: Extract structured data")
    extraction = extract(transcript, run_id="test_extract")
    
    print("\n" + "=" * 80)
    print("EXTRACTION ARTIFACT")
    print("=" * 80)
    print(f"Artifact ID: {extraction.artifact_id}")
    print(f"Type: {extraction.type}")
    print(f"Status: {extraction.status}")
    print(f"Version: {extraction.version}")
    print(f"Confidence: {extraction.confidence}")
    print(f"Derived from: {extraction.derived_from}")
    
    print("\nStage metadata:")
    for key, value in extraction.stage_metadata.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("EXTRACTED CONTENT")
    print("=" * 80)
    
    print("\nSummary:")
    print(f"  {extraction.content['summary']}")
    
    print("\nTasks:")
    for task in extraction.content['tasks']:
        print(f"  - {task}")
    
    print("\nDecisions:")
    for decision in extraction.content['decisions']:
        print(f"  - {decision}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Check artifact structure
    assert extraction.type == "extraction", "Incorrect type"
    assert extraction.status == "draft", "Incorrect status"
    assert extraction.version == 1, "Incorrect version"
    assert extraction.confidence == 0.85, "Incorrect confidence"
    print("✅ Artifact structure correct")
    
    # Check derived_from
    assert len(extraction.derived_from) == 1, "Should have 1 parent"
    assert extraction.derived_from[0] == transcript.artifact_id, "Incorrect parent ID"
    print("✅ Derived_from tracking correct")
    
    # Check stage metadata
    assert extraction.stage_metadata["model"] == "rule-based", "Incorrect model"
    assert extraction.stage_metadata["tokens"] == 0, "Incorrect token count"
    assert extraction.stage_metadata["cost_usd"] == 0.0, "Incorrect cost"
    assert extraction.stage_metadata["latency_ms"] >= 0, "Invalid latency"
    print("✅ Stage metadata correct")
    
    # Check extracted content
    assert extraction.content['summary'], "Summary should not be empty"
    assert len(extraction.content['tasks']) > 0, "Should have extracted tasks"
    assert len(extraction.content['decisions']) > 0, "Should have extracted decisions"
    print("✅ Extracted content present")
    
    # Verify specific extractions
    tasks = extraction.content['tasks']
    decisions = extraction.content['decisions']
    
    # Check for expected keywords
    task_text = ' '.join(tasks).lower()
    assert 'will' in task_text or 'action' in task_text or 'todo' in task_text, "Tasks missing keywords"
    print("✅ Tasks contain expected keywords")
    
    decision_text = ' '.join(decisions).lower()
    assert 'agree' in decision_text or 'decided' in decision_text, "Decisions missing keywords"
    print("✅ Decisions contain expected keywords")
    
    # Check that transcript was not mutated
    assert transcript.type == "transcript", "Transcript type changed"
    assert transcript.artifact_id.startswith("transcript_"), "Transcript ID changed"
    print("✅ Original transcript not mutated")
    
    print("\n✅ All extract stage tests passed")


if __name__ == '__main__':
    test_extract()
