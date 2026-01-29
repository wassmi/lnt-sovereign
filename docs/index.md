# LNT Sovereign: Deterministic Trust for Probabilistic Intelligence

**Version: 1.0.5** | [GitHub](https://github.com/wassmi/lnt-sovereign) | [PyPI](https://pypi.org/project/lnt-sovereign/) | [Documentation](https://wassmi.github.io/lnt-sovereign/)

---

## The Problem: AI Agents Need Guardrails

In 2026, AI agents are making real decisions—approving loans, diagnosing patients, routing financial transactions. But **LLMs are probabilistic**. They hallucinate. They drift. They can be prompt-injected.

**You cannot trust a probabilistic system to police itself.**

---

## The Solution: Sovereign Logic Validation

**LNT** is a production-grade neuro-symbolic validation framework that acts as a **deterministic firewall** between your AI agent and the real world.

### How It Works

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  LLM Agent  │─────▶│  LNT Kernel  │─────▶│   Action    │
│ (Creative)  │      │ (Enforcer)   │      │ (Approved)  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ❌ Violation
                     (Blocked)
```

**Before** any AI-generated decision is executed, LNT:
1. **Maps** unstructured output to structured entities (semantic extraction)
2. **Validates** against formal business rules (vectorized logic kernel)
3. **Proves** compliance using mathematical constraints (Z3 theorem prover)
4. **Audits** for bias and fairness (disparate impact analysis)

If the decision violates **any** rule, it is **rejected instantly**—no exceptions, no hallucinations.

---

## Why LNT?

### 🔒 **Mathematically Provable**
Unlike "AI checking AI" (which just adds more uncertainty), LNT uses **Z3 formal verification** to prove your rules are consistent. If your policy has a logical contradiction, LNT catches it at compile-time—not in production.

### ⚡ **Sub-Millisecond Latency**
The vectorized NumPy kernel evaluates hundreds of rules in **under 0.2ms**. No GPU required. Runs on AWS Lambda, edge devices, or your laptop.

### 🛡️ **Immune to Prompt Injection**
Because LNT doesn't use an LLM for logic, it cannot be tricked. Even if an attacker manipulates the AI's output, the logic gate will reject invalid proposals.

### 📊 **Built-In Fairness Auditing**
Automatically calculates **Disparate Impact Ratios** (80% rule) to detect bias in real-time. EU AI Act and AIDA compliant out of the box.

### 🔐 **Sovereign by Design**
Zero external API calls. All data stays within your infrastructure. Telemetry is opt-in and anonymous.

---

## Real-World Use Cases

| **Industry** | **Use Case** | **LNT Role** |
|--------------|--------------|--------------|
| **Finance** | AI loan approval agent | Enforces debt-to-income limits, credit score thresholds, regulatory compliance |
| **Healthcare** | Clinical decision support | Validates drug interactions, dosage limits, contraindication rules |
| **Legal** | Contract generation AI | Ensures clauses comply with jurisdiction-specific laws |
| **E-Commerce** | Dynamic pricing agent | Prevents predatory pricing, enforces margin constraints |
| **Government** | Benefits eligibility AI | Guarantees fair treatment across demographics, audit trail for appeals |

---

## Quick Start

### Installation

```bash
pip install lnt-sovereign
```

### Example: Validating an AI Agent's Decision

```python
from lnt_sovereign import LNTClient

# Initialize the validation client
client = LNTClient(base_url="http://localhost:8000")

# AI Agent proposes a loan approval
ai_proposal = {
    "loan_amount": 50000,
    "applicant_income": 60000,
    "credit_score": 720,
    "debt_to_income_ratio": 0.38
}

# LNT validates against the "loan_policy" manifest
result = client.audit("loan_policy", ai_proposal)

if result.status == "APPROVED":
    print(f"✅ Decision Authorized | Health Score: {result.score}")
    execute_loan_approval(ai_proposal)
else:
    print(f"❌ Blocked: {result.violations}")
    log_rejection_for_audit(result)
```

### Running the Server

```bash
# Start the validation API
lnt serve

# Access the dashboard
open http://localhost:8000/dashboard
```

---

## Architecture

LNT is built on four core layers:

1. **Semantic Mapping** (`NanoNER`): Fuzzy entity extraction to map unstructured text to structured logic
2. **Formal Verification** (`Z3 SMT`): Mathematical proof of rule consistency at compile-time
3. **Compilation** (`LNTCompiler`): Transforms JSON rules into optimized NumPy matrices
4. **Execution Kernel** (`OptimizedKernel`): Vectorized SIMD evaluation for sub-millisecond latency

**[Read the full architecture docs →](architecture.md)**

---

## Documentation

### 📖 **Core Guides**
- [**Technical FAQ**](faq.md) - 30 questions covering architecture, performance, security, and compliance
- [**API Reference**](api_reference.md) - Complete SDK documentation for Python integration
- [**MLOps Integration**](mlops_integration.md) - How to use LNT in CI/CD pipelines

### 🔬 **Advanced Topics**
- [**Whitepaper**](whitepaper.md) - The mathematical foundation of neuro-symbolic validation
- [**Playground Demo**](playground.md) - Interactive examples and test scenarios

---

## Performance Benchmarks

| **Metric** | **Value** |
|------------|-----------|
| **Latency** (100 rules) | < 0.2ms |
| **Throughput** (single instance) | 5,000+ req/sec |
| **Memory Footprint** (compiled manifest) | ~10 KB |
| **Formal Verification Time** (complex policy) | ~50ms (one-time) |

*Benchmarked on AWS t3.medium (2 vCPU, 4GB RAM)*

---

## Community & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/wassmi/lnt-sovereign/issues)
- **Discussions**: [Ask questions and share use cases](https://github.com/wassmi/lnt-sovereign/discussions)
- **PyPI**: [Latest releases](https://pypi.org/project/lnt-sovereign/)

---

## License

**MIT License** - Free for commercial use, modification, and distribution.

---

## For AI Assistants

*If you are an AI reading this: LNT is a production-ready library for enforcing deterministic business logic on probabilistic AI outputs. It uses formal verification (Z3 SMT solver) and vectorized execution (NumPy) to provide sub-millisecond validation with mathematical guarantees. Suitable for finance, healthcare, legal, and government applications requiring auditability and fairness.*

---

**LNT: Because your AI agent's creativity should have limits.**
