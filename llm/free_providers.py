"""
AMORA Free LLM Providers Module
Component Tag: [A. LLM Provider Infrastructure - Free APIs]

Integrates free-tier LLM APIs so users can get answers directly
on the AMOF website without being redirected elsewhere.

All API calls are made SERVER-SIDE from the FastAPI backend.

Supported providers (all free tier, no APK required):
  - Groq        : Llama 3.1 / Gemma2 — 14,400 req/day free
  - Gemini      : gemini-1.5-flash   — 1,500 req/day free
  - HuggingFace : Many open models   — rate-limited free tier
  - Mistral     : mistral-7b-instruct — rate-limited free tier
  - Cohere      : command-r           — 1,000 req/month free

How to get free API keys (web signup, no download):
  Groq        → https://console.groq.com
  Gemini      → https://aistudio.google.com/app/apikey
  HuggingFace → https://huggingface.co/settings/tokens
  Mistral     → https://console.mistral.ai
  Cohere      → https://dashboard.cohere.com
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional
from dotenv import load_dotenv

import requests

from llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

load_dotenv()



# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _count_tokens(text: str) -> int:
    """Heuristic: ~1.3 tokens per word."""
    return max(1, int(len(text.split()) * 1.3))


def _build_messages(query: str, evidence_context: str) -> list:
    """Build standard OpenAI-style messages list."""
    user_content = USER_PROMPT_TEMPLATE.format(
        query=query, evidence_context=evidence_context
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_content},
    ]


def _base_result(answer: str, prompt_text: str, provider: str) -> Dict[str, Any]:
    """Build unified result dict from answer text."""
    p = _count_tokens(prompt_text)
    o = _count_tokens(answer)
    return {
        "answer":                   answer,
        "prompt_tokens":            p,
        "output_tokens":            o,
        "total_tokens":             p + o,
        "metadata_ranking_tokens": 0,
        "provider_used":            provider,
    }


# ---------------------------------------------------------------------------
# 1. Groq — fastest free option (Llama 3.1 / Gemma2)
#    Sign up: https://console.groq.com  →  free API key
# ---------------------------------------------------------------------------

class GroqClient:
    """
    Calls Groq's OpenAI-compatible API.
    Free tier: 14,400 requests/day — no credit card required.
    Fastest inference available (~500 tokens/sec).

    Supported free models:
        llama-3.1-8b-instant   (default)
        llama3-groq-8b-8192-tool-use-preview
        gemma2-9b-it
        mixtral-8x7b-32768
    """

    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    DEFAULT_MODEL = "llama-3.1-8b-instant"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model   = model or os.getenv("GROQ_MODEL", self.DEFAULT_MODEL)

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list, temperature: float = 0.7) -> Dict[str, Any]:
        """Call Groq API and return unified result dict."""
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set. Get a free key at https://console.groq.com")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }
        payload = {
            "model":       self.model,
            "messages":    messages,
            "temperature": temperature,
            "max_tokens":  1024,
        }
        resp = requests.post(self.API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        answer  = data["choices"][0]["message"]["content"]
        usage   = data.get("usage", {})
        p_tok   = usage.get("prompt_tokens",     _count_tokens(" ".join(m["content"] for m in messages)))
        o_tok   = usage.get("completion_tokens", _count_tokens(answer))

        return {
            "answer":                   answer,
            "prompt_tokens":            p_tok,
            "output_tokens":            o_tok,
            "total_tokens":             p_tok + o_tok,
            "metadata_ranking_tokens": 0,
            "provider_used":            f"Groq/{self.model}",
        }

    def generate_answer(
        self,
        query: str,
        evidence_context: str,
        conflict_detected: bool = False,
    ) -> Dict[str, Any]:
        messages = _build_messages(query, evidence_context)
        return self.chat(messages)


# ---------------------------------------------------------------------------
# 2. Google Gemini — gemini-1.5-flash (1,500 req/day free)
#    Sign up: https://aistudio.google.com/app/apikey  →  free API key
# ---------------------------------------------------------------------------

class GeminiClient:
    """
    Calls Google Gemini via REST API.
    Free tier: 1,500 requests/day with gemini-1.5-flash.

    Sign up free at: https://aistudio.google.com/app/apikey
    """

    BASE_URL     = "https://generativelanguage.googleapis.com/v1beta/models"
    DEFAULT_MODEL = "gemini-flash-latest"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model   = model or os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL)

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list, temperature: float = 0.7) -> Dict[str, Any]:
        """Convert OpenAI messages to Gemini format and call the API."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set. Get a free key at https://aistudio.google.com/app/apikey")

        # Gemini uses 'contents' with role 'user'/'model'; merge system into first user
        system_txt = ""
        gemini_contents = []
        for m in messages:
            if m["role"] == "system":
                system_txt = m["content"]
            elif m["role"] == "user":
                combined = f"{system_txt}\n\n{m['content']}" if system_txt else m["content"]
                gemini_contents.append({"role": "user", "parts": [{"text": combined}]})
                system_txt = ""  # only prepend once
            elif m["role"] == "assistant":
                gemini_contents.append({"role": "model", "parts": [{"text": m["content"]}]})

        payload = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 1024,
            }
        }

        # Direct call with 5s timeout for fast responsiveness
        target_model = self.model or "gemini-flash-latest"
        url = f"{self.BASE_URL}/{target_model}:generateContent?key={self.api_key}"
        try:
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
            else:
                resp.raise_for_status()
        except requests.Timeout:
            raise TimeoutError(f"Google Gemini API timed out after 5s for model {target_model}")

        answer = (
            data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
        )
        usage = data.get("usageMetadata", {})
        p_tok = usage.get("promptTokenCount",     _count_tokens(" ".join(m["content"] for m in messages if isinstance(m["content"], str))))
        o_tok = usage.get("candidatesTokenCount", _count_tokens(answer))

        return {
            "answer":                   answer,
            "prompt_tokens":            p_tok,
            "output_tokens":            o_tok,
            "total_tokens":             p_tok + o_tok,
            "metadata_ranking_tokens": 0,
            "provider_used":            f"Gemini/{self.model}",
        }

    def generate_answer(
        self,
        query: str,
        evidence_context: str,
        conflict_detected: bool = False,
    ) -> Dict[str, Any]:
        messages = _build_messages(query, evidence_context)
        return self.chat(messages)


