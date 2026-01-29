import os
import sys

try:
    from lnt_sovereign.core.topology import TopologyOrchestrator
    print("✅ Successfully imported lnt_sovereign components.")
    
    # Check if manifests are present in the installed package
    import lnt_sovereign
    pkg_path = os.path.dirname(lnt_sovereign.__file__)
    example_dir = os.path.join(pkg_path, "manifests", "examples")
    mega_dir = os.path.join(pkg_path, "manifests", "mega")
    vault_dir = os.path.join(pkg_path, "vault")
    
    if os.path.exists(example_dir) and len(os.listdir(example_dir)) > 0:
        print(f"✅ Public examples found in package: {example_dir}")
    else:
        print("❌ Public examples MISSING from package!")
        sys.exit(1)
        
    if not os.path.exists(mega_dir) or len(os.listdir(mega_dir)) == 0:
        print("✅ Proprietary 'mega' manifests correctly EXCLUDED.")
    else:
        print("❌ Proprietary 'mega' manifests leaked into package!")
        sys.exit(1)
        
    if not os.path.exists(vault_dir):
        print("✅ Commercial 'vault' correctly EXCLUDED.")
    else:
        print("❌ Commercial 'vault' leaked into package!")
        sys.exit(1)

    print("\n--- Running Quick Smoke Test ---")
    manifold = TopologyOrchestrator()
    # Test a known example
    res = manifold.process_application("Visa application with passport and funding.")
    print(f"Status: {res['status']}")
    print(f"Domain: {res['domain']}")
    
    if res['status'] in ["CERTIFIED", "REJECTED_BY_LOGIC"]:
        print("✅ Smoke test PASSED.")
    else:
        print(f"❌ Smoke test FAILED: Unexpected status {res['status']}")
        sys.exit(1)

    print("\n🚀 PACKAGE READY FOR PYPI RELEASE 🚀")

except ImportError as e:
    print(f"❌ Failed to import lnt_sovereign: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Verification error: {e}")
    sys.exit(1)
