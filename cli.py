#!/usr/bin/env python3
"""CLI for Agent Scratchpad Synthesizer."""
import argparse
import json
import sys
from scratchpad_engine import ScratchpadSynthesizer, EntryType


def cmd_add(args):
    synth = ScratchpadSynthesizer(max_entries=args.max_entries)
    entry_type = EntryType(args.type)
    if entry_type == EntryType.THOUGHT:
        entry = synth.add_thought(args.content, priority=args.priority)
    elif entry_type == EntryType.ACTION:
        entry = synth.add_action(args.content, priority=args.priority)
    elif entry_type == EntryType.OBSERVATION:
        entry = synth.add_observation(args.content, priority=args.priority)
    elif entry_type == EntryType.REFLECTION:
        entry = synth.add_reflection(args.content, priority=args.priority)
    print(f"Added {args.type}: {entry.id}")


def cmd_synthesize(args):
    synth = ScratchpadSynthesizer()
    synth.add_thought("Need to analyze the problem", priority=0.7)
    synth.add_action("Searched for relevant data", priority=0.6)
    synth.add_observation("Found key pattern in the data", priority=0.8)
    synth.add_reflection("The pattern suggests a correlation", priority=0.9)
    result = synth.synthesize()
    print(f"Summary: {result.summary}")
    print(f"Confidence: {result.confidence}")
    print(f"Insights: {result.key_insights}")
    print(f"Chain of thought ({len(result.chain_of_thought)} steps):")
    for step in result.chain_of_thought:
        print(f"  {step['step']}. [{step['type']}] {step['content'][:80]}")


def cmd_retrieve(args):
    synth = ScratchpadSynthesizer()
    synth.add_thought("Machine learning model training", priority=0.8)
    synth.add_observation("Loss decreasing over epochs", priority=0.7)
    synth.add_thought("Data preprocessing pipeline", priority=0.6)
    synth.add_reflection("Model performance is improving", priority=0.9)
    results = synth.retrieve(args.query, top_k=args.top_k)
    print(f"Query: '{args.query}'")
    for entry, score in results:
        print(f"  [{entry.type.value}] {entry.content[:60]} (score: {score:.3f})")


def cmd_branch(args):
    synth = ScratchpadSynthesizer()
    synth.add_thought("Initial approach: linear regression", priority=0.6)
    synth.add_observation("Data has non-linear patterns", priority=0.7)
    branch = synth.create_branch("Alternative approach")
    synth.add_thought("Try neural network instead", priority=0.8, branch=branch.id)
    synth.add_observation("NN converges faster", priority=0.7, branch=branch.id)
    synth.merge_branch(branch.id, "main", strategy=args.strategy)
    result = synth.synthesize()
    print(f"Merged branch '{branch.name}' into main")
    print(f"Total entries: {result.entry_count}")
    print(f"Branches: {result.branch_count}")


def cmd_serialize(args):
    synth = ScratchpadSynthesizer()
    synth.add_thought("Test thought", priority=0.5)
    synth.add_action("Test action", priority=0.6)
    serialized = synth.serialize()
    print("Serialized:")
    print(serialized[:500])
    restored = ScratchpadSynthesizer.deserialize(serialized)
    print(f"\nRestored: {restored.get_status()}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="agent-scratchpad-synthesizer",
        description="Structured scratchpad with chain-of-thought synthesis, branching, and retrieval"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add", help="Add a scratchpad entry")
    p_add.add_argument("--type", required=True, choices=["thought", "action", "observation", "reflection"])
    p_add.add_argument("--content", required=True, help="Entry content")
    p_add.add_argument("--priority", type=float, default=0.5)
    p_add.add_argument("--max-entries", type=int, default=100)

    subparsers.add_parser("synthesize", help="Synthesize scratchpad demo")

    p_retrieve = subparsers.add_parser("retrieve", help="Retrieve similar entries")
    p_retrieve.add_argument("--query", required=True, help="Search query")
    p_retrieve.add_argument("--top-k", type=int, default=5)

    p_branch = subparsers.add_parser("branch", help="Branch and merge demo")
    p_branch.add_argument("--strategy", default="append",
                          choices=["append", "interleave", "priority"])

    subparsers.add_parser("serialize", help="Serialization demo")

    args = parser.parse_args(argv)

    if args.command == "add":
        cmd_add(args)
    elif args.command == "synthesize":
        cmd_synthesize(args)
    elif args.command == "retrieve":
        cmd_retrieve(args)
    elif args.command == "branch":
        cmd_branch(args)
    elif args.command == "serialize":
        cmd_serialize(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
