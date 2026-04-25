# Quarantined Tasks

This directory holds PRs that didn't pass the benchmark filters. Layout:

```
harbor_tasks_quarantine/
├── candidates/                   # 4,862 placeholders awaiting causality classification + scaffold
├── discarded_decorative/         #   899 — gold fix is independent of agent-instruction files
├── discarded_no_instructions/    #   598 — repo has no agent-instruction files at HEAD
├── discarded_unmatched/          #   627 — placeholder slug doesn't match any scout entry
├── INDEX.txt                     # legacy index of task names
├── MANIFEST.json                 # legacy {task: [discard_reasons]} mapping
└── README.md                     # this file
```

See the main [README](../README.md#how-tasks-are-filtered) for the full
filter funnel and per-stage rationale.

## What lives in each subdirectory

### `candidates/` — awaiting scaffold

Placeholder task directories (one per scouted PR), with template files
(`{{REPO}}` / `{{PR_NUMBER}}` placeholders, no real `instruction.md` /
`solve.sh` / `Dockerfile`). They survive only because their source repo
has agent-instruction files at HEAD.

To become runnable Class-A or Class-B tasks they need:
1. **Causality verdict** from the Gemini 3.1 Pro judge — does the gold
   diff edit an agent-instruction file (Type A), or follow a specific
   rule from one (Type B), or is it decorative (Type C)? If C, move to
   `discarded_decorative/`.
2. **Scaffold** via the one-call Opus pipeline — produces a real
   `instruction.md`, `tests/test_outputs.py`, `solution/solve.sh`,
   `environment/Dockerfile`, and validates the oracle.

### `discarded_decorative/`

Gold fix is determined purely by the bug; removing the repo's
agent-instruction files wouldn't have changed it. Includes:
- 117 tasks from the original Tier-A gate sweep (contaminated oracle,
  trivial gold, grep-only tests) — see `MANIFEST.json` for per-task
  reasons.
- 741 tasks from the 2026-04-24 markdown-causality sweep
  (`scripts/markdown_causality_judge.py`, Gemini-judged decorative).
- ~41 tasks from earlier triviality / no-signal filter passes.

### `discarded_no_instructions/`

The placeholder's source repo has **no agent-instruction files at HEAD**
under any of the patterns we recognize (CLAUDE.md / AGENTS.md / SKILL.md
/ .cursor/rules / .agents/skills/ / .opencode/skills/ / .codex/skills/
/ .github/skills/ / .github/prompts/*.prompt.md). There's literally no
markdown for the agent to follow — these can't be instruction-following
tasks.

### `discarded_unmatched/`

Placeholder directory name (slug) doesn't match any entry in our scout
JSONL files — orphans from older scout passes that got renamed or
removed upstream. Without a scout entry we can't recover the PR ref.

## Reinstating a task

If you have a reason to bring something back:

```bash
mv harbor_tasks_quarantine/discarded_decorative/<task-name> harbor_tasks/
# or for placeholders ready for scaffold:
mv harbor_tasks_quarantine/candidates/<task-name> harbor_tasks/
.venv/bin/python scripts/validate_batch.py \
    --task-file <(echo "<task-name>") \
    --start-at oneshot_repair --concurrency 1
```
