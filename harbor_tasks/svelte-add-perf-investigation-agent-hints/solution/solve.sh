#!/usr/bin/env bash
set -euo pipefail

cd /workspace/svelte

# Idempotent: skip if already applied
if grep -q 'performance-investigation' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create AGENTS.md
cat > AGENTS.md <<'AGENTSEOF'
# Svelte Coding Agent Guide

This guide is for AI coding agents working in the Svelte monorepo.

**Important:** Read and follow [`CONTRIBUTING.md`](./CONTRIBUTING.md) as well - it contains essential information about testing, code structure, and contribution guidelines that applies here.

## Quick Reference

If asked to do a performance investigation, use the `performance-investigation` skill.
AGENTSEOF

# Create SKILL.md
mkdir -p .agents/skills/performance-investigation
cat > .agents/skills/performance-investigation/SKILL.md <<'SKILLEOF'
---
name: performance-investigation
description: Investigate performance regressions and find opportunities for optimization
---

## Quick start

1. Start from a branch you want to measure (for example `foo`).
2. Run:

```sh
pnpm bench:compare main foo
```

If you pass one branch, `bench:compare` automatically compares it to `main`.

## Where outputs go

- Summary report: `benchmarking/compare/.results/report.txt`
- Raw benchmark numbers:
  - `benchmarking/compare/.results/main.json`
  - `benchmarking/compare/.results/<your-branch>.json`
- CPU profiles (per benchmark, per branch):
  - `benchmarking/compare/.profiles/main/*.cpuprofile`
  - `benchmarking/compare/.profiles/main/*.md`
  - `benchmarking/compare/.profiles/<your-branch>/*.cpuprofile`
  - `benchmarking/compare/.profiles/<your-branch>/*.md`

The `.md` files are generated summaries of the CPU profile and are usually the fastest way to inspect hotspots.

## Suggested investigation flow

1. Open `benchmarking/compare/.results/report.txt` and identify largest regressions first.
2. For each high-delta benchmark, compare:
   - `benchmarking/compare/.profiles/main/<benchmark>.md`
   - `benchmarking/compare/.profiles/<branch>/<benchmark>.md`
3. Look for changes in self/inclusive hotspot share in runtime internals (`runtime.js`, `reactivity/batch.js`, `reactivity/deriveds.js`, `reactivity/sources.js`).
4. Make one optimization change at a time, then re-run targeted benches before re-running full compare.

## Fast benchmark loops

Run only selected reactivity benchmarks by substring:

```sh
pnpm bench kairo_mux kairo_deep kairo_broad kairo_triangle
pnpm bench repeated_deps sbench_create_signals mol_owned
```

## Tests to run after perf changes

Runtime reactivity regressions are most likely in runes runtime tests:

```sh
pnpm test runtime-runes
```

## Helpful script

For quick cpuprofile hotspot deltas between two branches:

```sh
node benchmarking/compare/profile-diff.mjs kairo_mux_owned main foo
```

This prints top function sample-share deltas for the selected benchmark.

## Practical gotchas

- `bench:compare` checks out branches while running. Avoid uncommitted changes (or stash them) so branch switching is safe.
- Each `bench:compare` run rewrites `benchmarking/compare/.results` and `benchmarking/compare/.profiles`.
SKILLEOF

# Create profile-diff.mjs
cat > benchmarking/compare/profile-diff.mjs <<'SCRIPTEOF'
import fs from 'node:fs';
import path from 'node:path';

const [benchmark, baseBranch = 'main', candidateBranch] = process.argv.slice(2);

if (!benchmark || !candidateBranch) {
	console.error(
		'Usage: node benchmarking/compare/profile-diff.mjs <benchmark> <base-branch> <candidate-branch>'
	);
	process.exit(1);
}

const root = path.resolve('benchmarking/compare/.profiles');

function safe(name) {
	return name.replace(/[^a-z0-9._-]+/gi, '_');
}

function read_profile(branch, bench) {
	const file = path.join(root, safe(branch), `${bench}.cpuprofile`);
	const profile = JSON.parse(fs.readFileSync(file, 'utf8'));
	const nodes = Array.isArray(profile.nodes) ? profile.nodes : [];
	const samples = Array.isArray(profile.samples) ? profile.samples : [];

	const id_to_node = new Map(nodes.map((node) => [node.id, node]));
	const self_counts = new Map();

	for (const sample of samples) {
		if (typeof sample !== 'number') continue;
		self_counts.set(sample, (self_counts.get(sample) ?? 0) + 1);
	}

	const total = samples.length || 1;
	const by_fn = new Map();

	for (const [id, count] of self_counts) {
		const node = id_to_node.get(id);
		if (!node || typeof node !== 'object') continue;

		const frame = node.callFrame ?? {};
		const function_name = frame.functionName || '(anonymous)';
		const url = frame.url || '';
		const line = typeof frame.lineNumber === 'number' ? frame.lineNumber + 1 : 0;

		const label = url
			? `${function_name} @ ${url.replace(/^.*packages\//, 'packages/')}:${line}`
			: function_name;

		by_fn.set(label, (by_fn.get(label) ?? 0) + count);
	}

	return { by_fn, total };
}

const base = read_profile(baseBranch, benchmark);
const candidate = read_profile(candidateBranch, benchmark);

const keys = new Set([...base.by_fn.keys(), ...candidate.by_fn.keys()]);
const rows = [...keys]
	.map((key) => {
		const base_pct = ((base.by_fn.get(key) ?? 0) * 100) / base.total;
		const candidate_pct = ((candidate.by_fn.get(key) ?? 0) * 100) / candidate.total;
		return {
			key,
			delta: candidate_pct - base_pct,
			base_pct,
			candidate_pct
		};
	})
	.sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
	.slice(0, 20);

console.log(`Benchmark: ${benchmark}`);
console.log(`Base: ${baseBranch}`);
console.log(`Candidate: ${candidateBranch}`);
console.log('');

for (const row of rows) {
	const sign = row.delta >= 0 ? '+' : '';
	console.log(
		`${sign}${row.delta.toFixed(2).padStart(6)}pp  candidate ${row.candidate_pct.toFixed(2).padStart(6)}%  base ${row.base_pct.toFixed(2).padStart(6)}%  ${row.key}`
	);
}
SCRIPTEOF

echo "Patch applied successfully."
