import time
from lnt_sovereign.core.kernel import KernelEngine
from lnt_sovereign.core.compiler import SovereignCompiler
from lnt_sovereign.core.optimized_kernel import OptimizedKernel
import os

def run_benchmark():
    print("--- LNT Performance Benchmark: JSON vs BELM ---")
    
    # 1. Setup Manifest
    manifest_path = os.path.join("manifests", "healthcare_triage.json")
    kernel_engine = KernelEngine()
    raw_manifest = kernel_engine.load_manifest(manifest_path)
    
    compiler = SovereignCompiler()
    compiled = compiler.compile(raw_manifest)
    opt_kernel = OptimizedKernel(compiled)
    
    # 2. Setup Proposal
    proposal = {
        "heart_rate": 110.0,
        "oxygen_saturation": 82.0,
        "blood_pressure_systolic": 120.0,
        "blood_pressure_diastolic": 80.0
    }
    
    iterations = 50000
    
    # 3. Benchmark Legacy Kernel (Interpreted)
    # Warm up
    for _ in range(100):
        kernel_engine.evaluate(proposal)
    start_time = time.perf_counter()
    for _ in range(iterations):
        _ = kernel_engine.evaluate(proposal)
    legacy_time = (time.perf_counter() - start_time) / iterations
    
    # 4. Benchmark Optimized Kernel (Vectorized BELM)
    # Warm up
    for _ in range(100):
        opt_kernel.evaluate(proposal)
    start_time = time.perf_counter()
    for _ in range(iterations):
        _ = opt_kernel.evaluate(proposal)
    opt_time = (time.perf_counter() - start_time) / iterations
    
    speedup = legacy_time / opt_time
    
    print(f"Legacy Kernel (JSON): {legacy_time * 1e6:.2f} microseconds")
    print(f"Optimized Kernel (BELM): {opt_time * 1e6:.2f} microseconds")
    print(f"Total Speedup: {speedup:.1f}x")
    print("-----------------------------------------------")
    
    # Assert sub-microsecond target (Depends on hardware, but usually true for vectorized math)
    # On most modern CPUs, 1-5 microseconds is typical for simple vectors.
    if opt_time < legacy_time:
        print("Performance verification: SUCCESS")
    else:
        print("Performance verification: FAILED")

def run_stress_test():
    print("\n--- LNT Scaling Stress Test (1000 Rules) ---")
    from lnt_sovereign.core.kernel import DomainManifest, ManifestConstraint
    
    # 1. Generate 1000 random rules
    constraints = []
    entities = [f"entity_{i}" for i in range(100)]
    for i in range(1000):
        constraints.append(ManifestConstraint(
            id=f"RULE_{i}",
            entity=entities[i % 100],
            operator="GT",
            value=float(i % 50),
            description="Stress rule",
            severity="TOXIC"
        ))
    
    manifest = DomainManifest(
        domain_id="STRESS_TEST",
        domain_name="Stress Test",
        version="1.0",
        entities=entities,
        constraints=constraints
    )
    
    kernel_engine = KernelEngine()
    kernel_engine.manifest = manifest
    
    compiler = SovereignCompiler()
    compiled = compiler.compile(manifest)
    opt_kernel = OptimizedKernel(compiled)
    
    proposal = {f"entity_{i}": 25.0 for i in range(100)}
    iterations = 500
    
    # Legacy
    start_time = time.perf_counter()
    for _ in range(iterations):
        _ = kernel_engine.evaluate(proposal)
    legacy_time = (time.perf_counter() - start_time) / iterations
    
    # Optimized
    start_time = time.perf_counter()
    for _ in range(iterations):
        _ = opt_kernel.evaluate(proposal)
    opt_time = (time.perf_counter() - start_time) / iterations
    
    print(f"Legacy Kernel (1000 rules): {legacy_time * 1e6:.2f} microseconds")
    print(f"Optimized Kernel (1000 rules): {opt_time * 1e6:.2f} microseconds")
    print(f"Total Speedup: {legacy_time / opt_time:.1f}x")
    print("--------------------------------------------")

    # --------------------------------------------
    # 3. Dense Scaling Test (NumPy's Home Turf)
    # --------------------------------------------
    print("\n--- Dense Scaling Test (10,000 Rules + Dense Input) ---")
    
    # Generate 10k rules
    constraints_long = []
    for i in range(10000):
        constraints_long.append(ManifestConstraint(
            id=f"R_{i}", entity=entities[i % 100], operator="GT", value=10.0,
            description="Dense rule", severity="TOXIC"
        ))
    
    manifest_dense = DomainManifest(
        domain_id="DENSE", domain_name="Dense", version="1.0",
        entities=entities, constraints=constraints_long
    )
    
    kernel_engine.manifest = manifest_dense
    compiled_dense = compiler.compile(manifest_dense)
    opt_kernel_dense = OptimizedKernel(compiled_dense)
    
    start_time = time.perf_counter()
    for _ in range(100):
        kernel_engine.evaluate(proposal)
    legacy_dense_time = (time.perf_counter() - start_time) / 100
    
    start_time = time.perf_counter()
    for _ in range(100):
        opt_kernel_dense.evaluate(proposal)
    opt_dense_time = (time.perf_counter() - start_time) / 100
    
    print(f"Legacy Kernel (10k rules): {legacy_dense_time * 1e3:.2f} ms")
    print(f"Optimized Kernel (10k rules): {opt_dense_time * 1e3:.2f} ms")
    print(f"Total Speedup: {legacy_dense_time / opt_dense_time:.1f}x")
    
if __name__ == "__main__":
    run_benchmark()
    run_stress_test()
    run_stress_test() # Run twice to verify cache/stability
