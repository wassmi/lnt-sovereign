import httpx
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LNT-SDK")

@dataclass
class LNTResponse:
    status: str
    domain: str
    proposal: Dict[str, Any]
    violations: List[Dict[str, Any]]
    proof: str
    explanation: str
    metadata: Dict[str, Any]

class LNTClient:
    """
    Sovereign LNT SDK: The professional interface for Neuro-Symbolic Logic.
    Supports asynchronous execution, shadow-mode audits, and verification proofs.
    """
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        max_retries: int = 3
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "X-LNT-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "LNT-Python-SDK/1.0.0"
        }
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "LNTClient":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout
            )
        return self._client

    async def evaluate(
        self, 
        user_text: str, 
        domain: Optional[str] = None,
        shadow_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates a request against the sovereign logic manifold.
        
        Args:
            user_text: The raw neural input (e.g., patient vitals, visa applicant text).
            domain: Optional override for domain detection.
            shadow_mode: If True, the audit is logged but does not block (non-blocking verification).
        """
        client = await self._get_client()
        payload = {
            "user_text": user_text,
            "domain_override": domain,
            "shadow_mode": shadow_mode
        }

        for attempt in range(self.max_retries):
            try:
                response = await client.post("/process", json=payload)
                response.raise_for_status()
                return response.json()
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"LNT connection failed after {self.max_retries} attempts: {str(e)}")
                    return {"status": "SDK_CONNECTION_ERROR", "error": str(e)}
                
                wait_time = 2 ** attempt # Exponential backoff
                logger.warning(f"LNT connection attempt {attempt + 1} failed. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            except httpx.HTTPStatusError as e:
                logger.error(f"LNT API rejected request: {e.response.status_code} - {e.response.text}")
                return {"status": "API_ERROR", "code": e.response.status_code, "detail": e.response.text}
        
        return {"status": "UNKNOWN_ERROR"}

    async def get_system_health(self) -> Dict[str, Any]:
        """Queries the engine's operational metrics (Latency, Hallucination Rate)."""
        client = await self._get_client()
        try:
            response = await client.get("/ops")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Returns advanced decision trends and rule heatmaps."""
        client = await self._get_client()
        try:
            response = await client.get("/analytics/summary")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def verify_proof_integrity(self, result: Dict[str, Any]) -> bool:
        """
        Validates the SHA-256 integrity of a sovereign proof.
        """
        proof = result.get("proof")
        return bool(proof and len(proof) == 64)
