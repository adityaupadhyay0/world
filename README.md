# STRATUM — Structured Temporal Reasoning and Update Model

STRATUM is a high-fidelity world model framework designed for LLM agents. It maintains a stable, causally consistent, and persistent representation of reality that agents can query and update.

## Core Features
- **Structured Ontology:** Pydantic-based schemas with a dynamic registry to prevent model drift.
- **Persistent State Engine:** Graph-based world representation (NetworkX) and an append-only event log (SQLite).
- **Causal Consistency:** Automatic verification of LLM-proposed updates against domain rules and physical constraints.
- **Three-Tier Memory:** Hot (recent), Warm (summaries), and Cold (vector-indexed episodic memory via ChromaDB).
- **Simulation & Prediction:** Forward-predict trajectories and run counterfactual "What If?" scenarios.
- **Multi-Agent Believability:** Support for private belief states and information asymmetry.
- **Async First:** Fully non-blocking architecture using `asyncio` and `aiosqlite`.

## Quick Start

```python
import asyncio
from stratum.state.world_state import WorldState
from stratum.state.async_event_log import AsyncEventLog
from stratum.state.async_manager import AsyncStateManager
from stratum.reasoning.async_agent import AsyncReasoningAgent
from stratum.ontology.schema import Organization

async def main():
    # Setup
    ws = WorldState()
    el = AsyncEventLog()
    sm = AsyncStateManager(ws, el)
    await sm.initialize()

    # Initialize World
    await sm.create_entity(Organization(id="org_1", name="FutureWorks", balance=1000000))

    # Reasoning Loop
    agent = AsyncReasoningAgent(sm)
    await agent.process_event("A global recession begins.", ["org_1"])

if __name__ == "__main__":
    asyncio.run(main())
```

## Architecture
1. **Ontology Layer:** Defines *what exists*.
2. **State Layer:** Tracks *what is true right now*.
3. **Reasoning Layer:** Cognitive interface (LLM) to update and simulate the world.

## Metrics & Evaluation
Use the `EvaluationHarness` to measure:
- **Coherence Score:** Rate of contradictions over time.
- **Causal Fidelity:** Adherence to physical/logical rules.
- **Memory Efficiency:** Growth and retrieval accuracy.