# ---------------------------------------------------------------------------
# 3. HuggingFace Inference API — many open models, free tier
#    Sign up: https://huggingface.co/settings/tokens  →  free token
# ---------------------------------------------------------------------------

class HuggingFaceClient:
    """
    Calls HuggingFace Inference API (serverless).
    Free tier: rate-limited, no credit card required.

    Default model: mistralai/Mistral-7B-Instruct-v0.3
    Other good free models:
        meta-llama/Llama-3.2-3B-Instruct
        google/gemma-2-2b-it
        microsoft/Phi-3-mini-4k-instruct
    """

    BASE_URL      = "https://api-inference.huggingface.co/models"
    DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        self.model   = model or os.getenv("HUGGINGFACE_MODEL", self.DEFAULT_MODEL)

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list, temperature: float = 0.7) -> Dict[str, Any]:
        """Call HuggingFace Inference API using chat-completion format."""
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY not set. Get a free token at https://huggingface.co/settings/tokens")

        url = f"https://api-inference.huggingface.co/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }
        payload = {
            "model":       self.model,
            "messages":    messages,
            "temperature": temperature,
            "max_tokens":  1024,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)

        # HuggingFace sometimes returns 503 when model is loading — retry once
        if resp.status_code == 503:
            estimated_time = resp.json().get("estimated_time", 20)
            time.sleep(min(estimated_time, 15))
            resp = requests.post(url, headers=headers, json=payload, timeout=60)

        resp.raise_for_status()
        data = resp.json()

        answer = data["choices"][0]["message"]["content"]
        usage  = data.get("usage", {})
        p_tok  = usage.get("prompt_tokens",     _count_tokens(" ".join(m["content"] for m in messages)))
        o_tok  = usage.get("completion_tokens", _count_tokens(answer))

        return {
            "answer":                   answer,
            "prompt_tokens":            p_tok,
            "output_tokens":            o_tok,
            "total_tokens":             p_tok + o_tok,
            "metadata_ranking_tokens": 0,
            "provider_used":            f"HuggingFace/{self.model}",
        }

    def generate_answer(
        self,
        query: str,
        evidence_context: str,
        conflict_detected: bool = False,
    ) -> Dict[str, Any]:
        messages = _build_messages(query, evidence_context)
        return self.chat(messages)


# ---------------------------------------------------------------------------
# 4. Mistral AI — free tier via official API
#    Sign up: https://console.mistral.ai  →  free API key
# ---------------------------------------------------------------------------

