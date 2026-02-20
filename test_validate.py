#!/usr/bin/env python3
"""
Test validation stage.
"""

from stages.normalize import normalize
from stages.extract import extract
from stages.context import contextualize
from stages.insight import generate_insight
from stages.validate import validate


def test_validate():
    """Test validation stage with insight artifact."""
    
    # Create sample transcript
    raw_text = """
John Smith: We will implement the new feature for the meeting next week.

Jane Doe: I agree with that project timeline.

John Smith: The conversation about action items is clear.
"""
    
    print("=" * 80)
    print("VALIDATION STAGE TEST")
    print("=" * 80)
    
    # Step 1: Normalize
    print("\nStep 1: Normalize transcript")
    transcript = normalize(raw_text, run_id="test_validate")
    print(f"  ✅ Created transcript: {transcript.artifact_id}")
    
    # Step 2: Extract
    print("\nStep 2: Extract structured data")
    extraction = extract(transcript, run_id="test_validate")
    print(f"  ✅ Created extraction: {extraction.artifact_id}")
    
    # Step 3: Contextualize
    print("\nStep 3: Contextualize extraction")
    contextualized = contextualize(extraction, run_id="test_validate")
    print(f"  ✅ Created contextualized: {contextualized.artifact_id}")
    print(f"     Referenced contexts: {len(contextualized.referenced_context)}")
    
    # Step 4: Generate insight
    print("\nStep 4: Generate insight")
    insight = generate_insight(contextualized, run_id="test_validate")
    print(f"  ✅ Created insight: {insight.artifact_id}")
    print(f"     Confidence: {insight.confidence}")
    print(f"     Risk flags: {insight.content['risk_flags']}")
    
    # Step 5: Validate
    print("\nStep 5: Validate insight")
    validated = validate(insight, run_id="test_validate")
    
    print("\n" + "=" * 80)
    print("VALIDATED ARTIFACT")
    print("=" * 80)
    print(f"Artifact ID: {validated.artifact_id}")
    print(f"Type: {validated.type}")
    print(f"Status: {validated.status}")
    print(f"Version: {validated.version}")
    print(f"Confidence: {validated.confidence} (validation_score)")
    print(f"Derived from: {validated.derived_from}")
    print(f"Referenced context: {validated.referenced_context}")
    
    print("\nStage metadata:")
    for key, value in validated.stage_metadata.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("VALIDATION CONTENT")
    print("=" * 80)
    
    print("\nRecommendations:")
    for rec in validated.content['recommendations']:
        print(f"  - {rec}")
    
    print(f"\nRisk flags: {validated.content['risk_flags']}")
    print(f"Validation score: {validated.content['validation_score']}")
    print(f"Hallucination risk: {validated.content['hallucination_risk']}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Check artifact structure
    assert validated.type == "validated_insight", "Incorrect type"
    assert validated.version == 1, "Incorrect version"
    print("✅ Artifact structure correct")
    
    # Check derived_from
    assert len(validated.derived_from) == 1, "Should have 1 parent"
    assert validated.derived_from[0] == insight.artifact_id, "Incorrect parent ID"
    print("✅ Derived_from tracking correct")
    
    # Check stage metadata
    assert validated.stage_metadata["model"] == "deterministic_validation", "Incorrect model"
    assert validated.stage_metadata["tokens"] == 0, "Incorrect token count"
    assert validated.stage_metadata["cost_usd"] == 0.0, "Incorrect cost"
    assert validated.stage_metadata["latency_ms"] >= 0, "Invalid latency"
    print("✅ Stage metadata correct")
    
    # Check referenced_context preservation
    assert validated.referenced_context == insight.referenced_context, "Referenced context not preserved"
    print("✅ Referenced context preserved")
    
    # Check validation score computation
    expected_score = insight.confidence
    if "low_confidence" in insight.content.get("risk_flags", []):
        expected_score -= 0.05
    if not insight.referenced_context:
        expected_score -= 0.05
    expected_score = max(expected_score, 0.60)
    
    assert abs(validated.content['validation_score'] - expected_score) < 0.001, "Validation score incorrect"
    print(f"✅ Validation score computed correctly: {validated.content['validation_score']}")
    
    # Check hallucination risk assessment
    hallucination_risk = validated.content['hallucination_risk']
    assert hallucination_risk in ["low", "medium"], "Invalid hallucination risk value"
    
    if not insight.referenced_context:
        assert hallucination_risk == "medium", "Should be medium risk (no context)"
    elif insight.confidence < 0.80:
        assert hallucination_risk == "medium", "Should be medium risk (low confidence)"
    else:
        assert hallucination_risk == "low", "Should be low risk"
    print(f"✅ Hallucination risk assessed correctly: {hallucination_risk}")
    
    # Check status determination
    if validated.content['validation_score'] >= 0.85:
        assert validated.status == "validated", "Should be validated"
        print("✅ Status: validated (score >= 0.85)")
    else:
        assert validated.status == "review_required", "Should be review_required"
        print("✅ Status: review_required (score < 0.85)")
    
    # Check confidence equals validation_score
    assert validated.confidence == validated.content['validation_score'], "Confidence should equal validation_score"
    print("✅ Confidence equals validation_score")
    
    # Check recommendations preservation
    assert validated.content['recommendations'] == insight.content['recommendations'], "Recommendations not preserved"
    print("✅ Recommendations preserved")
    
    # Check risk_flags preservation
    assert validated.content['risk_flags'] == insight.content['risk_flags'], "Risk flags not preserved"
    print("✅ Risk flags preserved")
    
    # Check that insight was not mutated
    assert insight.type == "insight", "Insight type changed"
    print("✅ Original insight artifact not mutated")
    
    print("\n✅ All validation stage tests passed")


if __name__ == '__main__':
    test_validate()
