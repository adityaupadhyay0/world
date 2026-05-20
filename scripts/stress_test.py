import logging
import os
from stratum.state.world_state import WorldState
from stratum.state.event_log import EventLog
from stratum.state.manager import StateManager
from stratum.reasoning.agent import ReasoningAgent
from stratum.ontology.schema import Organization, Employee, Project, ProjectStatus
from stratum.evaluation.harness import EvaluationHarness
from datetime import datetime, timezone

logging.basicConfig(level=logging.ERROR)

def run_stress_test():
    db_path = "stress_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    ws = WorldState()
    el = EventLog(db_path=db_path)
    sm = StateManager(ws, el)

    # Setup initial state
    sm.create_entity(Organization(id="org_1", name="StressCorp", balance=1000000.0))
    sm.create_entity(Employee(id="emp_1", name="Alice", role="Lead", skills=[], morale=1.0, energy_level=1.0, salary=10000))
    sm.create_entity(Project(id="proj_1", name="LargeProject", status=ProjectStatus.ACTIVE, budget=500000, progress=0.0, deadline=datetime.now(timezone.utc), complexity=0.7))

    agent = ReasoningAgent(sm)

    print("Running 500+ event stress test...")
    for i in range(500):
        if i % 100 == 0:
            print(f"Progress: {i}/500")

        event = "Progress update" if i % 2 == 0 else "Random morale fluctuation"
        agent.process_event(f"Step {i}: {event}", ["org_1", "emp_1", "proj_1"])

    eval_harness = EvaluationHarness(el)
    eval_harness.report()

if __name__ == "__main__":
    run_stress_test()
