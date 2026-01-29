import pytest

from lnt_sovereign.core.formal import FormalVerifier


@pytest.fixture
def verifier():
    return FormalVerifier()

def test_dead_code_detection(verifier):
    """Test that mathematically impossible rules are flagged as dead code."""
    manifest = {
        "domain_id": "DEAD_CODE_TEST",
        "constraints": [
            {
                "id": "ADULT",
                "entity": "age",
                "operator": "GT",
                "value": 18
            },
            {
                "id": "CHILD_ONLY",
                "entity": "age",
                "operator": "LT",
                "value": 10,
                "conditional_on": ["ADULT"]
            },
            {
                "id": "VALID_RULE",
                "entity": "age",
                "operator": "GT",
                "value": 25,
                "conditional_on": ["ADULT"]
            }
        ]
    }
    
    dead_rules = verifier.detect_dead_code(manifest)
    assert "CHILD_ONLY" in dead_rules
    assert "ADULT" not in dead_rules
    assert "VALID_RULE" not in dead_rules

def test_transitive_contradiction(verifier):
    """Test that contradictions across multiple rules are caught."""
    manifest = {
        "domain_id": "TRANSITIVE_DEAD",
        "constraints": [
            {"id": "A", "entity": "x", "operator": "GT", "value": 10},
            {"id": "B", "entity": "x", "operator": "GT", "value": 20, "conditional_on": ["A"]},
            {"id": "C", "entity": "x", "operator": "LT", "value": 15, "conditional_on": ["B"]}
        ]
    }
    # C requires B (x > 20) but says x < 15. Impossible.
    dead_rules = verifier.detect_dead_code(manifest)
    assert "C" in dead_rules
