#!/usr/bin/env python3
"""
Test full pipeline orchestration.
"""

from pipeline import run_pipeline


def test_pipeline():
    """Test complete pipeline execution."""
    
    # Sample raw transcript
    raw_text = """
John Smith: We will implement the new feature for the meeting next week.

Jane Doe: I agree with that project timeline.

John Smith: The conversation about action items is clear.

Jane Doe: We decided to move forward with the proposal.
"""
    
    print("=" * 80)
    print("FULL PIPELINE TEST")
    print("=" * 80)
    
    print("\nRunning complete pipeline...")
    print("  Stage 1: Normalize")
    print("  Stage 2: Extract")
    print("  Stage 3: Contextualize")
    print("  Stage 4: Generate Insight")
    print("  Stage 5: Validate")
    
    # Run full pipeline
    artifacts = run_pipeline(raw_text, run_id="test_pipeline")
    
    # Extract validated artifact
    result = artifacts["validated"]
    
    print("\n" + "=" * 80)
    print("PIPELINE RESULT")
    print("=" * 80)
    print(f"Final artifact ID: {result.artifact_id}")
    print(f"Type: {result.type}")
    print(f"Status: {result.status}")
    print(f"Version: {result.version}")
    print(f"Confidence: {result.confidence}")
    
    print("\n" + "=" * 80)
    print("ARTIFACT LINEAGE")
    print("=" * 80)
    print(f"Derived from: {result.derived_from}")
    print(f"Referenced context: {result.referenced_context}")
    
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print(f"Validation score: {result.content['validation_score']}")
    print(f"Hallucination risk: {result.content['hallucination_risk']}")
    
    print("\nRecommendations:")
    for rec in result.content['recommendations']:
        print(f"  - {rec}")
    
    print(f"\nRisk flags: {result.content['risk_flags']}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Verify final artifact type
    assert result.type == "validated_insight", "Final artifact should be validated_insight"
    print("✅ Final artifact type correct")
    
    # Verify status is set
    assert result.status in ["validated", "review_required"], "Status should be validated or review_required"
    print(f"✅ Status set: {result.status}")
    
    # Verify content structure
    assert "recommendations" in result.content, "Should have recommendations"
    assert "risk_flags" in result.content, "Should have risk_flags"
    assert "validation_score" in result.content, "Should have validation_score"
    assert "hallucination_risk" in result.content, "Should have hallucination_risk"
    print("✅ Content structure complete")
    
    # Verify lineage tracking
    assert len(result.derived_from) == 1, "Should have 1 parent (insight artifact)"
    assert result.derived_from[0].startswith("insight_"), "Parent should be insight artifact"
    print("✅ Lineage tracking correct")
    
    # Verify referenced context
    assert isinstance(result.referenced_context, list), "Referenced context should be list"
    print(f"✅ Referenced {len(result.referenced_context)} context(s)")
    
    # Verify confidence/validation_score
    assert result.confidence == result.content['validation_score'], "Confidence should equal validation_score"
    assert result.confidence >= 0.60, "Confidence should be >= 0.60 (floor)"
    print("✅ Confidence/validation_score correct")
    
    # Verify recommendations generated
    assert len(result.content['recommendations']) > 0, "Should have recommendations"
    print(f"✅ Generated {len(result.content['recommendations'])} recommendation(s)")
    
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 80)
    print(f"✅ All 5 stages executed successfully")
    print(f"✅ Final artifact: {result.artifact_id}")
    print(f"✅ Status: {result.status}")
    print(f"✅ Validation score: {result.content['validation_score']:.2f}")
    
    print("\n✅ All pipeline tests passed")


if __name__ == '__main__':
    test_pipeline()
