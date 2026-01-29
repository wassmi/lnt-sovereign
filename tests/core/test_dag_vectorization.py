import pytest

from lnt_sovereign.core.compiler import LNTCompiler
from lnt_sovereign.core.kernel import DomainManifest
from lnt_sovereign.core.optimized_kernel import OptimizedKernel


@pytest.fixture
def compiler():
    return LNTCompiler(verify=False)

@pytest.fixture
def dag_manifest():
    manifest_data = {
        "domain_id": "DAG_TEST",
        "domain_name": "DAG Dependency Test",
        "version": "1.0.0",
        "entities": ["a", "b", "c"],
        "constraints": [
            {
                "id": "RULE_A",
                "entity": "a",
                "operator": "GT",
                "value": 10,
                "description": "Rule A",
                "severity": "TOXIC",
                "weight": 1.0
            },
            {
                "id": "RULE_B",
                "entity": "b",
                "operator": "GT",
                "value": 5,
                "description": "Rule B depends on A",
                "severity": "WARNING",
                "weight": 1.0,
                "conditional_on": ["RULE_A"]
            },
            {
                "id": "RULE_C",
                "entity": "c",
                "operator": "GT",
                "value": 0,
                "description": "Rule C generic",
                "severity": "WARNING",
                "weight": 1.0
            }
        ]
    }
    return DomainManifest(**manifest_data)

def test_dag_pruning(compiler, dag_manifest):
    """Test that if RULE_A fails, RULE_B is pruned (not evaluated)."""
    compiled = compiler.compile(dag_manifest)
    kernel = OptimizedKernel(compiled)
    
    # CASE 1: RULE_A fails
    proposal = {"a": 5, "b": 10, "c": 5}
    result = kernel.trace_evaluate(proposal)
    
    assert result["status"] == "REJECTED"
    assert "RULE_A" in [v["id"] for v in result["violations"]]
    assert "RULE_B" not in [v["id"] for v in result["violations"]]
    assert "RULE_B" in result["pruned"]
    assert "RULE_C" in result["passes"]
    
    # Score check: total_weight should exclude RULE_B
    # total_weight = weight(A) + weight(C) = 1 + 1 = 2
    # deducted = weight(A) = 1
    # score = 100 * (1 - 1/2) = 50.0
    assert result["score"] == 50.0

def test_dag_passing_chain(compiler, dag_manifest):
    """Test that if RULE_A passes, RULE_B is evaluated."""
    compiled = compiler.compile(dag_manifest)
    kernel = OptimizedKernel(compiled)
    
    # CASE 2: RULE_A passes, RULE_B fails
    proposal = {"a": 20, "b": 2, "c": 5}
    result = kernel.trace_evaluate(proposal)
    
    assert "RULE_A" in result["passes"]
    assert "RULE_B" in [v["id"] for v in result["violations"]]
    assert "RULE_B" not in result["pruned"]
    
    # total_weight = A + B + C = 3
    # deducted = weight(B) = 1
    # score = 100 * (1 - 1/3) = 66.67
    assert result["score"] == 66.67
