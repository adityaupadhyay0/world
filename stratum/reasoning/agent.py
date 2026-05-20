import logging
from typing import Dict, Any, List, Optional
from stratum.state.manager import StateManager
from stratum.reasoning.serializer import StateSerializer
from stratum.reasoning.parser import UpdateParser
from stratum.reasoning.verifier import CausalVerifier
from stratum.reasoning.detector import ContradictionDetector

class ReasoningAgent:
    def __init__(self, state_manager: StateManager, llm_client=None):
        self.state_manager = state_manager
        self.llm_client = llm_client # In a real scenario, this would be an OpenAI/Anthropic client
        self.serializer = StateSerializer()
        self.parser = UpdateParser()
        self.verifier = CausalVerifier()
        self.detector = ContradictionDetector()
        self.logger = logging.getLogger(__name__)

    def process_event(self, event_description: str, entity_ids: List[str]):
        """
        1. Read state
        2. Check contradictions
        3. Prompt LLM (Mocked for Phase 2 implementation)
        4. Parse response
        5. Verify causal consistency
        6. Commit update
        """
        # 1. Read State
        current_snapshot = self.state_manager.get_state_snapshot(entity_ids)

        # 2. Contradiction Detection
        conflicts = self.detector.detect_contradictions(current_snapshot)
        if conflicts:
            self.logger.warning(f"Contradictions detected before reasoning: {conflicts}")
            # In Phase 3+, we might ask the LLM to resolve these first

        # 3. Prompting (Mocked or using provided client)
        serialized_state = self.serializer.serialize_to_json(current_snapshot)
        prompt = self._build_prompt(serialized_state, event_description)

        # Here we would call the LLM. For now, we simulate the logic or use llm_client if provided.
        llm_response = self._get_llm_response(prompt, event_description, current_snapshot)

        # 4. Parse
        proposed_update = self.parser.parse_llm_response(llm_response)

        # 5. Verify
        violations = self.verifier.verify_update(current_snapshot, proposed_update)
        if violations:
            self.logger.error(f"Causal violations in LLM update: {violations}")
            # Re-prompting logic would go here in Phase 2/3
            raise ValueError(f"Causal violations: {violations}")

        # 6. Commit
        self.state_manager.validate_and_commit_update(proposed_update, cause=event_description)
        return proposed_update

    def _build_prompt(self, state_json: str, event: str) -> str:
        return f"""
SYSTEM: You are a world state updater. Your job is to update the world
        state based on the event. You MUST return valid JSON matching
        the schema. You CANNOT change entity types or relations not
        directly affected by this event.

STATE:  {state_json}

EVENT:  {event}

OUTPUT: JSON state delta (full entity data for updated entities)
"""

    def _get_llm_response(self, prompt: str, event: str, state: Dict[str, Any]) -> str:
        if self.llm_client:
            return self.llm_client.generate(prompt)

        # Fallback Mock Logic for testing Phase 2 without a real API key
        self.logger.info(f"Mocking LLM response for event: {event}")
        # Basic heuristic mock
        if "quit" in event.lower() or "resign" in event.lower():
             # Find an employee and remove them or mark them?
             # Our schema doesn't have 'active' status yet, so maybe we just don't return them.
             # Actually, StateWriter should handle deletion if we wanted, but let's just update morale to 0
             for ent in state['entities']:
                 if ent['type'] == 'Employee':
                     ent['morale'] = 0.0
                     return json.dumps({"entities": [ent]})

        if "progress" in event.lower() or "work" in event.lower():
             for ent in state['entities']:
                 if ent['type'] == 'Project':
                     ent['progress'] = min(1.0, ent['progress'] + 0.1)
                     return json.dumps({"entities": [ent]})

        return json.dumps({"entities": []})
