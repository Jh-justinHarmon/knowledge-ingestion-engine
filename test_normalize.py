#!/usr/bin/env python3
"""
Test normalize stage.
"""

from stages.normalize import normalize


def test_normalize():
    """Test normalize stage with sample input."""
    
    # Sample raw transcript with various speaker formats
    raw_text = """
    
    
John Smith: Hello, this is a test transcript.


Jane Doe: Yes, I agree with that assessment.

John Smith: Let me add some more context here.


Jane Doe: That makes sense to me.


Moderator: Thank you both for your input.

    
    """
    
    print("=" * 80)
    print("NORMALIZE STAGE TEST")
    print("=" * 80)
    
    print("\nRaw input:")
    print(repr(raw_text))
    
    # Run normalize
    artifact = normalize(raw_text, run_id="test_run_normalize")
    
    print("\n" + "=" * 80)
    print("ARTIFACT CREATED")
    print("=" * 80)
    print(f"Artifact ID: {artifact.artifact_id}")
    print(f"Type: {artifact.type}")
    print(f"Status: {artifact.status}")
    print(f"Version: {artifact.version}")
    print(f"Confidence: {artifact.confidence}")
    print(f"Derived from: {artifact.derived_from}")
    print(f"Referenced context: {artifact.referenced_context}")
    
    print("\nStage metadata:")
    for key, value in artifact.stage_metadata.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("NORMALIZED TEXT")
    print("=" * 80)
    print(artifact.content["text"])
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    normalized_text = artifact.content["text"]
    
    # Check speaker standardization
    assert "Speaker 1:" in normalized_text, "Speaker 1 not found"
    assert "Speaker 2:" in normalized_text, "Speaker 2 not found"
    assert "Speaker 3:" in normalized_text, "Speaker 3 not found"
    assert "John Smith:" not in normalized_text, "Original speaker name still present"
    assert "Jane Doe:" not in normalized_text, "Original speaker name still present"
    print("✅ Speaker labels standardized correctly")
    
    # Check whitespace normalization
    assert not normalized_text.startswith('\n'), "Leading whitespace not stripped"
    assert not normalized_text.endswith('\n'), "Trailing whitespace not stripped"
    assert '\n\n\n' not in normalized_text, "Multiple blank lines not normalized"
    print("✅ Whitespace normalized correctly")
    
    # Check artifact structure
    assert artifact.type == "transcript", "Incorrect artifact type"
    assert artifact.status == "draft", "Incorrect status"
    assert artifact.version == 1, "Incorrect version"
    assert artifact.confidence == 0.95, "Incorrect confidence"
    print("✅ Artifact structure correct")
    
    # Check stage metadata
    assert artifact.stage_metadata["model"] == "deterministic", "Incorrect model"
    assert artifact.stage_metadata["tokens"] == 0, "Incorrect token count"
    assert artifact.stage_metadata["cost_usd"] == 0.0, "Incorrect cost"
    assert artifact.stage_metadata["latency_ms"] >= 0, "Invalid latency"
    print("✅ Stage metadata correct")
    
    print("\n✅ All normalize stage tests passed")


if __name__ == '__main__':
    test_normalize()
