# Parallelize code-change-verification validation steps

## Problem

The `code-change-verification` skill in `.agents/skills/code-change-verification/` currently runs all six verification steps (`pnpm i`, `pnpm build`, `pnpm -r build-check`, `pnpm -r -F "@openai/*" dist:check`, `pnpm lint`, `pnpm test`) strictly sequentially in both `scripts/run.sh` and `scripts/run.ps1`. The last four steps (`build-check`, `dist-check`, `lint`, `test`) are independent of each other and could run in parallel after `install` and `build` complete, significantly speeding up the verification cycle.

The duplicated shell logic between `run.sh` (bash) and `run.ps1` (PowerShell) also makes maintenance harder — any change to the step sequence requires updating both scripts.

## Expected Behavior

- Create a shared Node.js runner (`scripts/run.mjs`) that keeps `pnpm i` and `pnpm build` as sequential barriers, then runs the remaining validation steps (`build-check`, `dist-check`, `lint`, `test`) in parallel with fail-fast cancellation and prefixed step output.
- Simplify `run.sh` and `run.ps1` to delegate to the new Node runner instead of containing their own step logic.
- The runner should export a `createDefaultPlan` function so the plan structure (sequential barriers + parallel steps) is inspectable and testable.
- Implement proper signal handling (SIGINT, SIGTERM) to clean up child processes.
- After making the code changes, update the relevant agent instruction files (`.agents/skills/code-change-verification/SKILL.md` and `AGENTS.md`) to accurately describe the new phase-based execution model. The documentation should reflect that steps now run in phases with barriers, not strictly in a fixed sequential order.

## Files to Look At

- `.agents/skills/code-change-verification/scripts/run.sh` — current bash runner with sequential steps
- `.agents/skills/code-change-verification/scripts/run.ps1` — current PowerShell runner with sequential steps
- `.agents/skills/code-change-verification/SKILL.md` — skill documentation describing the verification workflow
- `AGENTS.md` — root contributor guide referencing the verification skill's execution model
