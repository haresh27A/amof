import requests
import json

queries = [
    "What is the current inventory stock quantity of Quantum X Laptop?",
    "What does the company return policy say about unopened merchandise and refund timeframe?",
    "Which product has generated the highest sales revenue?",
    "What is the capital of France?"
]

print("=== RUNNING MULTIPLE INPUTS FOR ACADEMIC EVALUATION ===")

for i, q in enumerate(queries, 1):
    print(f"\n=======================================================")
    print(f"EXPERIMENT {i}: QUERY = \"{q}\"")
    print(f"=======================================================")
    
    # 1. Panel A: AMORA
    try:
        r_a = requests.post("http://127.0.0.1:8000/query", json={
            "query": q,
            "provider": "amora-fast",
            "mode": "weighted",
            "top_k": 5
        }, timeout=20)
        da = r_a.json()
        print("\n--- PANEL A (AMORA + Qwen) ---")
        print(f"Retrieval Required : {da.get('retrieval_required')}")
        print(f"Activation Score   : {da.get('k_activation_score')}")
        print(f"Selected Sources   : {[s['name'] for s in da.get('selected_sources', [])]}")
        print(f"Evidence Count     : {da.get('retrieved_evidence_count')}")
        print(f"Prompt Tokens      : {da.get('token_details', {}).get('prompt_tokens')}")
        print(f"Output Tokens      : {da.get('token_details', {}).get('output_tokens')}")
        print(f"Total Tokens       : {da.get('tokens')}")
        print(f"Latency            : {da.get('latency_ms')} ms")
        print(f"Accuracy Score     : {round(da.get('accuracy_score', 0) * 100, 2)}%")
        print(f"Synthesized Answer : {da.get('final_answer')[:160]}...")
    except Exception as e:
        print("Panel A Error:", e)

    # 2. Panel B: Without AMORA (Full Dataset Check)
    try:
        r_b = requests.post("http://127.0.0.1:8000/llm/chat", json={
            "question": q,
            "provider": "gemini",
            "evidence_context": ""
        }, timeout=25)
        db = r_b.json()
        print("\n--- PANEL B (Without AMORA / Direct Baseline) ---")
        print(f"Prompt Tokens      : {db.get('prompt_tokens')}")
        print(f"Output Tokens      : {db.get('output_tokens')}")
        print(f"Total Tokens       : {db.get('total_tokens')}")
        print(f"Latency            : {db.get('latency_ms')} ms")
        print(f"Accuracy Score     : {round(db.get('accuracy_score', 0) * 100, 2)}%")
        print(f"Direct Answer      : {db.get('answer')[:160]}...")
    except Exception as e:
        print("Panel B Error:", e)
