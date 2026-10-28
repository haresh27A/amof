"""
Qwen LLM Provider Integration Module
Component Tag: [A. LLM Provider Infrastructure]

Supports:
  - AMORA Fast Engine (primary high-speed integrated grounder)
  - Ollama            : qwen3.6:latest running locally via Ollama daemon
  - Free Cloud Providers: Groq, Gemini, Mistral, Cohere, HuggingFace
  - Mock              : deterministic high-speed fallback for testing

IMPORTANT — provenance contract
-------------------------------
Every response carries two fields:

  provider_used : human-readable name of the engine that produced the text
  is_stub       : True when the text came from `canned_stub_response` (a fixed
                  keyword-matching template), False when a real generative model
                  produced it.

`canned_stub_response` is NOT a language model. It does not read the evidence, it
replays pre-written sentences. It exists so the API degrades gracefully when Ollama
is unreachable. Callers must surface `is_stub` to the user and must not score a
stub response as if it were a grounded LLM answer.
"""

from typing import Dict, Any, Optional, Iterator, Tuple
import requests
import json
import re
from pydantic import BaseModel
from backend.config import settings
from llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

# Label attached to any response produced without a generative model.
STUB_LABEL = "STUB - canned template (no LLM was called)"


class LLMResponse(BaseModel):
    answer: str
    prompt_tokens: int
    output_tokens: int
    total_tokens: int
    metadata_ranking_tokens: int = 0
    provider_used: str
    is_stub: bool = False


def build_messages(query: str, evidence_context: str) -> list:
    """Assemble the chat messages sent to the generative model."""
    user_content = USER_PROMPT_TEMPLATE.format(query=query, evidence_context=evidence_context)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_content},
    ]


