# AMORA – Adaptive Multi-Objective Reasoning Algorithm for Heterogeneous External Source Routing and Tool Coordination in LLM-based Retrieval

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Flutter](https://img.shields.io/badge/UI-Flutter-02569B-blue.svg)](https://flutter.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Executive Overview

**AMORA** is a research-grade Retrieval-Augmented Generation (RAG) system extending the **INKER** adaptive retrieval framework. While INKER decides **WHEN** retrieval is required (IE-KRT) and **WHAT** to retrieve (IE-KQF), **AMORA** provides adaptive multi-objective source routing (**WHERE** to retrieve) and tool coordination (**WHICH TOOL** to use) across large, heterogeneous enterprise environments (SQL databases, REST APIs, PDF repositories, FAISS vector stores, and Web search).

```
USER QUERY
    |
    v
INKER IE-KRT ──(Retrieval NOT required)──> QWEN LLM ──> FINAL ANSWER
    |
(Retrieval required)
    |
    v
INKER IE-KQF ──(Query q+)──> AMORA SOURCE ROUTER
                                   |
                         Scalable Pre-filtering (10,000 -> 200)
                                   |
                         Dynamic Source Profiling (R_i, L_i, F_i, C_i, H_i, K_i)
                                   |
                         Dynamic Weight Generation (sum W = 1.0)
                                   |
                         Multi-Objective Ranking / Pareto Optimization
                                   |
                         Top-K Sources & Source-Tool Coordination
                                   |
               +----------+--------+--------+----------+
               |          |        |        |          |
              SQL        API    Vector     PDF        Web
               |          |        |        |          |
               +----------+--------+--------+----------+
                                   |
                           Retrieved Evidence
                                   |
                            Evidence Fusion
                                   |
                              Qwen LLM
                                   |
                             FINAL ANSWER
```

---

## 🧮 Theoretical & Mathematical Framework

### 1. INKER Knowledge Retrieval Trigger (IE-KRT)
Determines when external retrieval is required using the conceptual activation score:
$$K(t_i) = (E - m_i) \cdot S_i$$
- $E \in [0, 1]$: Query structural and semantic complexity.
- $m_i \in [0, 1]$: Parametric model token confidence (Mode A via logits, Mode B via uncertainty heuristic).
- $S_i \in [0, 1]$: External knowledge contribution requirement.

### 2. INKER Knowledge Query Formulator (IE-KQF)
Formulates the expanded retrieval query:
$$q^+ = \text{concat}(P, I)$$
where $P$ represents reasoning context phrases and $I$ denotes key query entities.

### 3. AMORA Dynamic Source Profiling Metrics
For candidate source $i$:
- **Relevance ($R_i$)**: Cosine similarity $R_i = \text{cosine\_similarity}(q^+, s_i) \in [0, 1]$.
- **Reliability ($L_i$)**: Weighted baseline reliability $L_i = \alpha \cdot \text{success\_rate}_i + \beta \cdot \text{availability}_i$ with $\alpha + \beta = 1.0$.
- **Freshness ($F_i$)**: Exponential time decay $F_i = \exp(-\lambda \Delta t)$ where $\Delta t$ is source age in hours.
- **Cost ($C_i$)**: Normalized retrieval cost penalty $C_i \in [0, 1]$.
- **Historical Success ($H_i$)**: Bayesian smoothed historical success rate $H_i = \frac{\text{successes} + \alpha}{\text{attempts} + \alpha + \beta}$.
- **Conflict Penalty ($K_i$)**: Normalized disagreement penalty score $K_i \in [0, 1]$.

### 4. Query-Aware Dynamic Weight Generation
Weights are dynamically adjusted per query based on features ($q_{\text{complexity}}, q_{\text{freshness\_need}}, q_{\text{cost\_sensitivity}}, q_{\text{reliability\_need}}, q_{\text{conflict\_sensitivity}}$) subject to strict normalization:
$$W_r + W_l + W_f + W_c + W_h + W_k = 1.0$$

### 5. AMORA Score & Multi-Objective Ranking
Single-objective composite score:
$$\text{Score}_i = W_r R_i + W_l L_i + W_f F_i + W_h H_i - W_c C_i - W_k K_i$$
*Pareto Non-Dominated Sorting Mode* is also supported to identify non-dominated source frontiers across trade-offs.

---

## ⚡ Quick Start & Installation

### 1. Local Environment Setup
```bash
# Clone or navigate to directory
cd amof

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment settings
cp .env.example .env
```

> **Embeddings.** Source pre-filtering uses the `EMBEDDING_MODEL` sentence-transformer
> (`BAAI/bge-small-en-v1.5`, 384-dim) via FAISS inner-product on normalized vectors.
> Control the backend with `EMBEDDING_BACKEND`:
> - `auto` (default) — use the model, fall back to a deterministic hash encoder if it cannot load
> - `model` — require the model; fail loudly rather than degrade
> - `hash` — always use the hash encoder (lexical overlap only, no semantic similarity)
>
> Every stored vector records the encoder that produced it. Changing `EMBEDDING_MODEL`
> invalidates stored vectors, which are re-embedded on the next run rather than being
> silently mixed into the same index.

---

## 🧠 Local LLM (Ollama / Qwen 3.6)

AMORA answers questions with a **real local model** through the Ollama daemon. Nothing is
fabricated: if the model is unavailable, the API says so explicitly instead of inventing an
answer.

```bash
ollama serve
ollama pull qwen3.6:latest

# Confirm the model is reachable and actually pulled
curl http://localhost:8000/llm/status
```

```json
{
  "model": "qwen3.6:latest",
  "ollama_reachable": true,
  "model_present": true,
  "ready": true,
  "timeout_seconds": 300,
  "num_predict": 4096,
  "think_enabled": false
}
```

### Generation limits that matter

Two settings cause silent, misleading failures if left at their old values:

| Setting | Default | Why it matters |
|---|---|---|
| `OLLAMA_TIMEOUT_SECONDS` | `300` | `qwen3.6:latest` (~24 GB) needs **100–150 s** for a RAG answer on CPU. A short timeout makes the client abandon the model mid-generation. |
| `OLLAMA_NUM_PREDICT` | `4096` | A **cap, not a target**. Reasoning models emit a chain of thought before the answer; a cap of 1024 truncates mid-reasoning and no answer is ever produced. |
| `OLLAMA_THINK` | `false` | With thinking disabled, Ollama returns the answer in `content` and the reasoning in `thinking`. AMORA reads `content`. |

### Answer provenance

Every query response reports which engine actually produced the text:

| Field | Meaning |
|---|---|
| `provider_used` | Engine name, e.g. `Ollama/qwen3.6:latest`. |
| `used_stub_response` | `true` when **no generative model ran** and the text came from a fixed template. |
| `llm_note` | Why a model was skipped, or that generation was truncated. |

When `used_stub_response` is `true`, `accuracy_score` is forced to `0.0` and the UI shows a
warning. A canned template emits `[Source: ...]` markers, so without this rule a
pre-written answer would score 100% on citation coverage.

### Streaming

`qwen3.6` can take minutes. `POST /query/stream` returns Server-Sent Events so tokens
render as they arrive:

| Event | Payload |
|---|---|
| `retrieval` | Routed sources, DST beliefs, and fused evidence — sent **before** generation starts. |
| `delta` | Incremental answer text (repeated). |
| `done` | Final metrics, including `provider_used` and `used_stub_response`. |
| `error` | Generation failure. |

---

## ⚠️ Reading the Reported Metrics

Not every number this system returns is an empirical measurement. Being explicit about which
is which:

| Metric | What it actually is |
|---|---|
| `accuracy_score` (query responses) | A **grounding proxy**, not ground truth. Computed from citation coverage, routed-source quality, and evidence yield. A response that ignores its own evidence scores poorly. Forced to `0.0` when `used_stub_response` is true, because a template is not a model output. |
| `grounded_claim_ratio` (`/compare`) | Fraction of *assertive, non-hedged* sentences carrying a source citation. A structural property of the answer. |
| `amora_hallucination_risk` (`/compare`) | The same structural measure, phrased as a label. **Not** a hallucination rate. |
| nDCG, precision@k, hit-rate | **Genuinely measured** against gold labels — `POST /evaluation/run`. |

Empirical hallucination rates require a labelled evaluation set. Use the benchmark
endpoint rather than quoting the structural figures as accuracy.

### 2. Initialize Database & Seed Demo Data
```bash
python -m datasets.demo_data
```

### 3. Run FastAPI Backend
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
- API Documentation available at: `http://localhost:8000/docs`

### 4. Run the Flutter UI

The UI is Flutter — there is no Python UI layer.

```bash
# Comprehensive app (chat, compare, benchmark, sources, free-AI chat)
cd frontend/flutter_app
flutter pub get
flutter run -d chrome          # or: -d windows, -d android, -d <device-id>

# Chat-focused client (pipeline drawer, sidebar, direct Ollama access)
cd amora_chat
flutter pub get
flutter run
```

To use the app from a browser without a separate web server, build it for web and let
FastAPI serve the bundle at `/app`:

```powershell
# Windows — see the note below on why this is a script
powershell -ExecutionPolicy Bypass -File tools\build_flutter_web.ps1
```

Then start the backend and open **http://localhost:8000/app**.

> **If `flutter build web` fails with `'C:\Users\...' is not recognized`:** Flutter 3.38
> runs a native-assets hook for `objective_c` (an Apple-only transitive dep via
> `path_provider_foundation`) even for web builds, and that hook shells out with unquoted
> paths. Any space in the project path *or* the pub cache path breaks it. `tools/build_flutter_web.ps1`
> stages the build in a space-free directory with a space-free `PUB_CACHE`, then copies the
> finished bundle back into `frontend/flutter_app/build/web`. Use it instead of calling
> `flutter build web` directly.

If no web build is present, `/app` returns a 503 page with these instructions rather than
failing silently. Set `FLUTTER_WEB_DIR` to serve a bundle from a different location.

> **Pointing the app at your backend.** Both Flutter clients default to
> `http://localhost:8000`. On the Android emulator `localhost` is the device itself, not
> your machine — change `ApiService.baseUrl` (`frontend/flutter_app/lib/services/api_service.dart`,
> `amora_chat/lib/services/amora_service.dart`) to `http://10.0.2.2:8000`, or to your host's
> LAN IP for a physical device.

---

## 🐳 Docker Deployment

The backend image builds the Flutter web bundle in a first stage and serves it at `/app`,
so a single container hosts both API and UI:

```bash
docker-compose up --build
```

---

## 🧪 Testing & Verification

Run the full pytest test suite:
```bash
pytest tests/ -v
```

---

## 📊 Generating 10,000-Source Synthetic Catalog
```bash
python -m datasets.generate_synthetic_catalog
```

---

## 🏷️ Code Component Attribution Tags

All major Python source code files contain explicit headers identifying component lineage:
- `[A. Existing/Reused Functionality]` Infrastructure, FastAPI server, Pydantic schemas, database engines.
- `[B. INKER-Inspired Functionality]` IE-KRT activation formulas and IE-KQF query expansion.
- `[C. AMORA Proposed Functionality]` Scalable vector pre-filtering, dynamic source profiling, query-aware dynamic weight generation, multi-objective ranking, source-tool coordination, evidence fusion, and conflict detection.

---

## 📄 License
MIT License. Developed for research in LLM Retrieval-Augmented Generation.
