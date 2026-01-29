import pytest

from lnt_sovereign.core.compiler import LNTCompiler
from lnt_sovereign.core.kernel import DomainManifest
from lnt_sovereign.core.optimized_kernel import OptimizedKernel


@pytest.fixture
def compiler():
    return LNTCompiler(verify=False) # Disable Z3 for faster core tests

@pytest.fixture
def simple_manifest_obj():
    manifest_data = {
        "domain_id": "TEST_V1",
        "domain_name": "Test Domain",
        "version": "1.0.0",
        "entities": ["age", "income"],
        "constraints": [
            {
                "id": "GT_18",
                "entity": "age",
                "operator": "GT",
                "value": 18,
                "description": "Must be adult",
                "severity": "TOXIC",
                "weight": 5.0,
                "evidence_source": "Law 1"
            },
            {
                "id": "MIN_INCOME",
                "entity": "income",
                "operator": "GT", # Changed from GTE to GT to match current Enum
                "value": 30000,
                "description": "Minimum income required",
                "severity": "WARNING",
                "weight": 1.0,
                "evidence_source": "Policy A"
            }
        ]
    }
    return DomainManifest(**manifest_data)

def test_vectorized_passes(compiler, simple_manifest_obj):
    """Test that valid proposals pass correctly via vectorization."""
    compiled = compiler.compile(simple_manifest_obj)
    kernel = OptimizedKernel(compiled)
    
    proposal = {"age": 25, "income": 50000}
    result = kernel.trace_evaluate(proposal)
    
    assert result["status"] == "CERTIFIED"
    assert result["score"] == 100.0
    assert not result["violations"]
    assert len(result["passes"]) == 2

def test_vectorized_violations(compiler, simple_manifest_obj):
    """Test that violations are caught and weights applied correctly."""
    compiled = compiler.compile(simple_manifest_obj)
    kernel = OptimizedKernel(compiled)
    
    # Fail only the warning rule (MIN_INCOME)
    proposal = {"age": 25, "income": 20000}
    result = kernel.trace_evaluate(proposal)
    
    assert result["status"] == "REJECTED"
    assert len(result["violations"]) == 1
    assert result["violations"][0]["id"] == "MIN_INCOME"
    
    # Score calculation: 100 * (1 - (deducted / total))
    # total_weight = 5 (TOXIC) + 1 (WARNING) = 6
    # deducted = 1 (WARNING)
    # score = 100 * (1 - 1/6) = 100 * 5/6 = 83.33
    assert result["score"] == 83.33

def test_toxic_rejection(compiler, simple_manifest_obj):
    """Test that a toxic violation significantly impacts the score."""
    compiled = compiler.compile(simple_manifest_obj)
    kernel = OptimizedKernel(compiled)
    
    # Fail the TOXIC rule (age)
    proposal = {"age": 16, "income": 50000}
    result = kernel.trace_evaluate(proposal)
    
    assert result["status"] == "REJECTED"
    assert any(v["severity"] == "TOXIC" for v in result["violations"])
    
    # total_weight = 6
    # deducted = 5
    # score = 100 * (1 - 5/6) = 100 * 1/6 = 16.67
    assert result["score"] == 16.67

def test_matrix_reset(compiler, simple_manifest_obj):
    """Ensure that the state vector is reset between evaluations."""
    compiled = compiler.compile(simple_manifest_obj)
    kernel = OptimizedKernel(compiled)
    
    # First evaluation: Valid
    kernel.trace_evaluate({"age": 25, "income": 50000})
    
    # Second evaluation: Invalid (leaked state would pass if not reset)
    result = kernel.trace_evaluate({"age": 10, "income": 10000})
    assert result["status"] == "REJECTED"
    assert len(result["violations"]) == 2
