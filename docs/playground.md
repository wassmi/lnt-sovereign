# LNT: Interactive Developer Playground

The **LNT Playground** is a CLI utility that allows developers to "try out" their logic manifests and proposals with visual, color-coded feedback.

---

## How to launch the playground

Once you have the repository cloned, you can start the interactive playground from your terminal:

```bash
python scripts/playground_demo.py
```

---

## What can you do in the playground?

### 1. Visual Satisfaction Reports
The playground uses the **Z3 SMT solver** to show you in real-time if your rules are satisfiable.
*   🟢 **Satisfiable**: Your rules are consistent. The playground will generate an "Example Valid Input" for you.
*   🔴 **Unsatisfiable**: You have a logic contradiction. The playground will help you identify which rules are conflicting.

### 2. Live Proposal Testing
Enter values for your defined entities (like `age`, `income`, `risk_score`) and watch how the **Vectorized Logic Kernel** evaluates them.

### 3. "Shadow Mode" Dry-Runs
Test your manifests in a safe environment before deploying them as a "Logic Gate" in your CI/CD pipeline.

---

## Example Interaction

```text
> Enter Age: 25
> Enter Income: 55000

--- EVALUATION RESULTS ---
STATUS: CERTIFIED ✅
SCORE: 100.0/100.0
PASSES: [GT_18, MIN_INCOME]
VIOLATIONS: []

VERDICT: Proposal is safe to proceed.
```

---

## Why use the playground?

*   **Zero-Risk Iteration**: Experiment with complex rules without touching production code.
*   **Intuitive Debugging**: See exactly why a specific input triggers a violation.
*   **Proof of Concept**: Quickly demonstrate LNT's value to your team with immediate visual results.
