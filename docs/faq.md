# LNT: Technical FAQ (Research Prototype)

This document provides technical clarification on the design and research goals of the LNT validation framework.

---

## Project Status

### 1. Is LNT production-ready?
**No.** LNT is an early-stage research prototype. It has not been security audited, has no third-party validation, and has not been tested in diverse production environments. It is currently intended for local development and technical experimentation.

### 2. Is LNT audited?
No. There are currently no official security or technical audits for this project. Developers should exercise caution and conduct their own reviews before use.

---

## Architecture & Logic

### 3. What is the "Neuro-Symbolic" goal?
The goal is to investigate how probabilistic model outputs (neural) can be validated against deterministic logic (symbolic). LNT acts as a technical bridge for this experimentation.

### 4. Why use formal logic instead of standard conditionals?
LNT explores whether using a unified logic engine and SMT solvers (like Z3) can help developers detect contradictions and unreachable states in their business rules more systematically than using scattered `if/else` logic.

### 5. Does LNT require a GPU?
No. The execution kernel is implemented using NumPy-vectorized operations designed for CPU execution.

---

## Performance & Scaling (Goals)

### 6. What are the performance characteristics?
Preliminary testing on simple rule sets suggests low evaluation latency. However, high-throughput scaling and performance in high-concurrency environments are active areas of research.

### 7. How many rules can the prototype handle?
Initial tests show that the vectorized kernel can evaluate hundreds of rules with minimal overhead, but the practical limits of this approach in complex production scenarios are not yet known.

---

## Formal Verification (Z3 Integration)

### 8. How is Z3 used?
Z3 is used to help developers verify if their rule manifests are internally consistent. This is a pre-deployment step to catch logical errors before they affect runtime data.

### 9. Does Z3 run on every request?
No. In the current design, formal verification happens during **Manifest Ingestion**. Request-time evaluation is handled by the vectorized kernel.

---

## Integration

### 10. What is "Critical" vs "Warning" severity?
- **Critical**: Constraints that, if violated, trigger an immediate rejection by the logic gate.
- **Warning**: Constraints that contribute to an aggregate "Logic Health Score" but do not by themselves trigger rejection.
