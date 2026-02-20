"""
Artifact Data Model

Defines structure for knowledge artifacts.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class Artifact:
    """Represents a knowledge artifact."""
    
    artifact_id: str
    type: str
    content: Dict[str, Any]
    derived_from: List[str] = field(default_factory=list)
    referenced_context: List[str] = field(default_factory=list)
    confidence: float = 0.0
    stage_metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "draft"
    version: int = 1
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert artifact to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of artifact
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Artifact':
        """
        Create artifact from dictionary.
        
        Args:
            data: Dictionary containing artifact data
            
        Returns:
            Artifact instance
        """
        return cls(**data)
    
    def increment_version(self) -> None:
        """Increment artifact version."""
        self.version += 1
