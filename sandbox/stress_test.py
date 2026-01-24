from lnt_sovereign.client import LNTClient

def stress_test():
    client = LNTClient()
    
    print("--- LNT Edge Case & Stress Testing ---")
    
    # 1. Invalid Manifest ID
    print("\n[Case 1] Invalid Manifest ID:")
    try:
        client.audit(manifest_id="non_existent_manifest", proposal={})
    except Exception as e:
        print(f"✅ Caught expected error for invalid manifest: {str(e)}")

    # 2. Missing Required Fields (Visa Application expects 'velocity')
    print("\n[Case 2] Missing Required Fields:")
    try:
        # Note: visa_application rules check 'velocity' and 'age_days'
        result = client.audit(manifest_id="visa_application", proposal={"unknown_field": 100})
        print(f"Status: {result.status}")
        print(f"Violations for missing data: {len(result.violations)}")
        for v in result.violations:
            print(f"  - {v['description']}")
    except Exception as e:
        print(f"🔥 Unexpected crash on missing fields: {str(e)}")

    # 3. Type Mismatch (Passing string where number expected)
    print("\n[Case 3] Type Mismatch:")
    try:
        result = client.audit(manifest_id="visa_application", proposal={"velocity": "TOO_FAST", "context": {"age_days": 10}})
        print(f"Status: {result.status}")
        if result.status == "FAIL":
             print("✅ Handled type mismatch (Logic failure rather than crash).")
    except Exception as e:
        print(f"🔥 Potential crash on type mismatch: {str(e)}")

    # 4. Extreme Values
    print("\n[Case 4] Extreme Values:")
    try:
        result = client.audit(manifest_id="visa_application", proposal={"velocity": 999999, "context": {"age_days": -1}})
        print(f"Status: {result.status}")
        print(f"Score: {result.score}")
    except Exception as e:
        print(f"🔥 Crash on extreme values: {str(e)}")

if __name__ == "__main__":
    stress_test()
