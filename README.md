# Agent Scratchpad Synthesizer

A pure Python production-grade structured working memory and chain-of-thought derivation engine implementing:
- Isolated scratchpad working memory with priority-based eviction and bounded retention.
- Multi-branch thought exploration (branching, hypothesis evaluation, and path merging).
- Semantic context compression (summarizing intermediate derivations to prevent context window bloat).
- Priority-weighted relevance retrieval combining Jaccard term similarity with derivation priority:
  $$\text{Score} = 0.7 \times \text{Similarity}(\text{query}, \text{entry}) + 0.3 \times \text{Priority}$$
- Structured thought synthesis across derivation branches into actionable consensus findings.
- Supervisory multi-agent telemetry auditing across analytical reasoning workflows.

Requires Python standard library only (zero external runtime dependencies).

---

## Features

- **Priority Working Memory:** Manages categorized scratchpad entries (`thought`, `observation`, `derivation`, `hypothesis`, `verification`, `synthesis`) with bounded memory limits.
- **Context Compression:** Periodically compresses long scratchpad records into concise derivation summaries while preserving high-priority conclusions.
- **Branching Exploration:** Supports tree-like exploration of alternative reasoning paths without corrupting main derivation state.
- **Relevance Retrieval:** Fast in-memory similarity lookup identifying earlier related observations and equations.
- **Batch CSV Processing:** High-throughput validation and telemetry auditing for derivation tasks.

---

## Installation & Requirements

- Python 3.10+ (tested on 3.10, 3.11, 3.12)
- Zero external runtime dependencies. `pytest` is optional for running tests.

```bash
git clone https://github.com/abusuraihsakhri/agent-scratchpad-synthesizer.git
cd agent-scratchpad-synthesizer
```

---

## CLI Usage

### 1. Add Entry to Scratchpad
```bash
python cli.py add --type derivation --content "E = mc^2 verified under standard relativistic conditions" --priority 0.8
```

### 2. Query Scratchpad Derivations
```bash
python cli.py query --query "relativistic" --top-k 3
```

### 3. Synthesize Working Memory
Synthesize entries across the active scratchpad:
```bash
python cli.py synthesize --strategy consensus
```

### 4. Inspect Scratchpad Status
```bash
python cli.py status
```

### 5. Multi-Agent Supervisory Audit
Run supervisory audit with JSON output:
```bash
python scratchpad_mind_app.py audit --task-id TASK-2026-001 --primary 29.4 --secondary 15.1 --json
```

### 6. Batch CSV Processing
Batch process records and generate synthesis reports:
```bash
python scratchpad_mind_app.py batch -i sample.csv -o results.csv
```

---

## Python API Quickstart

```python
from scratchpad_engine import (
    ScratchpadSynthesizer,
    EntryType,
)

# 1. Initialize Synthesizer
synth = ScratchpadSynthesizer(max_entries=50, compress_after=10)

# 2. Add thoughts and derivations
synth.add_thought("Investigating initial clinical symptoms.", priority=0.6)
synth.add_thought("Lab results indicate elevated lipase levels.", entry_type=EntryType.OBSERVATION, priority=0.8)

# 3. Explore alternative branch
branch = synth.create_branch("DifferentialDiagnosis")
synth.add_thought("Consider acute pancreatitis vs cholecystitis.", branch=branch.id, priority=0.9)

# 4. Synthesize conclusions
result = synth.synthesize(branch=branch.id)
print(f"Synthesized {result.entry_count} entries into summary: {result.summary}")
```

---

## Running Tests

Run the test suite using standard `unittest` or `pytest`:

```bash
pytest -v
```

