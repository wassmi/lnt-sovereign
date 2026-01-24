# API Reference
**Version: 1.0.3**

This document provides a comprehensive reference for the LNT SDK and core data structures.

## 1. LNTClient Reference
The `LNTClient` is the primary interface for auditing proposals against logic manifests.

### `LNTClient(api_key: Optional[str] = None, ...)`
*   **api_key**: (str) Required for remote evaluation via Sovereign Cloud. If `None`, the client defaults to local "Toolbox" mode.
*   **base_url**: (str) URL of the LNT endpoint (default: `http://localhost:8000`).
*   **timeout**: (float) Request timeout in seconds.
*   **max_retries**: (int) Number of connection retries before failing.

### `client.audit(manifest_id, proposal)`
Performs a deterministic audit of a structured proposal.
*   **manifest_id**: (str) The identifier for the logic manifest (e.g., `"visa_application"`).
*   **proposal**: (Dict[str, Any]) A dictionary of signals/entities to validate.
*   **Returns**: An `LNTResult` object containing:
    *   `status`: `"PASS"` or `"FAIL"`.
    *   `score`: (float) Weighted safety score from `0.0` to `100.0`.
    *   `violations`: (List[Violation]) List of triggered constraints.
    *   `domain`: (str) The ID of the manifest used.
    *   `proof`: (str) A SHA-256 signature of the decision.

### `client.evaluate(user_text, ...)`
*Async method*. Performs neural parsing followed by a logic audit.
*   **user_text**: (str) Raw natural language input.
*   **shadow_mode**: (bool) If `True`, the audit is logged but the result is always "PASS".

## 2. Data Structures
### `ManifestConstraint`
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Unique identifier for the rule. |
| `entity` | `str` | The signal name (e.g., `heart_rate`). |
| `operator` | `ConstraintOperator` | `GT`, `LT`, `EQ`, `RANGE`, `REQUIRED`. |
| `value` | `Any` | The threshold or allowed set. |
| `severity` | `str` | `TOXIC`, `IMPOSSIBLE`, or `WARNING`. |
| `weight` | `float` | Rule importance (0.0 - 1.0). |

## 3. Error Registry
| Error Code | Class | Rationale |
| :--- | :--- | :--- |
| `LNT_100` | `ManifestNotFoundError` | The requested `manifest_id` does not exist in local or remote registry. |
| `LNT_200` | `TypeMismatchError` | Proposal signal type is incompatible with operator (e.g., `GT` on a string). |
| `LNT_300` | `EvaluationError` | Unexpected runtime error during symbolic evaluation. |
| `LNT_400` | `LNT_SMT_UNSAT` | The manifest contains logically impossible or contradictory rules. |

## 4. Integration Guidelines
### HTTP Headers (Remote Mode)
When using the REST API directly:
*   `X-LNT-API-KEY`: Your authentication token.
*   `User-Agent`: `LNT-Python-SDK/1.0.3`.
