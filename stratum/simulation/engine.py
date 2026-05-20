from typing import List, Dict, Any
import copy
from stratum.state.manager import StateManager
from stratum.reasoning.agent import ReasoningAgent

class ForwardSimulator:
    def __init__(self, reasoning_agent: ReasoningAgent):
        self.agent = reasoning_agent

    def simulate_steps(self, initial_entity_ids: List[str], n_steps: int = 5) -> List[Dict[str, Any]]:
        """
        Predicts future states by recursively asking the reasoning agent
        "What happens next?" based on current trajectories.
        """
        trajectory = []
        # In a real implementation, we might fork the StateManager/WorldState to avoid polluting truth
        # For MVP, we'll just simulate the data flow

        current_ids = initial_entity_ids
        for i in range(n_steps):
            # We simulate a "Time passes" event
            prediction = self.agent.process_event(f"Simulation step {i+1}: 1 week passes.", current_ids)
            trajectory.append(prediction)

        return trajectory

class CounterfactualEngine:
    def __init__(self, reasoning_agent: ReasoningAgent):
        self.agent = reasoning_agent

    def what_if(self, hypothetical_event: str, entity_ids: List[str]) -> Dict[str, Any]:
        """
        Simulates the consequences of a hypothetical event.
        """
        # We process the event but potentially in a 'sandbox' mode.
        # For now, we use the agent to generate the delta.
        return self.agent.process_event(f"HYPOTHETICAL: {hypothetical_event}", entity_ids)
