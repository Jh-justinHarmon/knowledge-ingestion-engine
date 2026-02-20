"""
Artifact Store

Handles persistence of processed artifacts.
"""

import json
from pathlib import Path
from typing import List


class ArtifactStore:
    """Stores and retrieves artifacts in append-only fashion."""
    
    def __init__(self, artifacts_dir: str = "artifacts"):
        """
        Initialize artifact store.
        
        Args:
            artifacts_dir: Directory for artifact files
        """
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    def save_artifact(self, artifact) -> None:
        """
        Save artifact to storage (append-only, no overwrites).
        
        Args:
            artifact: Artifact instance
            
        Raises:
            FileExistsError: If artifact file already exists
        """
        artifact_path = self.artifacts_dir / f"{artifact.artifact_id}.json"
        
        # Enforce append-only: raise error if file exists
        if artifact_path.exists():
            raise FileExistsError(
                f"Artifact {artifact.artifact_id} already exists. "
                "No overwrites allowed (append-only store)."
            )
        
        # Serialize and write
        artifact_dict = artifact.to_dict()
        with open(artifact_path, 'w') as f:
            json.dump(artifact_dict, f, indent=2)
    
    def load_artifact(self, artifact_id: str):
        """
        Load artifact from storage.
        
        Args:
            artifact_id: Artifact ID to load
            
        Returns:
            Artifact instance
            
        Raises:
            FileNotFoundError: If artifact does not exist
        """
        from models.artifact import Artifact
        
        artifact_path = self.artifacts_dir / f"{artifact_id}.json"
        
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"Artifact {artifact_id} not found in {self.artifacts_dir}"
            )
        
        # Load and deserialize
        with open(artifact_path, 'r') as f:
            artifact_dict = json.load(f)
        
        return Artifact.from_dict(artifact_dict)
    
    def list_versions(self, base_name: str) -> List[str]:
        """
        List all artifact IDs matching a base name prefix.
        
        Args:
            base_name: Prefix to match (e.g., "art_001")
            
        Returns:
            Sorted list of artifact IDs
        """
        matching_ids = []
        
        for artifact_file in self.artifacts_dir.glob(f"{base_name}*.json"):
            artifact_id = artifact_file.stem  # Remove .json extension
            matching_ids.append(artifact_id)
        
        return sorted(matching_ids)
