# Subagent Duration Display Shows Inflated Runtime

## Bug Description

When running `/subagents list` or `/subagents info` during an active subagent run, the displayed runtime is inflated by approximately 5-6x. For example, a subagent that has been running for ~30 seconds shows "1m" instead of "30s".

The root cause is in `src/shared/subagents-format.ts`. The `formatDurationCompact` function in that file converts milliseconds to minutes by dividing by 60,000 and then rounding up with `Math.max(1, ...)`, which means anything under 60 seconds gets displayed as "1m". It also completely lacks second-level granularity — it jumps directly from minutes to hours to days.

There is already a canonical `formatDurationCompact` implementation in `src/infra/format-time/format-duration.ts` that correctly handles second-level precision (e.g. "30s", "1m30s") and is used by other callers in the codebase (bash-tools, sandbox-display, usage-render). The shared subagents module has its own duplicate that behaves differently.

## Affected Files

- `src/shared/subagents-format.ts` — contains the buggy duplicate formatter
- `src/agents/subagent-control.ts` — calls `formatDurationCompact` from the shared module
- `src/auto-reply/reply/commands-subagents/shared.ts` — calls `formatDurationCompact` from the shared module

## Expected Behavior

- `formatDurationCompact(30_000)` should return `"30s"`
- `formatDurationCompact(90_000)` should return `"1m30s"`
- Callers should handle the case where the formatter returns `undefined` for invalid input (the canonical implementation returns `undefined` rather than `"n/a"`)

## Repro

1. Spawn a subagent with a short task (~30 seconds)
2. Run `/subagents list` during execution
3. Observe the runtime column — it shows "1m" instead of "30s"

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
