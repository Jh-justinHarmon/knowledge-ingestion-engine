#!/usr/bin/env python3
"""
Test insight stage.
"""

from stages.normalize import normalize
from stages.extract import extract
from stages.context import contextualize
from stages.insight import generate_insight


def test_insight():
    """Test insight stage with contextualized artifact."""
    
    # Create sample transcript
    raw_text = """
John Smith: We will implement the new feature for the meeting next week.

Jane Doe: I agree with that project timeline.

John Smith: The conversation about action items is clear.
"""
    
    print("=" * 80)
    print("INSIGHT STAGE TEST")
    print("=" * 80)
    
    # Step 1: Normalize
    print("\nStep 1: Normalize transcript")
    transcript = normalize(raw_text, run_id="test_insight")
    print(f"  ✅ Created transcript: {transcript.artifact_id}")
    
    # Step 2: Extract
    print("\nStep 2: Extract structured data")
    extraction = extract(transcript, run_id="test_insight")
    print(f"  ✅ Created extraction: {extraction.artifact_id}")
    print(f"     Tasks: {len(extraction.content['tasks'])}")
    print(f"     Decisions: {len(extraction.content['decisions'])}")
    
    # Step 3: Contextualize
    print("\nStep 3: Contextualize extraction")
    contextualized = contextualize(extraction, run_id="test_insight")
    print(f"  ✅ Created contextualized: {contextualized.artifact_id}")
    print(f"     Confidence: {contextualized.confidence}")
    print(f"     Referenced contexts: {len(contextualized.referenced_context)}")
    
    # Step 4: Generate insight
    print("\nStep 4: Generate insight")
    insight = generate_insight(contextualized, run_id="test_insight")
    
    print("\n" + "=" * 80)
    print("INSIGHT ARTIFACT")
    print("=" * 80)
    print(f"Artifact ID: {insight.artifact_id}")
    print(f"Type: {insight.type}")
    print(f"Status: {insight.status}")
    print(f"Version: {insight.version}")
    print(f"Confidence: {insight.confidence} (was {contextualized.confidence})")
    print(f"Derived from: {insight.derived_from}")
    print(f"Referenced context: {insight.referenced_context}")
    
    print("\nStage metadata:")
    for key, value in insight.stage_metadata.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("INSIGHT CONTENT")
    print("=" * 80)
    
    print("\nRecommendations:")
    for rec in insight.content['recommendations']:
        print(f"  - {rec}")
    
    print(f"\nRisk flags: {insight.content['risk_flags']}")
    print(f"\nSource summary: {insight.content['source_summary']}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Check artifact structure
    assert insight.type == "insight", "Incorrect type"
    assert insight.status == "draft", "Incorrect status"
    assert insight.version == 1, "Incorrect version"
    print("✅ Artifact structure correct")
    
    # Check derived_from
    assert len(insight.derived_from) == 1, "Should have 1 parent"
    assert insight.derived_from[0] == contextualized.artifact_id, "Incorrect parent ID"
    print("✅ Derived_from tracking correct")
    
    # Check stage metadata
    assert insight.stage_metadata["model"] == "deterministic_interpretation", "Incorrect model"
    assert insight.stage_metadata["tokens"] == 0, "Incorrect token count"
    assert insight.stage_metadata["cost_usd"] == 0.0, "Incorrect cost"
    assert insight.stage_metadata["latency_ms"] >= 0, "Invalid latency"
    print("✅ Stage metadata correct")
    
    # Check referenced_context preservation
    assert insight.referenced_context == contextualized.referenced_context, "Referenced context not preserved"
    print("✅ Referenced context preserved")
    
    # Check recommendations logic
    recommendations = insight.content['recommendations']
    assert isinstance(recommendations, list), "Recommendations should be list"
    
    # Should have task recommendation since extraction has tasks
    has_task_rec = any("task" in rec.lower() for rec in recommendations)
    assert has_task_rec, "Should have task recommendation"
    print("✅ Task recommendation generated")
    
    # Should have decision recommendation since extraction has decisions
    has_decision_rec = any("decision" in rec.lower() for rec in recommendations)
    assert has_decision_rec, "Should have decision recommendation"
    print("✅ Decision recommendation generated")
    
    # Check risk flags logic
    risk_flags = insight.content['risk_flags']
    assert isinstance(risk_flags, list), "Risk flags should be list"
    
    # Check if low_confidence flag is set correctly
    if contextualized.confidence < 0.88:
        assert "low_confidence" in risk_flags, "Should have low_confidence flag"
        print("✅ Low confidence flag set correctly")
    else:
        assert "low_confidence" not in risk_flags, "Should not have low_confidence flag"
        print("✅ No low confidence flag (confidence >= 0.88)")
    
    # Check confidence adjustment
    expected_confidence = max(contextualized.confidence - 0.03, 0.70)
    assert abs(insight.confidence - expected_confidence) < 0.001, "Confidence calculation incorrect"
    print(f"✅ Confidence adjusted correctly (-0.03, floored at 0.70)")
    
    # Check source_summary preservation
    assert insight.content['source_summary'] == contextualized.content['summary'], "Source summary not preserved"
    print("✅ Source summary preserved")
    
    # Check that contextualized was not mutated
    assert contextualized.type == "contextualized_extraction", "Contextualized type changed"
    print("✅ Original contextualized artifact not mutated")
    
    print("\n✅ All insight stage tests passed")


if __name__ == '__main__':
    test_insight()
