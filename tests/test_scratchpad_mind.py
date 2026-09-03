#!/usr/bin/env python3
"""Tests for Scratchpad Synthesizer."""
import sys
import os
import unittest
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scratchpad_engine import (
    ScratchpadSynthesizer, ScratchpadEntry, EntryType,
    WorkingMemory, ContextCompressor, ScratchpadRetriever,
    ChainOfThoughtSynthesizer, BranchManager, ScratchpadBranch,
)


class TestScratchpadEntry(unittest.TestCase):
    def test_create_entry(self):
        entry = ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="test thought")
        self.assertEqual(entry.id, "e1")
        self.assertEqual(entry.type, EntryType.THOUGHT)
        self.assertEqual(entry.priority, 0.5)

    def test_similarity(self):
        e1 = ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="the cat sat on the mat")
        e2 = ScratchpadEntry(id="e2", type=EntryType.THOUGHT, content="the dog sat on the rug")
        sim = e1.similarity(e2)
        self.assertGreater(sim, 0.3)
        self.assertLess(sim, 1.0)

    def test_similarity_no_overlap(self):
        e1 = ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="apple banana cherry")
        e2 = ScratchpadEntry(id="e2", type=EntryType.THOUGHT, content="dog elephant fox")
        sim = e1.similarity(e2)
        self.assertEqual(sim, 0.0)


class TestWorkingMemory(unittest.TestCase):
    def test_add_entry(self):
        mem = WorkingMemory(max_entries=10)
        entry = ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="test")
        mem.add(entry)
        self.assertEqual(mem.count, 1)

    def test_max_entries_eviction(self):
        mem = WorkingMemory(max_entries=3)
        for i in range(5):
            entry = ScratchpadEntry(id=f"e{i}", type=EntryType.THOUGHT,
                                    content=f"entry {i}", priority=i * 0.2)
            mem.add(entry)
        self.assertLessEqual(mem.count, 3)

    def test_eviction_keeps_highest_priority(self):
        mem = WorkingMemory(max_entries=2)
        mem.add(ScratchpadEntry(id="low", type=EntryType.THOUGHT, content="low", priority=0.1))
        mem.add(ScratchpadEntry(id="high", type=EntryType.THOUGHT, content="high", priority=0.9))
        mem.add(ScratchpadEntry(id="mid", type=EntryType.THOUGHT, content="mid", priority=0.5))
        ids = [e.id for e in mem.entries]
        self.assertIn("high", ids)
        self.assertIn("mid", ids)

    def test_get_by_type(self):
        mem = WorkingMemory()
        mem.add(ScratchpadEntry(id="t1", type=EntryType.THOUGHT, content="thought"))
        mem.add(ScratchpadEntry(id="a1", type=EntryType.ACTION, content="action"))
        thoughts = mem.get_by_type(EntryType.THOUGHT)
        self.assertEqual(len(thoughts), 1)

    def test_get_recent(self):
        mem = WorkingMemory()
        for i in range(5):
            mem.add(ScratchpadEntry(id=f"e{i}", type=EntryType.THOUGHT,
                                    content=f"entry {i}"))
        recent = mem.get_recent(3)
        self.assertEqual(len(recent), 3)

    def test_get_by_id(self):
        mem = WorkingMemory()
        mem.add(ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="test"))
        self.assertIsNotNone(mem.get_by_id("e1"))
        self.assertIsNone(mem.get_by_id("nonexistent"))

    def test_remove(self):
        mem = WorkingMemory()
        mem.add(ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="test"))
        self.assertTrue(mem.remove("e1"))
        self.assertEqual(mem.count, 0)

    def test_clear(self):
        mem = WorkingMemory()
        mem.add(ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="test"))
        mem.clear()
        self.assertEqual(mem.count, 0)

    def test_summary(self):
        mem = WorkingMemory()
        mem.add(ScratchpadEntry(id="t1", type=EntryType.THOUGHT, content="thought"))
        mem.add(ScratchpadEntry(id="a1", type=EntryType.ACTION, content="action"))
        summary = mem.summary()
        self.assertEqual(summary["thought"], 1)
        self.assertEqual(summary["action"], 1)


