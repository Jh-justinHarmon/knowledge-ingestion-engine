"""
Telemetry Data Model

Defines structure for pipeline telemetry.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class TelemetryEvent:
    """Represents a telemetry event."""
    
    run_id: str
    stage: str
    input_artifact_id: str
    output_artifact_id: Optional[str] = None
    latency_ms: int = 0
    cost_usd: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    replayable: bool = True
    replay_of: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of event
        """
        return asdict(self)
