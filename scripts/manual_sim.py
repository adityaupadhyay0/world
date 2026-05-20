from stratum.state.world_state import WorldState
from stratum.state.event_log import EventLog
from stratum.state.manager import StateManager
from stratum.ontology.schema import Organization, Employee, Project, Relation, ProjectStatus
from datetime import datetime, timezone, timedelta
import os

def manual_simulation():
    db_path = "simulation.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    ws = WorldState()
    el = EventLog(db_path=db_path)
    sm = StateManager(ws, el)

    print("--- Event 1: Organization Creation ---")
    org = Organization(id="org_1", name="FutureWorks", balance=500000.0)
    sm.create_entity(org, cause="Initial setup")

    print("--- Event 2: Hiring Lead Engineer ---")
    alice = Employee(
        id="emp_1",
        name="Alice",
        role="Lead Engineer",
        skills=["Python", "System Design"],
        morale=0.9,
        energy_level=1.0,
        salary=10000.0
    )
    sm.create_entity(alice, cause="Hiring")
    sm.add_relation(Relation(source_id="emp_1", target_id="org_1", relation_type="BELONGS_TO"))

    print("--- Event 3: Project Kickoff ---")
    project = Project(
        id="proj_1",
        name="NeuralLink-MVP",
        status=ProjectStatus.PLANNING,
        budget=100000.0,
        progress=0.0,
        deadline=(datetime.now(timezone.utc) + timedelta(days=90)),
        complexity=0.8
    )
    sm.create_entity(project, cause="New business goal")
    sm.add_relation(Relation(source_id="emp_1", target_id="proj_1", relation_type="WORKS_ON", properties={"allocation": 1.0}))

    print("--- Event 4: Work Progress ---")
    project.status = ProjectStatus.ACTIVE
    project.progress = 0.1
    sm.update_entity(project, cause="First sprint completed")

    print("--- Event 5: Hiring Designer ---")
    bob = Employee(
        id="emp_2",
        name="Bob",
        role="Designer",
        skills=["UI/UX"],
        morale=0.8,
        energy_level=1.0,
        salary=7000.0
    )
    sm.create_entity(bob, cause="Hiring")
    sm.add_relation(Relation(source_id="emp_2", target_id="org_1", relation_type="BELONGS_TO"))
    sm.add_relation(Relation(source_id="emp_2", target_id="proj_1", relation_type="WORKS_ON", properties={"allocation": 0.5}))

    print("--- Event 6: Monthly Expense ---")
    org.balance -= (alice.salary + bob.salary)
    sm.update_entity(org, cause="Payroll disbursement")

    print("--- Event 7: Unexpected Issue ---")
    project.complexity = 0.9
    alice.energy_level = 0.6
    sm.update_entity(project, cause="Technical debt discovered")
    sm.update_entity(alice, cause="Overwork")

    print("--- Event 8: Morale Boost ---")
    alice.morale = 0.95
    sm.update_entity(alice, cause="Successful demo")

    print("--- Event 9: More Progress ---")
    project.progress = 0.25
    sm.update_entity(project, cause="Second sprint completed")

    print("--- Event 10: State Snapshot Check ---")
    snapshot = sm.get_state_snapshot(["org_1", "emp_1", "proj_1"])
    print(f"Organization Balance: {org.balance}")
    print(f"Project Progress: {project.progress}")
    print(f"Alice Morale: {alice.morale}")

    events = el.get_events(limit=20)
    print(f"Total events logged: {len(events)}")

if __name__ == "__main__":
    manual_simulation()
