import asyncio
from lnt_sovereign.client import LNTClient

async def main():
    print("🌟 LNT Sovereign Platform Demo")
    
    # 1. Initialize the Client (SOC-2 API Key)
    client = LNTClient(api_key="lnt-sovereign-secret-2026")
    
    # 2. Audit a Visa Application
    print("\n--- Auditing Visa Application ---")
    visa_text = "Applicant has a passport and is sponsored by a tech group. Looking to settle with $50000."
    result = await client.audit_application(visa_text)
    
    print(f"Status: {result.get('status')}")
    print(f"Domain: {result.get('domain')}")
    if client.check_proof_integrity(result):
        print(f"✅ Sovereign Proof: {result.get('proof')}")
    
    # 3. Check System Operational Status
    print("\n--- Checking Sovereign Ops Dashboard ---")
    ops = await client.get_system_health()
    print(f"Reasoning Gap: {ops.get('metrics', {}).get('hallucination_rate')}")
    print(f"AIDA Fairness: {ops.get('metrics', {}).get('compliance_level')}")

if __name__ == "__main__":
    asyncio.run(main())