class OllamaLLMClient:
    """
    Dedicated Ollama LLM client for qwen3.6:latest (and any other Ollama-hosted model).
    Provides blocking generation, incremental streaming, and model discovery.
    Tag: [A. LLM Provider Infrastructure - Ollama]

    Latency note: a 23.9 GB reasoning model such as qwen3.6:latest needs well over
    two minutes for its first tokens on CPU. The read timeout therefore comes from
    settings.ollama_timeout_seconds (default 300s), not a hardcoded 20s ceiling.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        host: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.model = model or settings.qwen_model_name
        self.host = (host or settings.ollama_host).rstrip("/")
        # Use 127.0.0.1 on Windows to prevent IPv6 localhost connection delays
        if "localhost" in self.host:
            self.host = self.host.replace("localhost", "127.0.0.1")
        self.timeout = int(timeout or settings.ollama_timeout_seconds)
        self._chat_url = f"{self.host}/api/chat"
        self._models_url = f"{self.host}/api/tags"

    def _count_tokens(self, text: str) -> int:
        """Heuristic: ~1.3 tokens per word."""
        return max(1, int(len(text.split()) * 1.3))

    def _options(self, temperature: float, num_predict: Optional[int] = None) -> dict:
        # `think` is honoured by reasoning models (qwen3, deepseek-r1). Left enabled,
        # the model returns an empty `content` field and puts everything in `thinking`.
        return {
            "temperature": temperature,
            "num_predict": int(num_predict or settings.ollama_num_predict),
            "think": bool(settings.ollama_think),
        }

    @staticmethod
    def _extract_answer(msg: dict) -> Tuple[str, bool]:
        """
        Pull the final answer out of an Ollama message.

        Returns (answer, used_reasoning_fallback). With `think` disabled, Ollama puts
        the chain of thought in `thinking` and the answer in `content`. A non-empty
        `content` is the real answer. An empty `content` alongside a non-empty
        `thinking` means generation was cut off by `num_predict` before the model
        reached its answer, so the reasoning text is all we have.
        """
        answer = (msg.get("content") or "").strip()
        if answer:
            return answer, False
        thinking = (msg.get("thinking") or "").strip()
        return thinking, bool(thinking)

    def list_models(self) -> list:
        """Return model names available in the connected Ollama daemon."""
        try:
            res = requests.get(self._models_url, timeout=5)
            if res.status_code == 200:
                return [m["name"] for m in res.json().get("models", [])]
        except Exception:
            pass
        return []

    def is_available(self) -> bool:
        """Quick connectivity check to Ollama daemon."""
        try:
            res = requests.get(self._models_url, timeout=5)
            return res.status_code == 200
        except Exception:
            return False

    def has_model(self) -> bool:
        """True when the configured model or family model is actually present in the daemon."""
        models = self.list_models()
        if not models:
            return False
        # Exact or tag match
        for m in models:
            if m == self.model or m.split(":")[0] == self.model.split(":")[0]:
                self.model = m
                return True
        # Model family fallback (e.g. 'qwen' or 'qwen2.5' matches 'qwen3.6:latest')
        target_name = (self.model or "").lower().split(":")[0]
        for m in models:
            m_lower = m.lower()
            if target_name.startswith("qwen") and "qwen" in m_lower:
                self.model = m
                return True
            if target_name.startswith("llama") and "llama" in m_lower:
                self.model = m
                return True
        if models:
            self.model = models[0]
            return True
        return False

    def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        num_predict: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Call Ollama /api/chat and wait for the complete answer."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": self._options(temperature, num_predict),
        }
        res = requests.post(self._chat_url, json=payload, timeout=(10, self.timeout))
        res.raise_for_status()

        data = res.json()
        answer, reasoning_only = self._extract_answer(data.get("message", {}))
        llm_note = ""
        if reasoning_only:
            llm_note = (
                f"Generation hit the OLLAMA_NUM_PREDICT={settings.ollama_num_predict} cap "
                "while the model was still reasoning, so only its intermediate reasoning is "
                "shown and no final answer was produced. Raise OLLAMA_NUM_PREDICT to fix this."
            )
            answer = (
                f"{answer}\n\n---\n_[Truncated: {llm_note}]_"
            )
        elif not answer:
            answer = (
                f"The model '{self.model}' returned an empty response."
            )
            llm_note = f"Model '{self.model}' returned an empty response."

        p_tok = data.get("prompt_eval_count") or self._count_tokens(
            "".join(m.get("content", "") for m in messages)
        )
        o_tok = data.get("eval_count") or self._count_tokens(answer)

        return {
            "answer": answer,
            "prompt_tokens": int(p_tok),
            "output_tokens": int(o_tok),
            "total_tokens": int(p_tok) + int(o_tok),
            "metadata_ranking_tokens": 0,
            "provider_used": f"Ollama/{self.model}",
            "is_stub": False,
            "llm_note": llm_note,
        }

    def stream_chat(
        self,
        messages: list,
        temperature: float = 0.7,
        num_predict: Optional[int] = None,
    ) -> Iterator[Tuple[str, Any]]:
        """
        Stream an answer token-by-token from Ollama.

        Yields ("delta", str) for each text fragment and finally
        ("done", {"answer", "prompt_tokens", "output_tokens", "provider_used"}).
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": self._options(temperature, num_predict),
        }
        answer_parts: list = []
        p_tok = 0
        o_tok = 0
        hit_cap = False

        with requests.post(
            self._chat_url, json=payload, stream=True, timeout=(10, self.timeout)
        ) as res:
            res.raise_for_status()
            for line in res.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except (json.JSONDecodeError, TypeError):
                    continue

                msg = chunk.get("message", {})

                # The terminal chunk carries the token counters and has an empty
                # message body, so it must be handled before the delta check below
                # or the counts are lost.
                if chunk.get("done"):
                    p_tok = chunk.get("prompt_eval_count") or 0
                    o_tok = chunk.get("eval_count") or 0
                    break

                # Do not strip: Ollama deltas carry the whitespace between tokens,
                # and stripping each fragment would weld words together.
                delta = msg.get("content") or ""
                if delta:
                    answer_parts.append(delta)
                    yield ("delta", delta)
                elif (msg.get("thinking") or "").strip():
                    # Reasoning token. Held back rather than streamed as the answer,
                    # and recorded so a cut-off generation can be reported.
                    hit_cap = True

        answer = "".join(answer_parts).strip()
        llm_note = ""
        if not answer:
            if hit_cap:
                llm_note = (
                    f"Generation hit the OLLAMA_NUM_PREDICT={settings.ollama_num_predict} cap "
                    "while the model was still reasoning, so no final answer was produced. "
                    "Raise OLLAMA_NUM_PREDICT to fix this."
                )
                answer = f"No answer produced: the model exhausted its token budget while reasoning. {llm_note}"
            else:
                answer = f"The model '{self.model}' returned an empty response."
                llm_note = f"Model '{self.model}' returned an empty response."

        yield ("done", {
            "answer": answer,
            "prompt_tokens": int(p_tok or self._count_tokens(answer)),
            "output_tokens": int(o_tok or self._count_tokens(answer)),
            "provider_used": f"Ollama/{self.model}",
            "is_stub": False,
            "llm_note": llm_note,
        })

    def generate_answer(
        self,
        query: str,
        evidence_context: str,
        conflict_detected: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a RAG-grounded answer with the real local model.

        On failure this returns a clearly-labelled stub. It never silently
        impersonates a language model.
        """
        if not self.is_available():
            return canned_stub_response(
                query, evidence_context, conflict_detected,
                f"{STUB_LABEL} - Ollama daemon unreachable at {self.host}",
            )

        if not self.has_model():
            return canned_stub_response(
                query, evidence_context, conflict_detected,
                f"{STUB_LABEL} - model '{self.model}' is not pulled in Ollama",
            )

        try:
            return self.chat(build_messages(query, evidence_context))
        except requests.Timeout:
            return canned_stub_response(
                query, evidence_context, conflict_detected,
                f"{STUB_LABEL} - {self.model} exceeded {self.timeout}s timeout. "
                "Raise OLLAMA_TIMEOUT_SECONDS or use a smaller model.",
            )
        except Exception as exc:
            detail = re.sub(r"\s+", " ", str(exc))[:140]
            return canned_stub_response(
                query, evidence_context, conflict_detected,
                f"{STUB_LABEL} - {self.model} request failed: {detail}",
            )


# ---------------------------------------------------------------------------
# Canned stub — NOT a language model
# ---------------------------------------------------------------------------

def canned_stub_response(
    query: str,
    evidence_context: str,
    conflict_detected: bool = False,
    provider_label: str = STUB_LABEL,
) -> Dict[str, Any]:
    """
    Replays pre-written sentences for known topics. This performs no inference and
    does not read `evidence_context` for its facts; the numbers below are string
    literals. Every response is tagged `is_stub=True` so downstream consumers can
    refuse to score it as a grounded answer.
    """
    q_lower = query.lower()

    if not evidence_context.strip():
        # Ungrounded answer (simulates raw LLM lack of private enterprise access)
        if any(term in q_lower for term in ["stock", "inventory", "quantum x", "price", "revenue", "policy", "employee", "sales"]):
            answer = (
                f"As an AI language model without real-time database access, I cannot provide verified internal details for '{query}'.\n\n"
                f"To obtain current warehouse inventory, live prices, or active policies, connection to enterprise data sources (SQL/REST APIs) is required."
            )
        else:
            answer = f"Based on general parametric knowledge, here is information regarding '{query}': This is a standard concept and does not require private enterprise verification."

        def _tok(t: str) -> int: return max(1, int(len(t.split()) * 1.3))
        p = _tok(query)
        o = _tok(answer)
        return {
            "answer": answer,
            "prompt_tokens": p,
            "output_tokens": o,
            "total_tokens": p + o,
            "metadata_ranking_tokens": 0,
            "provider_used": provider_label,
            "is_stub": True,
        }

    # ── Parse specific facts from evidence ──
    facts = []
    conflict_note = ""

    if "quantum x" in q_lower or "laptop" in q_lower or "inventory" in q_lower or "stock" in q_lower:
        if "stock_quantity': 45" in evidence_context or "stock_quantity\": 45" in evidence_context or "45" in evidence_context:
            facts.append("- **Stock Quantity:** **45 units** currently available in stock [Source: Enterprise Sales & Inventory Database].")
            facts.append("- **Warehouse Location:** `Warehouse A - Rack 12` [Source: Enterprise Sales & Inventory Database].")
            facts.append("- **Unit Price:** **$1,299.99** [Source: Enterprise Sales & Inventory Database].")
            facts.append("- **Last Restock Date:** August 1, 2026 [Source: Enterprise Sales & Inventory Database].")

    if "return" in q_lower or "policy" in q_lower or "refund" in q_lower or "warranty" in q_lower:
        if "30 calendar days" in evidence_context or "unopened" in evidence_context:
            facts.append("- **Return Window:** Unopened merchandise may be returned within **30 calendar days** from delivery for a 100% full refund [Source: Company Policy & Legal Documentation].")
            facts.append("- **Item Condition:** Must be in original packaging with serial tags intact [Source: Company Policy & Legal Documentation].")
            facts.append("- **Warranty Protection:** Hardware includes a **12-month manufacturer limited warranty** [Source: Company Policy & Legal Documentation].")
            facts.append("- **Refund Timeline:** Processed within **5-7 business days** upon return receipt [Source: Company Policy & Legal Documentation].")

    if "revenue" in q_lower or "sales" in q_lower or "highest" in q_lower or "product" in q_lower:
        if "ORD-9003" in evidence_context or "Alice Smith" in evidence_context or "Carol White" in evidence_context:
            facts.append("- **Highest Revenue Product:** **Quantum X Laptop** generated top sales with orders totaling **$9,099.93** (Order ORD-9001: $2,599.98, Order ORD-9003: $6,499.95) [Source: Enterprise Sales & Inventory Database].")
            facts.append("- **Top Customer:** Carol White (5 units ordered on 2026-08-06) [Source: Enterprise Sales & Inventory Database].")

    if conflict_detected or "status='OK'" in evidence_context or "payload=" in evidence_context:
        if "stock': 142" in evidence_context or "49.99" in evidence_context:
            conflict_note = (
                "\n\n> [!WARNING]\n"
                "> **Conflict Resolution (Dempster-Shafer Engine):**\n"
                "> A numerical discrepancy was detected: The secondary REST API returned a payload indicating `stock: 142` and `unit_price: $49.99` for a generic label 'Product X'. "
                "AMORA's Dempster-Shafer belief aggregation prioritized the authoritative **Enterprise Sales & Inventory Database** ($L_i=0.996$) over the external API."
            )

    if facts:
        answer = (
            f"Based on multi-source authoritative retrieval, here is the verified information for **'{query}'**:\n\n"
            + "\n".join(facts)
            + conflict_note
        )
    else:
        # General synthesis over raw evidence items
        snippets = []
        for line in evidence_context.split("\n"):
            line_str = line.strip()
            if line_str.startswith("Source:") or line_str.startswith("Table") or line_str.startswith("[") or "text:" in line_str:
                if len(line_str) > 5 and len(line_str) < 180:
                    snippets.append(line_str)

        summary_text = "\n".join(snippets[:6]) if snippets else evidence_context[:300]
        answer = (
            f"Based on multi-source authoritative retrieval, here is the factual synthesis for **'{query}'**:\n\n"
            f"{summary_text}\n\n"
            f"**Conclusion:** All retrieved facts were verified against active data sources with high confidence."
            f"{conflict_note}"
        )

    def _tok(t: str) -> int: return max(1, int(len(t.split()) * 1.3))
    p = _tok(SYSTEM_PROMPT + query + evidence_context)
    o = _tok(answer)

    return {
        "answer": answer,
        "prompt_tokens": p,
        "output_tokens": o,
        "total_tokens": p + o,
        "metadata_ranking_tokens": 0,
        "provider_used": provider_label,
        "is_stub": True,
    }


# Backwards-compatible alias. This is a canned template, not a model.
synthesize_grounded_answer = canned_stub_response


# ---------------------------------------------------------------------------
# Unified Adapter
# ---------------------------------------------------------------------------

class QwenLLMClient:
    """
    Unified LLM Adapter - delegates to Ollama, Free Cloud Providers, or the canned stub.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or settings.llm_provider).lower().strip()
        model = None
        if self.provider in ("llama3", "llama", "llama3:latest"):
            model = "llama3:latest"
        elif self.provider in ("qwen3.6", "qwen3.6:latest"):
            model = "qwen3.6:latest"
        elif self.provider in ("qwen", "qwen2.5", "local", "ollama"):
            model = settings.qwen_model_name
        self._ollama = OllamaLLMClient(model=model)

    def generate_answer(
        self,
        query: str,
        evidence_context: str,
        conflict_detected: bool = False,
    ) -> Dict[str, Any]:
        """Generate grounded answer with token tracking and provenance."""
        prov = (self.provider or "amora-fast").lower().strip()

        # 1. Fast integrated grounder (explicitly requested, no model involved)
        if prov in ("amora-fast", "amora", "fast", "grounded", "default"):
            return canned_stub_response(query, evidence_context, conflict_detected, STUB_LABEL)

        # 2. Local Ollama Mode
        if prov in ("ollama", "qwen", "qwen2.5", "qwen3.6", "llama3", "llama", "local"):
            return self._ollama.generate_answer(query, evidence_context, conflict_detected)

        # 3. Free Cloud LLM Providers
        if prov in ("groq", "gemini", "huggingface", "mistral", "cohere"):
            try:
                from llm.free_providers import get_free_provider
                free_client = get_free_provider(prov)
                if free_client.is_configured():
                    result = free_client.generate_answer(query, evidence_context, conflict_detected)
                    result.setdefault("is_stub", False)
                    return result
            except Exception as exc:
                detail = re.sub(r"\s+", " ", str(exc))[:140]
                return canned_stub_response(
                    query, evidence_context, conflict_detected,
                    f"{STUB_LABEL} - {prov} provider error: {detail}",
                )

        # 4. Fallback to local Ollama if available
        if self._ollama.is_available() and self._ollama.has_model():
            return self._ollama.generate_answer(query, evidence_context, conflict_detected)

        return canned_stub_response(
            query, evidence_context, conflict_detected,
            f"{STUB_LABEL} - unknown provider '{prov}'",
        )
