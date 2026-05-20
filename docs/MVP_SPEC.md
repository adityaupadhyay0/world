# STRATUM MVP Domain Specification: Simulated Organization Engine

## 1. Overview
The **Simulated Organization Engine** is a narrow-domain world model designed to simulate the inner workings of a small company. It maintains a causally consistent state of employees, projects, and organizational health. The goal is to provide a substrate where an LLM can reason about organizational changes, project risks, and team dynamics without hallucinating the underlying facts.

## 2. Ontology (The Skeleton)

### Entities
- **Organization**: The top-level entity representing the company.
    - `name`: string
    - `balance`: float (USD)
- **Employee**: A person working in the organization.
    - `name`: string
    - `role`: string (e.g., "Engineer", "Manager", "Designer")
    - `skills`: List[string]
    - `morale`: float (0.0 to 1.0)
    - `energy_level`: float (0.0 to 1.0)
    - `salary`: float (monthly USD)
- **Project**: A work initiative.
    - `name`: string
    - `status`: Enum (PLANNING, ACTIVE, COMPLETED, FAILED)
    - `budget`: float
    - `progress`: float (0.0 to 1.0)
    - `deadline`: string (ISO date)
    - `complexity`: float (0.0 to 1.0)

### Relations
- `WORKS_ON`: Connects `Employee` to `Project`.
    - Properties: `allocation_percentage` (0.0 to 1.0)
- `REPORTS_TO`: Connects `Employee` to `Employee` (Manager).
- `BELONGS_TO`: Connects `Employee` to `Organization`.
- `OWNED_BY`: Connects `Project` to `Organization`.

## 3. Causal Constraints (The Rules)
1. **Financial Consistency**: An `Organization`'s `balance` decreases by the sum of `Employee` salaries every month.
2. **Work-Progress Link**: `Project` `progress` increases only if an `Employee` with `WORKS_ON` relation exists and has `energy_level > 0`.
3. **Burnout**: If `energy_level` stays at 0 for more than 3 ticks, `morale` drops significantly.
4. **Resignation**: If `morale` drops below 0.1, there is a high probability of an `EmployeeQuit` event.
5. **Project Failure**: If `deadline` is passed and `progress < 1.0`, project status shifts to `FAILED`.

## 4. State Layer (The Memory)
- **Persistence**: SQLite for the `EventLog` and current state snapshot.
- **Relations**: NetworkX for the graph-based representation of the organization's structure.

## 5. Definition of a "Good Simulation"
- **Temporal Consistency**: If a query is made about an employee's morale at T=10 and T=11 (with no intervening events), the answer should remain identical.
- **Causal Traceability**: Every change in `Project` progress must be attributable to a `WorkPerformed` event in the `EventLog`.
- **Zero Hallucination**: The LLM must not be able to "invent" a new employee or "forget" a project's deadline if it is present in the structured state.
