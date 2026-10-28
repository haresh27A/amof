import requests
import json

print("Testing Compare API Endpoints...")
print("\n--- PANEL A: Qwen with AMORA ---")
try:
    r_a = requests.post("http://127.0.0.1:8000/query", json={
        "query": "What is the current inventory of Quantum X Laptop?",
        "provider": "amora-fast",
        "mode": "weighted",
        "top_k": 5,
        "forced_retrieval": True
    }, timeout=10)
    data_a = r_a.json()
    print("Panel A Accuracy:", f"{data_a.get('accuracy_score', 0)*100:.1f}%")
    print("Panel A Latency:", f"{data_a.get('latency_ms')} ms")
    print("Panel A Tokens:", f"{data_a.get('tokens')} tokens")
    print("Panel A Answer:", data_a.get("final_answer", "")[:120])
except Exception as e:
    print("Error A:", e)

print("\n--- PANEL B: Gemini without AMORA (Full Dataset Check) ---")
try:
    r_b = requests.post("http://127.0.0.1:8000/llm/chat", json={
        "question": "What is the current inventory of Quantum X Laptop?",
        "provider": "gemini",
        "evidence_context": ""
    }, timeout=30)
    data_b = r_b.json()
    print("Panel B Accuracy:", f"{data_b.get('accuracy_score', 0)*100:.1f}%")
    print("Panel B Latency:", f"{data_b.get('latency_ms')} ms")
    print("Panel B Tokens:", f"{data_b.get('total_tokens')} tokens")
    print("Panel B Answer:", data_b.get("answer", "")[:120])
except Exception as e:
    print("Error B:", e)
