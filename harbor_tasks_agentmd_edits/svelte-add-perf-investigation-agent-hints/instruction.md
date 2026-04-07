# Add agent hints for performance investigations

## Problem

The Svelte monorepo has a benchmarking system at `benchmarking/compare/` that can compare performance across branches via `pnpm bench:compare`. However, there are no agent instructions or skill definitions to guide AI coding agents through performance investigation workflows. Additionally, there is no utility for quickly comparing CPU profile hotspots between two branches — agents (and developers) must manually inspect raw `.cpuprofile` files.

## What's Needed

1. **A profile diff utility** (`benchmarking/compare/profile-diff.mjs`): A Node.js script that reads two `.cpuprofile` files (one per branch) for a given benchmark name and prints the top function-level sample-share deltas. It should:
   - Accept 3 positional arguments: `<benchmark> <base-branch> <candidate-branch>`
   - Print a usage error and exit 1 if required arguments are missing
   - Read cpuprofile JSON from `benchmarking/compare/.profiles/<branch>/<benchmark>.cpuprofile`
   - Compute per-function self-sample percentages and output the top 20 deltas sorted by absolute change

2. **An `AGENTS.md` file** at the repository root: A concise guide for AI coding agents working in this monorepo. It should reference `CONTRIBUTING.md` for general contribution guidelines and point agents to the performance investigation skill when relevant.

3. **A performance investigation skill** (`.agents/skills/performance-investigation/SKILL.md`): A detailed skill file with YAML frontmatter that documents the full performance investigation workflow — how to run benchmarks, where outputs go, how to interpret results, and how to use the profile diff script.

## Files to Look At

- `benchmarking/compare/` — the existing benchmarking infrastructure (look at what's already there)
- `CONTRIBUTING.md` — existing contribution guidelines that the agent guide should reference
