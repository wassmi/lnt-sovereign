import time

import numpy as np

from lnt_sovereign.core.compiler import LNTCompiler
from lnt_sovereign.core.kernel import DomainManifest
from lnt_sovereign.core.optimized_kernel import OptimizedKernel


def benchmark_belm():
    # Create a manifest with 100 rules
    entities = [f"sensor_{i}" for i in range(10)]
    constraints = []
    for i in range(100):
        constraints.append({
            "id": f"RULE_{i}",
            "entity": np.random.choice(entities),
            "operator": "GT",
            "value": np.random.random() * 100,
            "description": f"Rule {i}",
            "severity": "WARNING",
            "weight": 1.0
        })
        
    manifest = DomainManifest(
        domain_id="BENCHMARK",
        domain_name="Benchmark Domain",
        version="1.0.0",
        entities=entities,
        constraints=constraints
    )
    
    compiler = LNTCompiler(verify=False)
    compiled = compiler.compile(manifest)
    kernel = OptimizedKernel(compiled)
    
    proposal = {e: np.random.random() * 100 for e in entities}
    
    # Warmup
    for _ in range(100):
        kernel.evaluate(proposal)
        
    # Benchmark
    iterations = 10000
    start = time.perf_counter()
    for _ in range(iterations):
        kernel.evaluate(proposal)
    end = time.perf_counter()
    
    avg_sec = (end - start) / iterations
    avg_ns = avg_sec * 1e9
    
    print("--- BELM Benchmark Results ---")
    print(f"Rules: {len(constraints)}")
    print(f"Iterations: {iterations}")
    print(f"Average Latency: {avg_ns:.2f} ns")
    print(f"Throughput: {1/avg_sec:,.0f} audits/sec")

if __name__ == "__main__":
    benchmark_belm()
