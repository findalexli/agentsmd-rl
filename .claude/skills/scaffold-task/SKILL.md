---
name: scaffold-task
description: Create a benchmark task from a GitHub PR. Use when generating new harbor tasks from merged PRs — fetches PR metadata, discovers agent configs, generates tests, Dockerfile, solve.sh, and eval_manifest.yaml.
argument-hint: "owner/repo#number (e.g., sgl-project/sglang#21471)"
allowed-tools: Bash(gh:*), Bash(git:*), Bash(python3:*), Bash(curl:*), Read, Edit, Write, Glob, Grep
---

# Scaffold Task

Create a benchmark task from a GitHub PR. The PR is the "gold solution" — we build tests that verify it.

## Input

`$ARGUMENTS` = `owner/repo#number`

## Quick reference

| Step | What | Reference |
|------|------|-----------|
| 1. Fetch PR metadata | gh CLI calls for title, body, diff, base commit | [steps.md](steps.md) §1 |
| 2. Discover agent configs | Find all CLAUDE.md/AGENTS.md/SKILL.md at base commit | [steps.md](steps.md) §2 |
| 3. Copy template + fill | Copy `taskforge/templates/task_template/` → `markdown_following/` | [steps.md](steps.md) §3 |
| 4. Write files | Dockerfile, solve.sh, test_outputs.py, eval_manifest.yaml, instruction.md | [steps.md](steps.md) §4 |
| 5. Self-audit | Stub walk, alternative fix, F2P coverage, anti-patterns | [steps.md](steps.md) §5 |

## Key principles

- **Binary scoring**: all checks pass → reward 1, any fail → reward 0
- **Call code, don't inspect it**: import and run functions, not AST/grep
- **Fail-to-pass primary**: tests must fail on base commit, pass on gold fix
- **Vary inputs**: never test with a single parameter value
- **instruction.md last**: write it after you know what tests check

## Task naming

`<repo-short>-<descriptive-slug>` (e.g., `sglang-detokenizer-unbound-fix`)

## Output directory

Write to `markdown_following/$TASK_NAME/` (or `markdown_edits/$TASK_NAME/` if the PR also modifies agent config files).

## Anti-patterns to avoid

See [test-design.md](test-design.md) for the 10 anti-patterns and design principles for test_outputs.py.

## For agentmd-edit tasks

If the PR modifies BOTH code AND agent config files (README.md, CLAUDE.md, etc.):
- Config file tests go to `rubric` in eval_manifest.yaml (LLM-judged), not binary checks
- The `reference` field in rubric rules gets auto-populated from solve.sh
- See [agentmd-edits.md](agentmd-edits.md) for the config edit evaluation architecture
