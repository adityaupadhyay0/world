from typing import Dict, Any, List
import math
from datetime import datetime, timezone

class TemporalDecay:
    @staticmethod
    def apply_decay(value: float, last_updated: datetime, decay_rate: float = 0.01) -> float:
        """
        Applies exponential decay based on time elapsed.
        """
        now = datetime.now(timezone.utc)
        delta = (now - last_updated).total_seconds() / 3600.0 # decay per hour
        return value * math.exp(-decay_rate * delta)

class SaliencyScorer:
    @staticmethod
    def score_event(event: Dict[str, Any]) -> float:
        """
        Determines how important an event is.
        """
        # Simple heuristic: updates to projects or organizational balance are high saliency
        etype = event.get('event_type')
        if etype == 'ENTITY_CREATED':
            return 0.8
        if etype == 'RELATION_ADDED':
            return 0.6

        data = event.get('data', {})
        if isinstance(data, dict) and 'new' in data:
            new_val = data['new']
            if new_val.get('type') == 'Organization':
                return 0.9
            if new_val.get('type') == 'Project' and new_val.get('status') == 'FAILED':
                return 1.0

        return 0.3
