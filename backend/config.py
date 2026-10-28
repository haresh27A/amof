"""
AMORA Project Configuration System
Component Tag: [A. Infrastructure / Utility]
"""

import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "AMORA RAG System")
    debug: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./amora.db")

    # LLM & Embedding
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    qwen_model_name: str = os.getenv("QWEN_MODEL_NAME", "llama3:latest")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # ── Local Ollama generation limits ────────────────────────────────────────
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
    # `num_predict` capped at 350 to deliver concise answers with only essential facts.
    ollama_num_predict: int = int(os.getenv("OLLAMA_NUM_PREDICT", "350"))
    # qwen3.6 is a reasoning model and returns an empty `content` field, putting its
    # output in `thinking` instead. Disable thinking so the answer lands in `content`.
    ollama_think: bool = os.getenv("OLLAMA_THINK", "false").lower() in ("true", "1", "yes")

    # ── Free LLM Provider API Keys (all free tier, no APK required) ──────────
    # Groq  → https://console.groq.com          (14,400 req/day free)
    # Gemini → https://aistudio.google.com      (1,500 req/day free)
    # HuggingFace → https://huggingface.co/settings/tokens (rate-limited free)
    # Mistral → https://console.mistral.ai      (free tier)
    # Cohere  → https://dashboard.cohere.com   (1,000 req/month free)
    free_llm_provider: str = os.getenv("FREE_LLM_PROVIDER", "groq")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    huggingface_api_key: str = os.getenv("HUGGINGFACE_API_KEY", "")
    huggingface_model: str = os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "")
    mistral_model: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    cohere_api_key: str = os.getenv("COHERE_API_KEY", "")
    cohere_model: str = os.getenv("COHERE_MODEL", "command-r")
    
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    # "auto"  -> use SentenceTransformer, silently fall back to the deterministic hash encoder
    # "model" -> use SentenceTransformer, raise if it cannot be loaded
    # "hash"  -> always use the deterministic hash encoder (no semantic embeddings)
    embedding_backend: str = os.getenv("EMBEDDING_BACKEND", "auto").strip().lower()

    # AMORA Mathematical Parameters
    alpha_reliability: float = float(os.getenv("ALPHA_RELIABILITY", "0.6"))
    beta_availability: float = float(os.getenv("BETA_AVAILABILITY", "0.4"))
    lambda_freshness: float = float(os.getenv("LAMBDA_FRESHNESS", "0.001"))
    bayes_alpha: float = float(os.getenv("BAYES_ALPHA", "1.0"))
    bayes_beta: float = float(os.getenv("BAYES_BETA", "1.0"))
    
    prefilter_top_n: int = int(os.getenv("PREFILTER_TOP_N", "200"))
    default_top_k: int = int(os.getenv("DEFAULT_TOP_K", "5"))

    # Efficiency metric normalization parameters
    eff_alpha: float = float(os.getenv("EFFICIENCY_ALPHA_TOKENS", "0.4"))
    eff_beta: float = float(os.getenv("EFFICIENCY_BETA_LATENCY", "0.3"))
    eff_gamma: float = float(os.getenv("EFFICIENCY_GAMMA_COST", "0.3"))

settings = Settings()
