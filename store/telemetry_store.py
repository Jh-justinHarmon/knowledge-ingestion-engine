"""
Telemetry Store

Handles persistence of pipeline telemetry.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Union


class TelemetryStore:
    """Stores telemetry events in append-only JSONL files."""
    
    def __init__(self, telemetry_dir: str = "telemetry"):
        """
        Initialize telemetry store.
        
        Args:
            telemetry_dir: Directory for telemetry files
        """
        self.telemetry_dir = Path(telemetry_dir)
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)
    
    def append_event(self, event) -> None:
        """
        Append telemetry event to date-based JSONL file.
        
        Args:
            event: TelemetryEvent instance or dict
        """
        # Get current date for filename
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        log_file = self.telemetry_dir / f"{date_str}.jsonl"
        
        # Convert event to dict if needed
        if hasattr(event, 'to_dict'):
            event_dict = event.to_dict()
        else:
            event_dict = event
        
        # Append to JSONL file
        with open(log_file, 'a') as f:
            f.write(json.dumps(event_dict) + '\n')
