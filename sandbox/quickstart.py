from lnt_sovereign.client import LNTClient
import json

def test_quickstart():
    print("--- LNT Developer Simulation: First Contact ---")
    
    # Instance the client as documented
    client = LNTClient()
    
    # Try the Visa Application example (documented in README as public)
    proposal = {
        "velocity": 450,
        "context": {"age_days": 2}
    }
    
    print(f"Auditing proposal: {json.dumps(proposal, indent=2)}")
    
    # Attempt audit
    try:
        result = client.audit(manifest_id="visa_application", proposal=proposal)
        
        print(f"\nAudit Status: {result.status}")
        print(f"Validation Score: {result.score}")
        
        if result.status == "PASS":
            print("✅ Quickstart Success: Passed validation criteria.")
        else:
            print("❌ Quickstart Result: Failed validation (Expected if rules were met).")
            for violation in result.violations:
                print(f"  - Violation: {violation.description}")

    except Exception as e:
        print(f"🔥 Error during Quickstart: {str(e)}")

if __name__ == "__main__":
    test_quickstart()
