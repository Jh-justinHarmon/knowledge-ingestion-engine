#!/usr/bin/env python3
"""
Quick test for telemetry model and store.
"""

from models.telemetry import TelemetryEvent
from store.telemetry_store import TelemetryStore


def test_telemetry():
    """Test telemetry event creation and storage."""
    
    # Create telemetry event
    event = TelemetryEvent(
        run_id="test_run_001",
        stage="normalize",
        input_artifact_id="art_001",
        output_artifact_id="art_002",
        latency_ms=150,
        cost_usd=0.0,
        replayable=True
    )
    
    print("Created event:")
    print(f"  run_id: {event.run_id}")
    print(f"  stage: {event.stage}")
    print(f"  timestamp: {event.timestamp}")
    print(f"  replayable: {event.replayable}")
    
    # Initialize store
    store = TelemetryStore(telemetry_dir="telemetry")
    
    # Append event
    store.append_event(event)
    print("\n✅ Event written to JSONL")
    
    # Create second event
    event2 = TelemetryEvent(
        run_id="test_run_001",
        stage="extract",
        input_artifact_id="art_002",
        output_artifact_id="art_003",
        latency_ms=200,
        cost_usd=0.001,
        replayable=True
    )
    
    store.append_event(event2)
    print("✅ Second event written to JSONL")
    
    print("\nTelemetry test complete.")


if __name__ == '__main__':
    test_telemetry()
