from typing import Dict, Any, List, Set
from stratum.ontology.schema import Entity

class BeliefState:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.known_entities: Dict[str, Dict[str, Any]] = {}
        self.known_relations: List[Dict[str, Any]] = []

    def update_belief(self, observation: Dict[str, Any]):
        """
        Updates the agent's private beliefs based on an observation.
        """
        for ent in observation.get('entities', []):
            self.known_entities[ent['id']] = ent

        for rel in observation.get('relations', []):
            self.known_relations.append(rel)

    def get_perceived_state(self) -> Dict[str, Any]:
        return {
            "entities": list(self.known_entities.values()),
            "relations": self.known_relations
        }

class Agent:
    def __init__(self, agent_id: str, role: str):
        self.agent_id = agent_id
        self.role = role
        self.beliefs = BeliefState(agent_id)

    def observe(self, partial_state: Dict[str, Any]):
        self.beliefs.update_belief(partial_state)

    def reason_over_beliefs(self, reasoning_agent_interface):
        # The agent uses their private beliefs to decide on an action
        perceived = self.beliefs.get_perceived_state()
        # ... logic to call reasoning agent with perceived state instead of ground truth
        pass
