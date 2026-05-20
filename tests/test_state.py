import pytest
import os
from datetime import datetime, timezone
from stratum.ontology.schema import Employee, Project, Organization, Relation, ProjectStatus
from stratum.state.world_state import WorldState
from stratum.state.event_log import EventLog
from stratum.state.manager import StateManager

@pytest.fixture
def state_manager():
    db_path = "test_events.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    ws = WorldState()
    el = EventLog(db_path=db_path)
    manager = StateManager(ws, el)
    yield manager
    if os.path.exists(db_path):
        os.remove(db_path)

def test_entity_creation(state_manager):
    emp = Employee(
        id="emp_1",
        name="Alice",
        role="Engineer",
        skills=["Python", "AI"],
        morale=0.9,
        energy_level=0.8,
        salary=8000
    )
    state_manager.create_entity(emp)

    retrieved = state_manager.world_state.get_entity("emp_1")
    assert retrieved.name == "Alice"
    assert retrieved.type == "Employee"

def test_relation_addition(state_manager):
    org = Organization(id="org_1", name="TechCorp", balance=1000000)
    emp = Employee(id="emp_1", name="Alice", role="Engineer", skills=[], morale=0.8, energy_level=0.8, salary=8000)

    state_manager.create_entity(org)
    state_manager.create_entity(emp)

    rel = Relation(source_id="emp_1", target_id="org_1", relation_type="BELONGS_TO")
    state_manager.add_relation(rel)

    relations = state_manager.world_state.get_relations(source_id="emp_1")
    assert len(relations) == 1
    assert relations[0].target_id == "org_1"
    assert relations[0].relation_type == "BELONGS_TO"

def test_event_log_persistence(state_manager):
    emp = Employee(id="emp_1", name="Alice", role="Engineer", skills=[], morale=0.8, energy_level=0.8, salary=8000)
    state_manager.create_entity(emp, cause="Hiring")

    events = state_manager.event_log.get_events(source_id="emp_1")
    assert len(events) == 1
    assert events[0]["event_type"] == "ENTITY_CREATED"
    assert events[0]["cause"] == "Hiring"

def test_state_snapshot(state_manager):
    org = Organization(id="org_1", name="TechCorp", balance=1000000)
    state_manager.create_entity(org)

    snapshot = state_manager.get_state_snapshot(["org_1"])
    assert len(snapshot["entities"]) == 1
    assert snapshot["entities"][0]["name"] == "TechCorp"

def test_update_validation(state_manager):
    project = Project(
        id="proj_1",
        name="Apollo",
        status=ProjectStatus.PLANNING,
        budget=50000,
        progress=0.0,
        deadline=datetime.now(timezone.utc),
        complexity=0.5
    )
    state_manager.create_entity(project)

    update_data = {
        "entities": [
            {
                "id": "proj_1",
                "type": "Project",
                "name": "Apollo",
                "status": "ACTIVE",
                "budget": 50000,
                "progress": 0.1,
                "deadline": datetime.now(timezone.utc).isoformat(),
                "complexity": 0.5
            }
        ]
    }
    state_manager.validate_and_commit_update(update_data, cause="Kickoff")

    updated_proj = state_manager.world_state.get_entity("proj_1")
    assert updated_proj.status == ProjectStatus.ACTIVE
    assert updated_proj.progress == 0.1
