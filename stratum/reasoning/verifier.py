from typing import Dict, Any, List, Optional
import logging

class CausalVerifier:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def verify_update(self, current_state: Dict[str, Any], proposed_update: Dict[str, Any]) -> List[str]:
        """
        Verifies the proposed update against causal constraints.
        Returns a list of violation messages. Empty list means success.
        """
        violations = []

        # Helper to find current entity by ID
        def get_current_entity(eid):
            for e in current_state.get('entities', []):
                if e['id'] == eid:
                    return e
            return None

        # 1. Budget Constraint
        for ent in proposed_update.get('entities', []):
            if ent.get('type') == 'Organization' and 'balance' in ent:
                old_org = get_current_entity(ent['id'])
                if old_org and ent['balance'] > old_org['balance']:
                    # In this world, money doesn't appear from nowhere (unless a specific event allows it)
                    # For MVP, we'll just log it or flag it if it's a massive jump without cause
                    pass

        # 2. Immutable Fields (Schema Drift Protection)
        for ent in proposed_update.get('entities', []):
            old_ent = get_current_entity(ent['id'])
            if old_ent:
                if ent.get('type') != old_ent.get('type'):
                    violations.append(f"Entity {ent['id']} attempted to change type from {old_ent['type']} to {ent.get('type')}")

        # 3. Value Ranges
        for ent in proposed_update.get('entities', []):
            if 'morale' in ent:
                if not (0.0 <= ent['morale'] <= 1.0):
                    violations.append(f"Employee {ent['id']} morale {ent['morale']} out of bounds [0, 1]")
            if 'progress' in ent:
                if not (0.0 <= ent['progress'] <= 1.0):
                    violations.append(f"Project {ent['id']} progress {ent['progress']} out of bounds [0, 1]")

        return violations