class TestContextCompressor(unittest.TestCase):
    def test_compress_under_limit(self):
        compressor = ContextCompressor(keep_recent=5)
        entries = [ScratchpadEntry(id=f"e{i}", type=EntryType.THOUGHT, content=f"entry {i}")
                   for i in range(3)]
        result, summary = compressor.compress(entries)
        self.assertEqual(len(result), 3)
        self.assertEqual(summary, "")

    def test_compress_over_limit(self):
        compressor = ContextCompressor(keep_recent=3)
        entries = [ScratchpadEntry(id=f"e{i}", type=EntryType.THOUGHT, content=f"entry {i}")
                   for i in range(10)]
        result, summary = compressor.compress(entries)
        self.assertEqual(len(result), 3)
        self.assertIn("Compressed", summary)

    def test_compress_preserves_recent(self):
        compressor = ContextCompressor(keep_recent=2)
        entries = [
            ScratchpadEntry(id="old", type=EntryType.THOUGHT, content="old entry"),
            ScratchpadEntry(id="new1", type=EntryType.THOUGHT, content="new entry 1"),
            ScratchpadEntry(id="new2", type=EntryType.THOUGHT, content="new entry 2"),
        ]
        result, _ = compressor.compress(entries)
        result_ids = [e.id for e in result]
        self.assertIn("new1", result_ids)
        self.assertIn("new2", result_ids)


class TestScratchpadRetriever(unittest.TestCase):
    def test_find_similar(self):
        retriever = ScratchpadRetriever()
        entries = [
            ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="machine learning model training"),
            ScratchpadEntry(id="e2", type=EntryType.THOUGHT, content="database query optimization"),
            ScratchpadEntry(id="e3", type=EntryType.OBSERVATION, content="machine learning accuracy improved"),
        ]
        results = retriever.find_similar("machine learning", entries, top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("machine learning", results[0][0].content)

    def test_find_similar_empty(self):
        retriever = ScratchpadRetriever()
        results = retriever.find_similar("test", [], top_k=5)
        self.assertEqual(len(results), 0)

    def test_find_by_type_and_keywords(self):
        retriever = ScratchpadRetriever()
        entries = [
            ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="analyze the data"),
            ScratchpadEntry(id="e2", type=EntryType.OBSERVATION, content="data shows patterns"),
            ScratchpadEntry(id="e3", type=EntryType.ACTION, content="loaded the data"),
        ]
        results = retriever.find_by_type_and_keywords(EntryType.OBSERVATION, ["data"], entries)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "e2")


class TestChainOfThoughtSynthesizer(unittest.TestCase):
    def test_synthesize_chain(self):
        cot = ChainOfThoughtSynthesizer()
        entries = [
            ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="First thought"),
            ScratchpadEntry(id="e2", type=EntryType.ACTION, content="Took action"),
            ScratchpadEntry(id="e3", type=EntryType.OBSERVATION, content="Observed result"),
        ]
        chain = cot.synthesize(entries)
        self.assertEqual(len(chain), 3)
        self.assertEqual(chain[0]["type"], "thought")
        self.assertEqual(chain[1]["type"], "action")

    def test_extract_insights(self):
        cot = ChainOfThoughtSynthesizer()
        entries = [
            ScratchpadEntry(id="e1", type=EntryType.REFLECTION, content="Key insight here", priority=0.8),
            ScratchpadEntry(id="e2", type=EntryType.OBSERVATION, content="Important observation", priority=0.7),
            ScratchpadEntry(id="e3", type=EntryType.THOUGHT, content="Low priority thought", priority=0.3),
        ]
        insights = cot.extract_insights(entries)
        self.assertGreater(len(insights), 0)


class TestBranchManager(unittest.TestCase):
    def test_create_branch(self):
        bm = BranchManager()
        branch = bm.create_branch("Alternative path")
        self.assertIn(branch.id, bm.branches)
        self.assertEqual(branch.name, "Alternative path")

    def test_create_branch_copies_entries(self):
        bm = BranchManager()
        entry = ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="test")
        bm.add_to_branch("main", entry)
        branch = bm.create_branch("Copy", parent_branch="main", copy_entries=True)
        self.assertEqual(len(branch.entries), 1)

    def test_add_to_branch(self):
        bm = BranchManager()
        branch = bm.create_branch("Test")
        entry = ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="test")
        bm.add_to_branch(branch.id, entry)
        self.assertEqual(len(branch.entries), 1)

    def test_add_to_nonexistent_branch(self):
        bm = BranchManager()
        entry = ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="test")
        with self.assertRaises(ValueError):
            bm.add_to_branch("nonexistent", entry)

    def test_merge_append(self):
        bm = BranchManager()
        bm.add_to_branch("main", ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="main entry"))
        branch = bm.create_branch("Alt", copy_entries=False)
        bm.add_to_branch(branch.id, ScratchpadEntry(id="e2", type=EntryType.THOUGHT, content="alt entry"))
        merged = bm.merge_branches(branch.id, "main", strategy="append")
        self.assertEqual(len(merged.entries), 2)

    def test_merge_priority(self):
        bm = BranchManager()
        bm.add_to_branch("main", ScratchpadEntry(id="e1", type=EntryType.THOUGHT, content="shared"))
        branch = bm.create_branch("Alt", copy_entries=False)
        bm.add_to_branch(branch.id, ScratchpadEntry(id="e2", type=EntryType.THOUGHT, content="unique"))
        merged = bm.merge_branches(branch.id, "main", strategy="priority")
        contents = [e.content for e in merged.entries]
        self.assertIn("unique", contents)

    def test_list_branches(self):
        bm = BranchManager()
        bm.create_branch("Branch 1")
        bm.create_branch("Branch 2")
        branches = bm.list_branches()
        self.assertGreaterEqual(len(branches), 3)


