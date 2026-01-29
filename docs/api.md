# API Reference

## `LNTClient` (The SDK)

The primary interface for users to interact with the LNT Engine.

### `evaluate(user_text, shadow_mode=False)`
Evaluates a proposal against the detecting domain.

---

## `SynthesisManifold`

The top-level orchestrator for local deployments.

### `process_application(user_text)`
The unified loop: Detect -> Parse -> Audit -> Log.

---

## `KernelEngine`

The heart of the symbolic logic.

### `trace_evaluate(proposal)`
Performs full DAG and Weighted evaluation. Returns a `score` and `violations`.
