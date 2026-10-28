import sys, os
sys.path.insert(0, os.path.abspath("."))
import time
from backend.api.query import free_llm_chat, FreeLLMChatRequest
from backend.api.query import execute_query_pipeline, QueryRequest
from database.session import SessionLocal

db = SessionLocal()

print("Testing direct free_llm_chat for gemini...")
t0 = time.time()
try:
    req_b = FreeLLMChatRequest(
        question="What is the current inventory of Quantum X Laptop?",
        provider="gemini",
        evidence_context=""
    )
    res_b = free_llm_chat(req_b)
    print("Gemini answer:", res_b.answer[:150])
    print("Gemini latency:", res_b.latency_ms)
    print("Gemini accuracy:", res_b.accuracy_score)
    print("Gemini tokens:", res_b.total_tokens)
except Exception as e:
    import traceback
    traceback.print_exc()

print("\nTesting execute_query_pipeline for qwen...")
try:
    req_a = QueryRequest(
        query="What is the current inventory of Quantum X Laptop?",
        provider="qwen",
        mode="weighted",
        top_k=5,
        forced_retrieval=True
    )
    res_a = execute_query_pipeline(req_a, db)
    print("Qwen answer:", res_a.final_answer[:150])
    print("Qwen provider used:", res_a.provider_used)
    print("Qwen is stub:", res_a.used_stub_response)
    print("Qwen accuracy:", res_a.accuracy_score)
    print("Qwen latency:", res_a.latency_ms)
    print("Qwen tokens:", res_a.tokens)
except Exception as e:
    import traceback
    traceback.print_exc()

db.close()
