# Agent Scratchpad Synthesizer

A structured scratchpad system for agent reasoning with chain-of-thought synthesis, working memory management, context compression, similarity-based retrieval, serialization, and branching/merging of reasoning paths.

## Features

- **Structured scratchpad format**: thought, action, observation, reflection entries
- **Chain-of-thought synthesis**: builds reasoning chains from entries
- **Working memory management**: max entries with priority-based eviction
- **Context compression**: summarization of old entries to free memory
- **Retrieval**: find relevant scratchpad entries by word-overlap similarity
- **State serialization/deserialization**: save/restore scratchpad state as JSON
- **Branching**: create alternative reasoning paths from any point
- **Merge**: combine insights from multiple branches (append, interleave, priority)

## Quick Start

```bash
# Add entries
python cli.py add --type thought --content "Need to analyze the data" --priority 0.7
python cli.py add --type action --content "Loaded dataset" --priority 0.6
python cli.py add --type observation --content "Found outliers" --priority 0.8
python cli.py add --type reflection --content "Outliers suggest data quality issues" --priority 0.9

# Synthesize
python cli.py synthesize

# Retrieve similar entries
python cli.py retrieve --query "data quality" --top-k 3

# Branch and merge
python cli.py branch --strategy append

# Serialize/deserialize
python cli.py serialize
```

## Python API

```python
from scratchpad_engine import ScratchpadSynthesizer

synth = ScratchpadSynthesizer(max_entries=100)

# Add structured entries
synth.add_thought("Analyze user behavior patterns", priority=0.7)
synth.add_action("Queried database for user sessions", priority=0.6)
synth.add_observation("Peak usage at 2-4 PM", priority=0.8)
synth.add_reflection("Should scale resources for peak hours", priority=0.9)

# Retrieve relevant entries
results = synth.retrieve("user patterns", top_k=3)

# Create alternative reasoning branch
branch = synth.create_branch("Alternative analysis")
synth.add_thought("Try clustering approach", priority=0.7, branch=branch.id)

# Merge back
synth.merge_branch(branch.id, "main", strategy="append")

# Synthesize
result = synth.synthesize()
print(result.summary, result.confidence, result.key_insights)

# Serialize
json_str = synth.serialize()
restored = ScratchpadSynthesizer.deserialize(json_str)
```

## Architecture

```
ScratchpadSynthesizer
├── WorkingMemory          # Max entries, priority-based eviction
├── ContextCompressor      # Summarize old entries
├── ScratchpadRetriever    # Similarity-based retrieval
├── ChainOfThoughtSynthesizer  # Build reasoning chains
└── BranchManager          # Create/merge alternative paths
```

## License

MIT
