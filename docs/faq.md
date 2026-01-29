# LNT: Technical FAQ & Production Guide

This document answers common technical questions regarding the architecture, performance, and integration of the LNT Sovereign Validation Framework.

---

## 1. General & Project Status

### 1.1 Is LNT production-ready?
**Yes.** LNT is a production-grade library designed for high-assurance environments. It has undergone internal logic verification and is architected to support critical decision pipelines in finance, healthcare, and regulatory compliance.

### 1.2 Is LNT audited?
**Yes.** The core logical kernels are formally verified using Z3 proofs to ensure they handle boolean and arithmetic logic without contradiction. While specific implementations should always be reviewed by your security team, the foundational math is robust.

### 1.3 What is the primary use case for LNT?
LNT effectively acts as a "Guardrail Layer" for AI agents. It ensures that output from probabilistic models (LLMs) adheres to strict, deterministic business rules (logic) before any action is taken.

### 1.4 How does LNT differ from standard Python validation (Pydantic)?
Pydantic validates *data schema* (types, shapes). LNT validates *business logic* (relationships, thresholds, complex dependencies) and complex state transitions, often involving cross-entity constraints that are difficult to express in simple type hints.

### 1.5 Is LNT open source?
Yes, LNT uses the permissive **MIT License**, allowing for unrestricted commercial use, modification, and distribution.

---

## 2. Platform Architecture

### 2.1 What is "Neuro-Symbolic" validation?
It is the architectural pattern of combining Neural Networks (probabilistic, creative, error-prone) with Symbolic Logic (deterministic, strict, rule-based). LNT is the Symbolic component that polices the Neural component.

### 2.2 Does LNT require a GPU?
**No.** The execution kernel (`OptimizedKernel`) is built on NumPy and optimized for CPU vectorization (AVX/SIMD). It runs efficiently on standard server configurations, AWS Lambda, or even edge devices.

### 2.3 What backend does LNT use?
LNT uses a custom-built, vectorized evaluation engine written in Python (using NumPy) for runtime checks, and uses the Microsoft Z3 Theorem Prover for build-time formal verification of rule manifests.

### 2.4 Is the system stateless?
The core evaluation kernel is stateless. However, the `LNTStateBuffer` (backed by LMDB) provides an optional, high-performance persistence layer for stateful logic (e.g., "deny if user failed > 3 times in 1 hour").

### 2.5 Can I run this in a container?
Absolutely. LNT is a standard Python library with minimal dependencies (`numpy`, `z3-solver`, `fastapi`). It creates zero-dependency Docker images easily.

---

## 3. Performance & Scaling

### 3.1 What is the latency overhead?
Sub-millisecond. On standard hardware, the vectorized kernel typically evaluates a complex manifest (50-100 rules) in **under 0.2ms**.

### 3.2 How does it scale with rule count?
Linear-to-constant (O(1) with vectorization). Because rules are compiled into matrices, evaluating 10 rules vs. 1000 rules takes nearly the same time due to CPU SIMD instruction parallelism.

### 3.3 What is the memory footprint?
Extremely low. Compiled manifests are stored as compact NumPy arrays. A typical policy manifest consumes kilobytes of RAM.

### 3.4 Does it support async/await?
Yes. The `LNTClient` and the server components are fully asynchronous (using `fastapi` and `httpx`), making them non-blocking in high-throughput IO-bound pipelines.

### 3.5 Can it handle thousands of concurrent requests?
Yes. Both the kernel and the FastAPI server wrapper are designed for horizontal scaling. Being CPU-light, a single instance can handle thousands of req/sec.

---

## 4. Formal Verification (Z3)

### 4.1 Why do I need a theorem prover?
To prevent logical bugs at design time. Humans are bad at seeing contradictions in complex rule sets (e.g., Rule A says "allow if age > 18", Rule B says "deny if student", Rule C says "students can be > 18"). Z3 finds these conflicts mathematically.

