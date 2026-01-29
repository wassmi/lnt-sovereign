import json
import os
import sys

# Ensure we can import from the root
sys.path.append(os.getcwd())

from lnt_sovereign.core.formal import FormalVerifier
from lnt_sovereign.core.kernel import KernelEngine


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("====================================================")
    print("🚀 LNT-SOVEREIGN: INTERACTIVE DEVELOPER PLAYGROUND")
    print("====================================================")
    print("This tool allows you to test logic manifests instantly.")
    
    # Check for example manifests
    manifest_dir = "lnt_sovereign/manifests/examples"
    if not os.path.exists(manifest_dir):
        print(f"Error: Manifest directory {manifest_dir} not found.")
        return

    examples = [f for f in os.listdir(manifest_dir) if f.endswith('.json')]
    
    if not examples:
        print("No example manifests found. Please create one in lnt_sovereign/manifests/examples/")
        return

    print("\nAvailable Manifests:")
    for idx, name in enumerate(examples):
        print(f"[{idx}] {name}")

    try:
        choice = int(input("\nSelect a manifest to load (index): "))
        manifest_path = os.path.join(manifest_dir, examples[choice])
    except (ValueError, IndexError):
        print("Invalid selection. Exiting.")
        return

    # Load Manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    print(f"\n✅ Loaded: {manifest.get('domain_name', 'Unnamed Domain')}")
    print(f"Rules: {len(manifest.get('constraints', []))}")

    # 1. Formal Verification Phase
    print("\n--- PHASE 1: FORMAL VERIFICATION (Z3) ---")
    verifier = FormalVerifier()
    consistent, error = verifier.verify_consistency(manifest)
    
    if consistent:
        print("🟢 STATUS: PROVABLY CONSISTENT")
        satisfiable, example = verifier.verify_satisfiable(manifest)
        if satisfiable:
            print("🟢 SATISFIABLE: At least one valid input exists.")
            print(f"💡 Example Valid Input: {example}")
    else:
        print("🔴 STATUS: LOGIC CONTRADICTION FOUND")
        print(f"❌ Error: {error}")
        return

    # 2. Live Evaluation Phase
    print("\n--- PHASE 2: LIVE PROPOSAL EVALUATION (Vectorized) ---")
    kernel = KernelEngine(manifest_path)
    
    proposal = {}
    entities = manifest.get('entities', [])
    
    print("Please enter values for the following entities (press enter for None):")
    for entity in entities:
        val = input(f"  > {entity}: ")
        if val != "":
            try:
                # Basic auto-typing
                if val.lower() in ['true', 'false']:
                    proposal[entity] = val.lower() == 'true'
                elif '.' in val:
                    proposal[entity] = float(val)
                else:
                    proposal[entity] = int(val)
            except ValueError:
                proposal[entity] = val

    # Evaluate
    result = kernel.trace_evaluate(proposal)
    
    print("\n--- EVALUATION RESULTS ---")
    status_color = "🟢" if result['status'] == 'CERTIFIED' else "🔴"
    print(f"STATUS: {status_color} {result['status']}")
    print(f"SCORE:  {result.get('score', 0.0)}/100.0")
    
    if result.get('violations'):
        print("\nVIOLATIONS FOUND:")
        for v in result['violations']:
            print(f"  ❌ [{v['id']}] {v.get('description', 'No description')}")
    
    if result.get('passes'):
        print("\nRULES PASSED:")
        for p in result['passes']:
            print(f"  ✅ [{p['id']}]")

    print("\n====================================================")
    print("Playground session complete. Optimized for 2026 AI Safety.")
    print("====================================================")

if __name__ == "__main__":
    main()
