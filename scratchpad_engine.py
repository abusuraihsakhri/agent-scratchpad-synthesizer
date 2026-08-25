#!/usr/bin/env python3
"""
Agent Scratchpad Synthesizer: Structured scratchpad with thought/action/observation/reflection,
chain-of-thought synthesis, working memory management, context compression, retrieval,
serialization, branching, and merge.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import time
import math
import json
import uuid
import copy


class EntryType(str, Enum):
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    REFLECTION = "reflection"


@dataclass
class ScratchpadEntry:
    id: str
    type: EntryType
    content: str
    timestamp: float = field(default_factory=time.time)
    priority: float = 0.5  # 0.0 to 1.0
    metadata: Dict = field(default_factory=dict)
    branch_id: str = "main"

    def similarity(self, other: "ScratchpadEntry") -> float:
        """Simple word-overlap similarity score."""
        words_self = set(self.content.lower().split())
        words_other = set(other.content.lower().split())
        if not words_self or not words_other:
            return 0.0
        intersection = words_self & words_other
        union = words_self | words_other
        return len(intersection) / len(union) if union else 0.0


@dataclass
class ScratchpadBranch:
    id: str
    name: str
    parent_branch: Optional[str] = None
    entries: List[ScratchpadEntry] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)


@dataclass
class SynthesisResult:
    summary: str
    key_insights: List[str]
    chain_of_thought: List[Dict]
    confidence: float
    entry_count: int
    branch_count: int


class WorkingMemory:
    """Manages scratchpad entries with priority-based eviction and max entry limits."""

    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self.entries: List[ScratchpadEntry] = []

    def add(self, entry: ScratchpadEntry) -> ScratchpadEntry:
        """Add an entry, evicting lowest-priority if at capacity."""
        if len(self.entries) >= self.max_entries:
            self._evict()
        self.entries.append(entry)
        return entry

    def _evict(self):
        """Evict the lowest-priority entry."""
        if not self.entries:
            return
        # Sort by priority (ascending) and remove the lowest
        self.entries.sort(key=lambda e: e.priority)
        self.entries.pop(0)

    def get_by_type(self, entry_type: EntryType) -> List[ScratchpadEntry]:
        return [e for e in self.entries if e.type == entry_type]

    def get_recent(self, n: int = 10) -> List[ScratchpadEntry]:
        return sorted(self.entries, key=lambda e: e.timestamp, reverse=True)[:n]

    def get_by_id(self, entry_id: str) -> Optional[ScratchpadEntry]:
        for e in self.entries:
            if e.id == entry_id:
                return e
        return None

    def remove(self, entry_id: str) -> bool:
        before = len(self.entries)
        self.entries = [e for e in self.entries if e.id != entry_id]
        return len(self.entries) < before

    def clear(self):
        self.entries.clear()

    @property
    def count(self) -> int:
        return len(self.entries)

    def summary(self) -> Dict[str, int]:
        counts = {t.value: 0 for t in EntryType}
        for e in self.entries:
            counts[e.type.value] += 1
        return counts


class ContextCompressor:
    """Compresses old scratchpad entries via summarization."""

    def __init__(self, keep_recent: int = 10):
        self.keep_recent = keep_recent

    def compress(self, entries: List[ScratchpadEntry]) -> Tuple[List[ScratchpadEntry], str]:
        """Compress entries: keep recent, summarize older ones."""
        if len(entries) <= self.keep_recent:
            return entries, ""

        sorted_entries = sorted(entries, key=lambda e: e.timestamp)
        old_entries = sorted_entries[:-self.keep_recent]
        recent_entries = sorted_entries[-self.keep_recent:]

        summary = self._summarize(old_entries)
        return recent_entries, summary

    def _summarize(self, entries: List[ScratchpadEntry]) -> str:
        """Create a text summary of entries."""
        if not entries:
            return ""

        type_counts = {}
        key_phrases = []
        for e in entries:
            type_counts[e.type.value] = type_counts.get(e.type.value, 0) + 1
            # Extract first sentence as key phrase
            first_sentence = e.content.split('.')[0].strip()
            if first_sentence and len(first_sentence) < 100:
                key_phrases.append(f"[{e.type.value}] {first_sentence}")

        summary_parts = [f"Compressed {len(entries)} entries:"]
        for t, count in type_counts.items():
            summary_parts.append(f"  - {t}: {count}")
        summary_parts.append("Key points:")
        for phrase in key_phrases[:5]:
            summary_parts.append(f"  - {phrase}")

        return "\n".join(summary_parts)


class ScratchpadRetriever:
    """Retrieves relevant scratchpad entries by similarity."""

    def __init__(self):
        pass

    def find_similar(self, query: str, entries: List[ScratchpadEntry],
                     top_k: int = 5) -> List[Tuple[ScratchpadEntry, float]]:
        """Find entries most similar to the query."""
        query_words = set(query.lower().split())
        if not query_words:
            return []

        scored = []
        for entry in entries:
            entry_words = set(entry.content.lower().split())
            if not entry_words:
                continue
            intersection = query_words & entry_words
            union = query_words | entry_words
            similarity = len(intersection) / len(union) if union else 0.0
            # Boost by priority
            score = similarity * 0.7 + entry.priority * 0.3
            scored.append((entry, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def find_by_type_and_keywords(self, entry_type: EntryType,
                                   keywords: List[str],
                                   entries: List[ScratchpadEntry]) -> List[ScratchpadEntry]:
        """Find entries matching type and containing any keyword."""
        results = []
        for entry in entries:
            if entry.type != entry_type:
                continue
            content_lower = entry.content.lower()
            if any(kw.lower() in content_lower for kw in keywords):
                results.append(entry)
        return results


class ChainOfThoughtSynthesizer:
    """Synthesizes chain-of-thought reasoning from scratchpad entries."""

    def synthesize(self, entries: List[ScratchpadEntry]) -> List[Dict]:
        """Build a chain-of-thought from entries in chronological order."""
        sorted_entries = sorted(entries, key=lambda e: e.timestamp)
        chain = []
        for i, entry in enumerate(sorted_entries):
            chain.append({
                "step": i + 1,
                "type": entry.type.value,
                "content": entry.content,
                "priority": entry.priority,
            })
        return chain

    def extract_insights(self, entries: List[ScratchpadEntry]) -> List[str]:
        """Extract key insights from reflection and observation entries."""
        insights = []
        for entry in entries:
            if entry.type in (EntryType.REFLECTION, EntryType.OBSERVATION):
                if entry.priority >= 0.6:
                    insights.append(entry.content[:200])
        return insights[:10]


class BranchManager:
    """Manages alternative reasoning branches."""

    def __init__(self):
        self.branches: Dict[str, ScratchpadBranch] = {}
        # Create main branch
        self.branches["main"] = ScratchpadBranch(id="main", name="Main reasoning path")

    def create_branch(self, name: str, parent_branch: str = "main",
                      copy_entries: bool = True) -> ScratchpadBranch:
        """Create a new branch, optionally copying entries from parent."""
        branch_id = f"branch_{uuid.uuid4().hex[:8]}"
        parent = self.branches.get(parent_branch)

        entries = []
        if copy_entries and parent:
            entries = [copy.deepcopy(e) for e in parent.entries]
            for e in entries:
                e.branch_id = branch_id

        branch = ScratchpadBranch(
            id=branch_id,
            name=name,
            parent_branch=parent_branch,
            entries=entries,
        )
        self.branches[branch_id] = branch
        return branch

    def add_to_branch(self, branch_id: str, entry: ScratchpadEntry):
        """Add an entry to a specific branch."""
        if branch_id not in self.branches:
            raise ValueError(f"Branch '{branch_id}' not found")
        entry.branch_id = branch_id
        self.branches[branch_id].entries.append(entry)

    def get_branch(self, branch_id: str) -> Optional[ScratchpadBranch]:
        return self.branches.get(branch_id)

    def merge_branches(self, source_id: str, target_id: str,
                       strategy: str = "append") -> ScratchpadBranch:
        """Merge source branch into target branch."""
        source = self.branches.get(source_id)
        target = self.branches.get(target_id)

        if not source:
            raise ValueError(f"Source branch '{source_id}' not found")
        if not target:
            raise ValueError(f"Target branch '{target_id}' not found")

        if strategy == "append":
            for entry in source.entries:
                merged_entry = copy.deepcopy(entry)
                merged_entry.branch_id = target_id
                merged_entry.id = f"merged_{uuid.uuid4().hex[:8]}"
                target.entries.append(merged_entry)
        elif strategy == "interleave":
            # Interleave entries by timestamp
            all_entries = target.entries + [copy.deepcopy(e) for e in source.entries]
            all_entries.sort(key=lambda e: e.timestamp)
            for e in all_entries:
                e.branch_id = target_id
            target.entries = all_entries
        elif strategy == "priority":
            # Keep highest priority entries when overlapping
            seen_content = {e.content for e in target.entries}
            for entry in source.entries:
                if entry.content not in seen_content:
                    merged_entry = copy.deepcopy(entry)
                    merged_entry.branch_id = target_id
                    target.entries.append(merged_entry)

        return target

    def list_branches(self) -> List[Dict]:
        return [
            {
                "id": b.id,
                "name": b.name,
                "parent": b.parent_branch,
                "entry_count": len(b.entries),
                "created_at": b.created_at,
            }
            for b in self.branches.values()
        ]


class ScratchpadSynthesizer:
    """Main synthesizer combining all scratchpad functionality."""

    def __init__(self, max_entries: int = 100, compress_after: int = 50):
        self.memory = WorkingMemory(max_entries)
        self.compressor = ContextCompressor(keep_recent=max(10, max_entries // 5))
        self.retriever = ScratchpadRetriever()
        self.chain_builder = ChainOfThoughtSynthesizer()
        self.branch_manager = BranchManager()
        self.compress_after = compress_after
        self._compressed_summary = ""

    def add_thought(self, content: str, priority: float = 0.5,
                    metadata: Optional[Dict] = None,
                    branch: str = "main") -> ScratchpadEntry:
        """Add a thought entry."""
        entry = ScratchpadEntry(
            id=f"thought_{uuid.uuid4().hex[:8]}",
            type=EntryType.THOUGHT,
            content=content,
            priority=priority,
            metadata=metadata or {},
            branch_id=branch,
        )
        self._add_entry(entry, branch)
        return entry

    def add_action(self, content: str, priority: float = 0.5,
                   metadata: Optional[Dict] = None,
                   branch: str = "main") -> ScratchpadEntry:
        """Add an action entry."""
        entry = ScratchpadEntry(
            id=f"action_{uuid.uuid4().hex[:8]}",
            type=EntryType.ACTION,
            content=content,
            priority=priority,
            metadata=metadata or {},
            branch_id=branch,
        )
        self._add_entry(entry, branch)
        return entry

    def add_observation(self, content: str, priority: float = 0.5,
                        metadata: Optional[Dict] = None,
                        branch: str = "main") -> ScratchpadEntry:
        """Add an observation entry."""
        entry = ScratchpadEntry(
            id=f"obs_{uuid.uuid4().hex[:8]}",
            type=EntryType.OBSERVATION,
            content=content,
            priority=priority,
            metadata=metadata or {},
            branch_id=branch,
        )
        self._add_entry(entry, branch)
        return entry

    def add_reflection(self, content: str, priority: float = 0.5,
                       metadata: Optional[Dict] = None,
                       branch: str = "main") -> ScratchpadEntry:
        """Add a reflection entry."""
        entry = ScratchpadEntry(
            id=f"refl_{uuid.uuid4().hex[:8]}",
            type=EntryType.REFLECTION,
            content=content,
            priority=priority,
            metadata=metadata or {},
            branch_id=branch,
        )
        self._add_entry(entry, branch)
        return entry

    def _add_entry(self, entry: ScratchpadEntry, branch: str):
        self.memory.add(entry)
        self.branch_manager.add_to_branch(branch, entry)
        # Auto-compress if needed
        if self.memory.count > self.compress_after:
            self.compress()

    def compress(self):
        """Compress old entries to free memory."""
        entries, summary = self.compressor.compress(self.memory.entries)
        if summary:
            self._compressed_summary = summary
            self.memory.clear()
            for e in entries:
                self.memory.entries.append(e)

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[ScratchpadEntry, float]]:
        """Retrieve relevant entries by similarity."""
        return self.retriever.find_similar(query, self.memory.entries, top_k)

    def synthesize(self, branch: str = "main") -> SynthesisResult:
        """Synthesize all scratchpad content into a coherent result."""
        branch_obj = self.branch_manager.get_branch(branch)
        entries = branch_obj.entries if branch_obj else self.memory.entries

        chain = self.chain_builder.synthesize(entries)
        insights = self.chain_builder.extract_insights(entries)

        # Compute confidence based on entry types and priorities
        if entries:
            avg_priority = sum(e.priority for e in entries) / len(entries)
            has_reflections = any(e.type == EntryType.REFLECTION for e in entries)
            has_observations = any(e.type == EntryType.OBSERVATION for e in entries)
            confidence = avg_priority * 0.5
            if has_reflections:
                confidence += 0.2
            if has_observations:
                confidence += 0.2
            confidence = min(1.0, confidence)
        else:
            confidence = 0.0

        summary_parts = []
        if self._compressed_summary:
            summary_parts.append(self._compressed_summary)
        summary_parts.append(f"Branch '{branch}' contains {len(entries)} entries")
        summary_parts.append(f"Key insights: {len(insights)}")

        return SynthesisResult(
            summary="\n".join(summary_parts),
            key_insights=insights,
            chain_of_thought=chain,
            confidence=round(confidence, 3),
            entry_count=len(entries),
            branch_count=len(self.branch_manager.branches),
        )

    def create_branch(self, name: str, parent: str = "main",
                      copy_entries: bool = True) -> ScratchpadBranch:
        """Create an alternative reasoning branch."""
        return self.branch_manager.create_branch(name, parent, copy_entries)

    def merge_branch(self, source: str, target: str = "main",
                     strategy: str = "append") -> ScratchpadBranch:
        """Merge a branch back into target."""
        return self.branch_manager.merge_branches(source, target, strategy)

    def serialize(self) -> str:
        """Serialize scratchpad state to JSON."""
        data = {
            "compressed_summary": self._compressed_summary,
            "entries": [
                {
                    "id": e.id,
                    "type": e.type.value,
                    "content": e.content,
                    "timestamp": e.timestamp,
                    "priority": e.priority,
                    "metadata": e.metadata,
                    "branch_id": e.branch_id,
                }
                for e in self.memory.entries
            ],
            "branches": self.branch_manager.list_branches(),
        }
        return json.dumps(data, indent=2)

    @classmethod
    def deserialize(cls, data: str, max_entries: int = 100) -> "ScratchpadSynthesizer":
        """Deserialize scratchpad state from JSON."""
        parsed = json.loads(data)
        synth = cls(max_entries=max_entries)
        synth._compressed_summary = parsed.get("compressed_summary", "")

        for e_data in parsed.get("entries", []):
            entry = ScratchpadEntry(
                id=e_data["id"],
                type=EntryType(e_data["type"]),
                content=e_data["content"],
                timestamp=e_data.get("timestamp", time.time()),
                priority=e_data.get("priority", 0.5),
                metadata=e_data.get("metadata", {}),
                branch_id=e_data.get("branch_id", "main"),
            )
            synth.memory.add(entry)

        return synth

    def get_status(self) -> Dict:
        return {
            "memory_count": self.memory.count,
            "memory_summary": self.memory.summary(),
            "branch_count": len(self.branch_manager.branches),
            "compressed_summary": bool(self._compressed_summary),
        }