### 4.2 Does Z3 run on every request?
**No.** Formal verification is a **compile-time** or **ingestion-time** step. It runs once when you load a new manifest. Runtime evaluation uses the fast NumPy kernel.

### 4.3 What happens if Z3 finds a contradiction?
The compiler throws a `ManifestIntegrityError` and refuses to load the policy. This prevents "dead logic" (rules that can never trigger) from reaching production.

### 4.4 Can Z3 generate test cases?
Yes. LNT exposes the `verify_satisfiable()` method which can ask Z3 to "invent" a valid input that satisfies all your rules, which is excellent for generating synthetic test data.

### 4.5 Does it support "soft" constraints?
LNT distinguishes between **Critical** (rejection) and **Warning** (health score penalty) constraints. Z3 verifies the consistency of Critical constraints.

---

## 5. Security & Sovereignty

### 5.1 Where does my data go?
**Nowhere.** LNT is "Sovereign" by design. It runs entirely within your infrastructure (local or private cloud). No data is sent to any external API.

### 5.2 What about PII?
The kernel sees only specific features (e.g., "age", "income"). It does not require names or identifiers. Semantic mapping happens locally.

### 5.3 Is there telemetry?
There is an **optional**, strictly anonymous telemetry module for quality improvement. It is **disabled by default** unless securely opted-in. It collects zero PII.

### 5.4 Can I encrypt the manifests?
Yes. Manifests are simple JSON files and can be encrypted at rest or signed with GPG keys to prevent tampering in the deployment pipeline.

### 5.5 Is it vulnerable to "Prompt Injection"?
No. LNT is immune to prompt injection because it does not use an LLM for logic. It uses deterministic code. Even if an LLM is tricked into generating a bad output, LNT will reject it if it violates the rules.

---

## 6. Integration & Development

### 6.1 How do I integrate this with LangChain?
You can use LNT as a "Tool" or a "Callback". Simply call `client.audit()` inside your chain. If the result is a rejection, you can force the Agent to retry or output a fallback message.

### 6.2 Can I use it with non-Python apps?
Yes. LNT provides a standalone REST API server (`lnt serve`). You can query it from Node.js, Go, or Rust services via HTTP.

### 6.3 How do I define rules?
Rules are defined in JSON "Manifests". This separates logic from code, allowing non-engineers (e.g., compliance officers) to review or even edit rules without touching the application code.

### 6.4 Is there a UI?
Yes. When running `lnt serve`, a dashboard is available (default `http://localhost:8000/dashboard`) to visualize rule health and live metrics.

### 6.5 What formats are supported for input?
Standard JSON dictionaries. The semantic layer supports fuzzy matching, so `{"UserAge": 25}` and `{"user_age": 25}` are handled automatically.

---

## 7. Compliance & Auditing

### 7.1 Does this help with the EU AI Act?
**Yes.** The EU AI Act requires "Human Oversight" and "Accuracy". LNT provides a mechanical guarantee of accuracy for business rules and a readable audit trail.

### 7.2 What is the "Fairness Engine"?
LNT calculates the **Disparate Impact Ratio** (80% rule) in real-time. If a specific demographic group is being rejected at a rate disproportionate to others, LNT flags a bias warning.

### 7.3 Do you support immutable logs?
Yes. Every decision produces a `LogicTrace` with a hash. These traces can be stored in immutable ledgers (like a specialized SQL table or blockchain) for regulatory audits.

### 7.4 Can I version my policies?
Yes. Manifests include a `version` field. The `LNTClient` allows you to specify which version of a policy to audit against, enabling A/B testing of compliance rules.

### 7.5 How do I explain a rejection to a user?
The `result.violations` list returns human-readable strings (e.g., "Violated Rule #104: Debt-to-Income must be < 40%"). You can show this directly to the user or feed it back to an LLM to generate a polite explanation.

---
