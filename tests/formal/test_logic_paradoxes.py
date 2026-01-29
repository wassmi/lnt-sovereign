import pytest

from lnt_sovereign.core.formal import FormalVerifier


@pytest.fixture
def verifier():
    return FormalVerifier()

def test_simple_contradiction(verifier):
    """Test that mutually exclusive numeric constraints fail."""
    manifest = {
        "domain_id": "PARADOX_V1",
        "constraints": [
            {"id": "GT_10", "entity": "age", "operator": "GT", "value": 10},
            {"id": "LT_5", "entity": "age", "operator": "LT", "value": 5}
        ]
    }
    consistent, error = verifier.verify_consistency(manifest)
    assert not consistent
    assert "contradictory" in error.lower()

def test_satisfiable_boundaries(verifier):
    """Test that touching boundaries without overlap passes."""
    manifest = {
        "domain_id": "BOUNDARY_V1",
        "constraints": [
            {"id": "GTE_10", "entity": "score", "operator": "GTE", "value": 10},
            {"id": "LTE_10", "entity": "score", "operator": "LTE", "value": 10}
        ]
    }
    consistent, error = verifier.verify_consistency(manifest)
    assert consistent
    
    # Verify that the only valid input is exactly 10
    satisfiable, example = verifier.verify_satisfiable(manifest)
    assert satisfiable
    assert float(example["score"]) == 10.0

def test_complex_unsat_core(verifier):
    """Test multiple dependencies that create an impossible state."""
    # If A > 10 AND B < 5 AND A + B must be 100 but rules say they are small
    manifest = {
        "domain_id": "COMPLEX_PARADOX",
        "constraints": [
            {"id": "RULE_1", "entity": "a", "operator": "GT", "value": 90},
            {"id": "RULE_2", "entity": "b", "operator": "GT", "value": 20},
            {"id": "RULE_3", "entity": "total", "operator": "LT", "value": 100}
        ]
    }
    # Currently our FormalVerifier doesn't support complex cross-entity relationships 
    # like 'total = a + b' in the JSON itself, but we can test if it handles multiple
    # independent contradictions.
    
    manifest_clash = {
        "domain_id": "CLASH",
        "constraints": [
            {"id": "X_1", "entity": "x", "operator": "EQ", "value": 1},
            {"id": "X_2", "entity": "x", "operator": "EQ", "value": 2}
        ]
    }
    consistent, _ = verifier.verify_consistency(manifest_clash)
    assert not consistent

def test_boolean_paradox(verifier):
    """Test contradictory boolean constraints."""
    manifest = {
        "domain_id": "BOOL_PARADOX",
        "constraints": [
            {"id": "B_TRUE", "entity": "is_valid", "operator": "EQ", "value": True},
            {"id": "B_FALSE", "entity": "is_valid", "operator": "EQ", "value": False}
        ]
    }
    consistent, _ = verifier.verify_consistency(manifest)
    assert not consistent

def test_impossible_range(verifier):
    """Test a range where min > max."""
    manifest = {
        "domain_id": "RANGE_PARADOX",
        "constraints": [
            {"id": "BAD_RANGE", "entity": "temp", "operator": "RANGE", "value": [100, 50]}
        ]
    }
    consistent, _ = verifier.verify_consistency(manifest)
    assert not consistent
