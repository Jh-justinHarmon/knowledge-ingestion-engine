#!/usr/bin/env python3
"""
Test artifact store operations.
"""

from models.artifact import Artifact
from store.artifact_store import ArtifactStore


def test_artifact_store():
    """Test save, load, and list_versions operations."""
    
    store = ArtifactStore(artifacts_dir="artifacts")
    
    # Test 1: Save artifact
    print("Test 1: Save artifact")
    artifact1 = Artifact(
        artifact_id="art_001_v1",
        type="transcript",
        content={"text": "Sample content"},
        confidence=0.95
    )
    
    store.save_artifact(artifact1)
    print(f"  ✅ Saved {artifact1.artifact_id}")
    print(f"     Status: {artifact1.status}")
    print(f"     Version: {artifact1.version}")
    
    # Test 2: Load artifact
    print("\nTest 2: Load artifact")
    loaded = store.load_artifact("art_001_v1")
    print(f"  ✅ Loaded {loaded.artifact_id}")
    print(f"     Type: {loaded.type}")
    print(f"     Confidence: {loaded.confidence}")
    print(f"     Content: {loaded.content}")
    
    # Test 3: Attempt to overwrite (should fail)
    print("\nTest 3: Attempt overwrite (should fail)")
    try:
        store.save_artifact(artifact1)
        print("  ❌ ERROR: Overwrite was allowed!")
    except FileExistsError as e:
        print(f"  ✅ Correctly blocked overwrite: {e}")
    
    # Test 4: Save multiple versions
    print("\nTest 4: Save multiple versions")
    artifact2 = Artifact(
        artifact_id="art_001_v2",
        type="transcript",
        content={"text": "Updated content"},
        confidence=0.98
    )
    artifact2.increment_version()
    
    artifact3 = Artifact(
        artifact_id="art_002_v1",
        type="summary",
        content={"summary": "Different artifact"},
        confidence=0.85
    )
    
    store.save_artifact(artifact2)
    store.save_artifact(artifact3)
    print(f"  ✅ Saved {artifact2.artifact_id}")
    print(f"  ✅ Saved {artifact3.artifact_id}")
    
    # Test 5: List versions
    print("\nTest 5: List versions with prefix 'art_001'")
    versions = store.list_versions("art_001")
    print(f"  Found {len(versions)} versions:")
    for v in versions:
        print(f"    - {v}")
    
    print("\nTest 6: List all artifacts with prefix 'art_'")
    all_artifacts = store.list_versions("art_")
    print(f"  Found {len(all_artifacts)} artifacts:")
    for a in all_artifacts:
        print(f"    - {a}")
    
    # Test 7: Load non-existent artifact (should fail)
    print("\nTest 7: Load non-existent artifact (should fail)")
    try:
        store.load_artifact("art_999")
        print("  ❌ ERROR: Non-existent artifact was loaded!")
    except FileNotFoundError as e:
        print(f"  ✅ Correctly raised error: {e}")
    
    print("\n✅ All artifact store tests passed")


if __name__ == '__main__':
    test_artifact_store()
