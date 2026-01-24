# Integration & Performance Tuning
**Guidelines for Industrial Deployment**

## 1. Integration Patterns
LNT is designed as a sidecar validation layer.

### Pattern A: Synchronous Gatekeeper
Block execution until LNT returns `CERTIFIED`.
```python
result = client.audit("fin_aml", tx_proposal)
if result.status == "PASS":
    execute_transaction(tx_proposal)
```

### Pattern B: Async Shadow Audit
Log violations without blocking the user path (High-throughput observation).
```python
# Launch audit in background task
background_tasks.add_task(client.evaluate, user_text, shadow_mode=True)
```

## 2. Performance Tuning
### BELM Pre-compilation
The first evaluation of a manifest incurs a JIT-compiler overhead (approx. 200ms). In production, trigger a "warm-up" audit during system initialization:
```python
# Warm up the kernel
client.audit("healthcare_triage", dummy_proposal)
```

### Signal Batching
For high-concurrency systems, utilize the `SynthesisManifold` directly to avoid HTTP overhead if running as an internal library.

## 3. Persistent State (SG-2)
Temporal logic (`trailing_average`) requires the `SovereignStateBuffer`. In distributed environments, ensure your load balancer uses **Sticky Sessions** if the buffer is held in local memory, or implement a Redis-backed state adapter (available in Sovereign Cloud).
