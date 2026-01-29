import os
from typing import Any, Dict, Optional

from fastapi import Body, FastAPI, Header, HTTPException

from lnt_sovereign.core.topology import TopologyOrchestrator

app = FastAPI(title="LNT Logic Evaluation Engine")
manifold = TopologyOrchestrator()

API_KEYS = {
    os.getenv("LNT_ADMIN_KEY", "lnt-admin-key-2026"): "ADMIN",
    os.getenv("LNT_VERIFIER_KEY", "lnt-verifier-key-2026"): "VERIFIER",
    os.getenv("LNT_AUDITOR_KEY", "lnt-auditor-key-2026"): "AUDITOR"
}
# Filter out None keys if any env var is missing and no default provided
API_KEYS = {k: v for k, v in API_KEYS.items() if k is not None}

@app.post("/process")
async def process(
    payload: Dict[str, Any] = Body(...),
    x_lnt_api_key: Optional[str] = Header(None)
) -> Dict[str, Any]:
    # 1. RBAC Clearance
    if not x_lnt_api_key or x_lnt_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    role = API_KEYS[x_lnt_api_key]
    if role == "AUDITOR":
        raise HTTPException(status_code=403, detail="Insufficient Clearance to process proposals.")

    # 2. Extract context
    user_text = payload.get("user_text", "")
    shadow_mode = payload.get("shadow_mode", False)
    
    # 3. Decision Cycle
    result = manifold.process_application(user_text)
    
    # 4. Shadow Mode Transformation
    if shadow_mode:
        original_status = result["status"]
        if original_status == "REJECTED_BY_LOGIC":
            result["status"] = "SHADOW_REJECTED"
        result["shadow_mode"] = True

    # 5. Reasoning Trace Mapping (Expected by SDK)
    # The SDK integration tests expect reasoning_trace.logic_anchors, neural_proposal etc.
    result["reasoning_trace"] = {
        "logic_anchors": result.get("violations", []) + result.get("passes", []),
        "neural_proposal": result.get("proposal", {}),
        "proof": result.get("proof", "")
    }
    
    return result

@app.get("/ops")
async def ops() -> Dict[str, Any]:
    """Operational health dashboard."""
    return manifold.monitor.get_ops_report()

@app.get("/analytics/summary")
async def analytics_summary() -> Dict[str, Any]:
    """LNT analytics rollup."""
    return manifold.analytics.generate_health_summary()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