class TestScratchpadSynthesizer(unittest.TestCase):
    def test_add_thought(self):
        synth = ScratchpadSynthesizer()
        entry = synth.add_thought("Analyze the problem", priority=0.7)
        self.assertEqual(entry.type, EntryType.THOUGHT)
        self.assertEqual(synth.memory.count, 1)

    def test_add_action(self):
        synth = ScratchpadSynthesizer()
        entry = synth.add_action("Run the query")
        self.assertEqual(entry.type, EntryType.ACTION)

    def test_add_observation(self):
        synth = ScratchpadSynthesizer()
        entry = synth.add_observation("Found a pattern")
        self.assertEqual(entry.type, EntryType.OBSERVATION)

    def test_add_reflection(self):
        synth = ScratchpadSynthesizer()
        entry = synth.add_reflection("This suggests a correlation")
        self.assertEqual(entry.type, EntryType.REFLECTION)

    def test_synthesize(self):
        synth = ScratchpadSynthesizer()
        synth.add_thought("Need to analyze", priority=0.7)
        synth.add_action("Loaded data", priority=0.6)
        synth.add_observation("Found outliers", priority=0.8)
        synth.add_reflection("Outliers are significant", priority=0.9)
        result = synth.synthesize()
        self.assertGreater(result.entry_count, 0)
        self.assertGreater(result.confidence, 0)
        self.assertGreater(len(result.chain_of_thought), 0)

    def test_retrieve(self):
        synth = ScratchpadSynthesizer()
        synth.add_thought("Machine learning model", priority=0.7)
        synth.add_thought("Database optimization", priority=0.6)
        results = synth.retrieve("machine learning")
        self.assertGreater(len(results), 0)

    def test_create_branch(self):
        synth = ScratchpadSynthesizer()
        synth.add_thought("Initial thought")
        branch = synth.create_branch("Alternative")
        self.assertIsNotNone(branch.id)
        synth.add_thought("Alt thought", branch=branch.id)
        self.assertGreater(len(branch.entries), 0)

    def test_merge_branch(self):
        synth = ScratchpadSynthesizer()
        synth.add_thought("Main thought")
        branch = synth.create_branch("Alt")
        synth.add_thought("Alt thought", branch=branch.id)
        merged = synth.merge_branch(branch.id, "main")
        self.assertGreater(len(merged.entries), 1)

    def test_serialize_deserialize(self):
        synth = ScratchpadSynthesizer()
        synth.add_thought("Test thought", priority=0.7)
        synth.add_action("Test action", priority=0.6)
        serialized = synth.serialize()
        restored = ScratchpadSynthesizer.deserialize(serialized)
        self.assertEqual(restored.memory.count, 2)

    def test_compress(self):
        synth = ScratchpadSynthesizer(max_entries=100, compress_after=5)
        for i in range(10):
            synth.add_thought(f"Thought {i}", priority=0.5)
        self.assertLessEqual(synth.memory.count, 100)

    def test_get_status(self):
        synth = ScratchpadSynthesizer()
        synth.add_thought("test")
        status = synth.get_status()
        self.assertIn("memory_count", status)
        self.assertIn("branch_count", status)

    def test_branch_synthesis(self):
        synth = ScratchpadSynthesizer()
        synth.add_thought("Main thought", priority=0.6)
        branch = synth.create_branch("Alt")
        synth.add_thought("Alt high priority thought", priority=0.9, branch=branch.id)
        result = synth.synthesize(branch=branch.id)
        self.assertGreater(result.entry_count, 0)


class TestScratchpadMindCLI(unittest.TestCase):
    def test_cli_audit_json(self):
        from scratchpad_mind.cli import main
        self.assertEqual(main(["audit", "--json", "--primary", "20.0"]), 0)

    def test_cli_sample_csv_batch(self):
        import os
        import tempfile
        from scratchpad_mind.cli import main
        sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample.csv")
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "out_batch.csv")
            ret = main(["batch", "-i", sample_path, "-o", out_file])
            self.assertEqual(ret, 0)
            self.assertTrue(os.path.exists(out_file))


if __name__ == "__main__":
    unittest.main()

