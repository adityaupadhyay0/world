import json
import logging
import os
from typing import List, Dict, Any
from stratum.state.world_state import WorldState
from stratum.state.event_log import EventLog
from stratum.state.manager import StateManager
from stratum.reasoning.agent import ReasoningAgent
from stratum.ontology.schema import Organization, Employee, Project, ProjectStatus
from datetime import datetime, timezone, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrationTest")

class MockLLMClient:
    def __init__(self):
        self.call_count = 0

    def generate(self, prompt: str) -> str:
        self.call_count += 1
        # Extract the event and state from the prompt to make a "reasoned" response
        # This is a bit more sophisticated than the Agent's internal mock
        if "EVENT:" in prompt:
            event_part = prompt.split("EVENT:")[1].split("OUTPUT:")[0].strip()
            state_part = prompt.split("STATE:")[1].split("EVENT:")[0].strip()
            state = json.loads(state_part)

            if "hire" in event_part.lower() and "charlie" in event_part.lower():
                return json.dumps({
                    "entities": [{
                        "id": "emp_3",
                        "type": "Employee",
                        "name": "Charlie",
                        "role": "QA Engineer",
                        "skills": ["Testing"],
                        "morale": 0.8,
                        "energy_level": 1.0,
                        "salary": 6000.0
                    }]
                })

            if "work" in event_part.lower() or "progress" in event_part.lower():
                projects = [e for e in state['entities'] if e['type'] == 'Project']
                if projects:
                    p = projects[0]
                    p['progress'] = min(1.0, p['progress'] + 0.05)
                    return json.dumps({"entities": [p]})

            if "morale" in event_part.lower() and "drop" in event_part.lower():
                employees = [e for e in state['entities'] if e['type'] == 'Employee']
                if employees:
                    e = employees[0]
                    e['morale'] = max(0.0, e['morale'] - 0.2)
                    return json.dumps({"entities": [e]})

        return json.dumps({"entities": []})

def run_integration_test():
    db_path = "integration_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    ws = WorldState()
    el = EventLog(db_path=db_path)
    sm = StateManager(ws, el)

    # Initialize World
    org = Organization(id="org_1", name="IntegrationCorp", balance=100000.0)
    emp = Employee(id="emp_1", name="Alice", role="Dev", skills=[], morale=0.8, energy_level=1.0, salary=5000)
    proj = Project(id="proj_1", name="ProjectX", status=ProjectStatus.ACTIVE, budget=10000, progress=0.0, deadline=datetime.now(timezone.utc), complexity=0.5)

    sm.create_entity(org)
    sm.create_entity(emp)
    sm.create_entity(proj)

    client = MockLLMClient()
    agent = ReasoningAgent(sm, llm_client=client)

    entity_ids = ["org_1", "emp_1", "proj_1"]

    logger.info("Starting 50 sequential events simulation...")

    for i in range(50):
        event_type = i % 3
        if event_type == 0:
            event_desc = f"Work performed on ProjectX, step {i}"
        elif event_type == 1:
            event_desc = f"Morale drop due to long hours, step {i}"
        else:
            event_desc = f"New hire Charlie joins the team, step {i}"

        try:
            agent.process_event(event_desc, entity_ids + (["emp_3"] if i >= 2 else []))
        except Exception as e:
            logger.error(f"Failed at step {i}: {e}")
            break

    # Final Check
    final_snapshot = sm.get_state_snapshot(entity_ids + ["emp_3"])
    logger.info("Simulation Complete.")
    logger.info(f"Final Project Progress: {next(e['progress'] for e in final_snapshot['entities'] if e['id'] == 'proj_1')}")
    logger.info(f"Final Alice Morale: {next(e['morale'] for e in final_snapshot['entities'] if e['id'] == 'emp_1')}")

    # Verify events
    events = el.get_events(limit=200)
    logger.info(f"Total events in log: {len(events)}")
    assert len(events) >= 53 # 3 initial + 50 simulation steps

if __name__ == "__main__":
    run_integration_test()