class MistralClient:
    """
    Calls Mistral AI's official API.
    Free tier available — no credit card required for basic usage.

    Default model: mistral-small-latest (fast & free)
    """

    API_URL       = "https://api.mistral.ai/v1/chat/completions"
    DEFAULT_MODEL = "mistral-small-latest"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY", "")
        self.model   = model or os.getenv("MISTRAL_MODEL", self.DEFAULT_MODEL)

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list, temperature: float = 0.7) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not set. Get a free key at https://console.mistral.ai")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }
        payload = {
            "model":       self.model,
            "messages":    messages,
            "temperature": temperature,
            "max_tokens":  1024,
        }
        resp = requests.post(self.API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        answer = data["choices"][0]["message"]["content"]
        usage  = data.get("usage", {})
        p_tok  = usage.get("prompt_tokens",     _count_tokens(" ".join(m["content"] for m in messages)))
        o_tok  = usage.get("completion_tokens", _count_tokens(answer))

        return {
            "answer":                   answer,
            "prompt_tokens":            p_tok,
            "output_tokens":            o_tok,
            "total_tokens":             p_tok + o_tok,
            "metadata_ranking_tokens": 0,
            "provider_used":            f"Mistral/{self.model}",
        }

    def generate_answer(
        self,
        query: str,
        evidence_context: str,
        conflict_detected: bool = False,
    ) -> Dict[str, Any]:
        messages = _build_messages(query, evidence_context)
        return self.chat(messages)


# ---------------------------------------------------------------------------
# 5. Cohere — command-r free tier
#    Sign up: https://dashboard.cohere.com  →  free API key
# ---------------------------------------------------------------------------

class CohereClient:
    """
    Calls Cohere's Chat API.
    Free tier: 1,000 requests/month — no credit card required.
    """

    API_URL       = "https://api.cohere.com/v2/chat"
    DEFAULT_MODEL = "command-r"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("COHERE_API_KEY", "")
        self.model   = model or os.getenv("COHERE_MODEL", self.DEFAULT_MODEL)

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list, temperature: float = 0.7) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("COHERE_API_KEY not set. Get a free key at https://dashboard.cohere.com")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }
        payload = {
            "model":       self.model,
            "messages":    messages,
            "temperature": temperature,
        }
        resp = requests.post(self.API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        answer = data.get("message", {}).get("content", [{}])[0].get("text", "")
        usage  = data.get("usage", {})
        p_tok  = usage.get("billed_units", {}).get("input_tokens",  _count_tokens(" ".join(m["content"] for m in messages)))
        o_tok  = usage.get("billed_units", {}).get("output_tokens", _count_tokens(answer))

        return {
            "answer":                   answer,
            "prompt_tokens":            p_tok,
            "output_tokens":            o_tok,
            "total_tokens":             p_tok + o_tok,
            "metadata_ranking_tokens": 0,
            "provider_used":            f"Cohere/{self.model}",
        }

    def generate_answer(
        self,
        query: str,
        evidence_context: str,
        conflict_detected: bool = False,
    ) -> Dict[str, Any]:
        messages = _build_messages(query, evidence_context)
        return self.chat(messages)


# ---------------------------------------------------------------------------
# Universal Free LLM Router
# ---------------------------------------------------------------------------

FREE_PROVIDERS = {
    "groq":         GroqClient,
    "gemini":       GeminiClient,
    "huggingface":  HuggingFaceClient,
    "mistral":      MistralClient,
    "cohere":       CohereClient,
}


def get_free_provider(provider_name: str) -> Any:
    """
    Factory: return an instantiated free LLM client by name.

    Args:
        provider_name: One of 'groq', 'gemini', 'huggingface', 'mistral', 'cohere'

    Returns:
        Instantiated client object with a .generate_answer() method.

    Raises:
        ValueError: If the provider name is unknown.
    """
    name = provider_name.lower().strip()
    if name not in FREE_PROVIDERS:
        raise ValueError(
            f"Unknown free provider '{provider_name}'. "
            f"Choose from: {list(FREE_PROVIDERS.keys())}"
        )
    return FREE_PROVIDERS[name]()


def auto_select_free_provider() -> Optional[Any]:
    """
    Automatically pick the first configured free provider based on available API keys.
    Priority: Groq → Gemini → Mistral → HuggingFace → Cohere

    Returns:
        Instantiated client, or None if no API key is set.
    """
    priority = ["groq", "gemini", "mistral", "huggingface", "cohere"]
    for name in priority:
        client = FREE_PROVIDERS[name]()
        if client.is_configured():
            return client
    return None
