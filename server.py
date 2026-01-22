from fastapi import FastAPI, HTTPException, Header, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from datetime import datetime

from lnt_sovereign.core.agents import AgentOrchestrator
from lnt_sovereign.core.database import log_decision

from enum import StrEnum

class UserRole(StrEnum):
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"
    VERIFIER = "VERIFIER"

class User(BaseModel):
    api_key: str
    role: UserRole
    organization: str

# Sovereign Key Registry (In production, move to HashiCorp Vault or Postgres)
API_REGISTRY = {
    "lnt-admin-key-2026": User(api_key="lnt-admin-key-2026", role=UserRole.ADMIN, organization="GOV_CANADA_CRTC"),
    "lnt-auditor-key-2026": User(api_key="lnt-auditor-key-2026", role=UserRole.AUDITOR, organization="AIDA_COMPLIANCE"),
    "lnt-verifier-key-2026": User(api_key="lnt-verifier-key-2026", role=UserRole.VERIFIER, organization="VISA_PROCESSING_UNIT")
}

API_KEY_NAME = "X-LNT-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_current_user(api_key: str = Security(api_key_header)) -> User:
    if api_key in API_REGISTRY:
        return API_REGISTRY[api_key]
    raise HTTPException(status_code=403, detail="Sovereign Access Denied: Invalid Logic Key")

def require_role(role: UserRole):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != role and user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail=f"Insufficient Clearance: Required {role}")
        return user
    return role_checker

app = FastAPI(
    title="LNT Sovereign Engine",
    description="Sovereign Neuro-Symbolic Inference for Federal Compliance",
    base_url="/",
    version="1.0.0"
)

orchestrator = AgentOrchestrator()

class ApplicationRequest(BaseModel):
    user_text: str
    domain_override: Optional[str] = None
    shadow_mode: bool = False

class DecisionResponse(BaseModel):
    status: str
    domain: str
    explanation: str
    violations: List[Dict[str, Any]]
    reasoning_trace: Dict[str, Any]
    proof: str
    shadow_mode: bool
    prover_note: str
    verifier_audit: str

@app.get("/")
def read_root():
    return {"status": "SOVEREIGN_ENGINE_ONLINE", "version": "1.0.0", "compliance": "AIDA/C-27"}

@app.post("/process", response_model=DecisionResponse)
async def process_intent(
    request: ApplicationRequest, 
    user: User = Depends(require_role(UserRole.VERIFIER))
):
    """
    Primary endpoint for neuro-symbolic inference.
    Requires VERIFIER or ADMIN clearance.
    """
    try:
        # 1. Execute the Agent Workflow
        workflow = orchestrator.execute_workflow(request.user_text)
        proposal = workflow["proposal"]
        audit = workflow["audit"]
        result = audit["manifold_result"]
        
        # 2. Extract violations for transparency
        violations = result.get("violations", [])
        
        # 3. Handle Shadow Mode Logic
        status = result["status"]
        if request.shadow_mode and status == "REJECTED_BY_SOVEREIGN_LOGIC":
            status = "SHADOW_REJECTED" 
        
        # 4. AIDA-Compliant Persistence
        log_decision(
            domain=result.get("domain", "UNKNOWN"),
            user_input=request.user_text,
            proposal=proposal.dict() if hasattr(proposal, 'dict') else {"content": proposal.content},
            result=result,
            bias_score=result.get("bias_score", 1.0)
        )
        
        # 5. Build the Reasoning Trace for the SDK
        reasoning_trace = {
            "status": status,
            "domain": result.get("domain", "UNKNOWN"),
            "proof": result.get("proof", "UNKNOWN"),
            "logic_anchors": result.get("passes", []),
            "neural_proposal": result.get("proposal", {}),
            "violations": violations,
            "timestamp": datetime.utcnow().isoformat()
        }

        return DecisionResponse(
            status=status,
            domain=result.get("domain", "UNKNOWN"),
            explanation=result["explanation"],
            violations=violations,
            reasoning_trace=reasoning_trace,
            proof=result.get("proof", "UNKNOWN"),
            shadow_mode=request.shadow_mode,
            prover_note=proposal.content,
            verifier_audit=audit["note"]
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Sovereign Manifold Error: {str(e)}")

@app.get("/ops")
def get_ops_metrics(user: User = Depends(require_role(UserRole.AUDITOR))):
    """
    Sovereign Ops Dashboard Endpoint.
    Requires AUDITOR or ADMIN clearance.
    """
    return orchestrator.verifier.manifold.monitor.get_ops_report()

@app.get("/analytics/summary")
async def get_analytics_summary(user: User = Depends(require_role(UserRole.AUDITOR))):
    """Returns a high-level health and decision summary."""
    return orchestrator.verifier.manifold.analytics.generate_health_summary()

@app.get("/analytics/trends")
async def get_analytics_trends(limit: int = 50, user: User = Depends(require_role(UserRole.AUDITOR))):
    """Returns scoring trends over time."""
    return orchestrator.verifier.manifold.analytics.get_score_trends(limit=limit)

@app.get("/analytics/heatmap")
async def get_analytics_heatmap(user: User = Depends(require_role(UserRole.AUDITOR))):
    """Returns the rule violation heatmap."""
    return orchestrator.verifier.manifold.analytics.get_violation_heatmap()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
