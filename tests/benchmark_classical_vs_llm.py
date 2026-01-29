import time

from lnt_sovereign.core.kernel import KernelEngine
from lnt_sovereign.core.neural import NeuralParser


def run_benchmark():
    print("--- LNT Benchmark: Classical ML vs. Neuro-Symbolic (LLM) ---")
    
    engine = KernelEngine()
    parser = NeuralParser()
    
    # 1. Setup Manifests
    llm_manifest_path = "lnt_sovereign/manifests/examples/visa_application.json"
    classical_manifest_path = "lnt_sovereign/manifests/examples/credit_score_v1.json"
    
    llm_manifest = engine.load_manifest(llm_manifest_path)
    engine.load_manifest(classical_manifest_path)

    # 2. Neuro-Symbolic Loop (LLM Style)
    # Includes text parsing + symbolic audit
    user_text = "Applicant is 25 years old and applying for a work visa with a valid passport."
    
    start_llm = time.perf_counter()
    proposal = parser.parse_intent(user_text, llm_manifest)
    res_llm = engine.trace_evaluate(proposal)
    end_llm = time.perf_counter()
    
    llm_time_ms = (end_llm - start_llm) * 1000

    # 3. Direct Classical ML Audit (Classical Style)
    # Numerical data directly into the kernel
    classical_proposal = {
        "debt_to_income_ratio": 0.35,
        "fico_score": 720,
        "applicant_age": 25,
        "loan_to_value_ratio": 0.80
    }
    
    start_classical = time.perf_counter()
    res_classical = engine.trace_evaluate(classical_proposal)
    end_classical = time.perf_counter()
    
    classical_time_ms = (end_classical - start_classical) * 1000

    print("\n[Neuro-Symbolic / LLM Mode]")
    print("> Task: Parse Text + Audit Logic")
    print(f"> Latency: {llm_time_ms:.4f} ms")
    print(f"> Status: {res_llm['status']}")

    print("\n[Classical ML / Direct Mode]")
    print("> Task: Direct Data Audit (XGBoost/Tabular)")
    print(f"> Latency: {classical_time_ms:.4f} ms")
    print(f"> Status: {res_classical['status']}")

    speedup = llm_time_ms / classical_time_ms
    print(f"\nSPEEDUP (Classical vs LLM): {speedup:.1f}x")
    print("-" * 55)

if __name__ == "__main__":
    run_benchmark()
