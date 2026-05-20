from typing import Dict, Any, List
import logging

class ContradictionDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def detect_contradictions(self, state: Dict[str, Any]) -> List[str]:
        """
        Runs a lightweight contradiction check over a state slice.
        """
        contradictions = []
        entities = state.get('entities', [])

        # Example: Duplicate IDs with different data
        ids = {}
        for ent in entities:
            eid = ent['id']
            if eid in ids:
                if ent != ids[eid]:
                    contradictions.append(f"Contradicting data for entity ID {eid}")
            ids[eid] = ent

        # Example: Logic contradictions
        for ent in entities:
            if ent.get('type') == 'Project':
                if ent.get('status') == 'COMPLETED' and ent.get('progress', 0) < 1.0:
                    contradictions.append(f"Project {ent['id']} is COMPLETED but progress is {ent.get('progress')}")
                if ent.get('status') == 'FAILED' and ent.get('progress', 0) >= 1.0:
                    contradictions.append(f"Project {ent['id']} is FAILED but progress is {ent.get('progress')}")

        return contradictions
