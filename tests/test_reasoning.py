import pytest
from stratum.reasoning.verifier import CausalVerifier
from stratum.reasoning.detector import ContradictionDetector

def test_causal_verifier_type_drift():
    verifier = CausalVerifier()
    current = {"entities": [{"id": "e1", "type": "Employee"}]}
    proposed = {"entities": [{"id": "e1", "type": "Project"}]}
    violations = verifier.verify_update(current, proposed)
    assert any("type from Employee to Project" in v for v in violations)

def test_causal_verifier_bounds():
    verifier = CausalVerifier()
    current = {"entities": [{"id": "e1", "type": "Employee", "morale": 0.5}]}
    proposed = {"entities": [{"id": "e1", "type": "Employee", "morale": 1.5}]}
    violations = verifier.verify_update(current, proposed)
    assert any("morale 1.5 out of bounds" in v for v in violations)

def test_contradiction_detector_project_logic():
    detector = ContradictionDetector()
    state = {"entities": [{"id": "p1", "type": "Project", "status": "COMPLETED", "progress": 0.5}]}
    conflicts = detector.detect_contradictions(state)
    assert any("COMPLETED but progress is 0.5" in c for c in conflicts)
