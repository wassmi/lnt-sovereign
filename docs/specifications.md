# Logic Verification Standards

LNT implements a tiered set of performance and security specifications to support high-reliability AI applications.

## Level 1: Constraint Enforcement
*   **Relationship Logic**: Prerequisites ensure context is satisfied before dependent rules are evaluated.
*   **Weighted Scoring**: Supports granular rule weights (0.0 to 1.0) for nuanced risk assessment.
*   **Vectorized Execution**: Matrix-accelerated evaluation for low-latency feedback in local experiments.

## Level 2: Temporal Analysis
*   **Stateful Windows**: Support for `trailing_average`, `event_frequency`, and `burst_detection`.
*   **Contextual Persistence**: The engine maintains historical state across configurable time horizons.
*   **Micro-Temporal Monitoring**: High-resolution delta checks for sensitive telemetry (e.g., medical vitals, cyber-security events).
