# Agent Scratchpad Synthesizer

> **Domain:** Autonomous Agent Systems & Context State Architecture  
> **Reference Guidelines & Standards:** `Distributed Systems RFC & State Machine Verification`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Agent Scratchpad Synthesizer** is an advanced analytical and computational platform implementing Isolated scratchpad working memory for intermediate mathematical/clinical derivations.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`EntryType`** — dedicated module for entry type evaluation and state verification.
- **`ScratchpadEntry`** — dedicated module for scratchpad entry evaluation and state verification.
- **`ScratchpadBranch`** — dedicated module for scratchpad branch evaluation and state verification.
- **`SynthesisResult`** — dedicated module for synthesis result evaluation and state verification.
- **`WorkingMemory`**: Manages scratchpad entries with priority-based eviction and max entry limits.
- **`ContextCompressor`**: Compresses old scratchpad entries via summarization.

---

## 📐 Mathematical Formulation & Logic

```text
  score = similarity * 0.7 + entry.priority * 0.3
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --type <value> --content <value> --priority <value> --max-entries <value>
```

### Parameter Reference
- `--type`: Specifies input measurement or parameter value.
- `--content`: Specifies input measurement or parameter value.
- `--priority`: Specifies input measurement or parameter value.
- `--max-entries`: Specifies input measurement or parameter value.
- `--query`: Specifies input measurement or parameter value.
- `--top-k`: Specifies input measurement or parameter value.
- `--strategy`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Parameter / observation metric | Required |
| `target_identifier` | Parameter / observation metric | Required |
| `primary_metric` | Parameter / observation metric | Required |
| `secondary_metric` | Parameter / observation metric | Required |
| `is_critical_flag` | Parameter / observation metric | Required |
| `status_descriptor` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t agent-scratchpad-synthesizer .
docker run -p 8000:8000 agent-scratchpad-synthesizer
```
