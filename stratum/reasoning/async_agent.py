import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from litellm import acompletion
from stratum.state.async_manager import AsyncStateManager
from stratum.reasoning.serializer import StateSerializer
from stratum.reasoning.parser import UpdateParser
from stratum.reasoning.verifier import CausalVerifier
from stratum.reasoning.detector import ContradictionDetector

class AsyncReasoningAgent:
    def __init__(self, state_manager: AsyncStateManager, model: str = "gpt-4o"):
        self.state_manager = state_manager
        self.model = model
        self.serializer = StateSerializer()
        self.parser = UpdateParser()
        self.verifier = CausalVerifier()
        self.detector = ContradictionDetector()
        self.logger = logging.getLogger(__name__)

    async def process_event(self, event_description: str, entity_ids: List[str]):
        current_snapshot = self.state_manager.get_state_snapshot(entity_ids)

        conflicts = self.detector.detect_contradictions(current_snapshot)
        if conflicts:
            self.logger.warning(f"Contradictions detected: {conflicts}")

        serialized_state = self.serializer.serialize_to_json(current_snapshot)
        prompt = self._build_prompt(serialized_state, event_description)

        # Real LLM Call via LiteLLM
        try:
            response = await acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            llm_response = response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            # Fallback to mock if needed, or re-raise
            raise

        proposed_update = self.parser.parse_llm_response(llm_response)

        violations = self.verifier.verify_update(current_snapshot, proposed_update)
        if violations:
            raise ValueError(f"Causal violations: {violations}")

        await self.state_manager.validate_and_commit_update(proposed_update, cause=event_description)
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
