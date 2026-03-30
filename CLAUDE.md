# agentsmd-rl

See [README.md](README.md) for project overview, research question, and task list.

## Repository Structure

```
agentsmd_rl/            # Python package (placeholder)
harbor_tasks/           # Harbor-compatible benchmark tasks
  <task>/
    instruction.md      # Agent reads this (bug description, not the fix)
    task.toml           # Metadata (difficulty, timeouts, resources)
    eval_manifest.yaml  # Declares graders, checks, weights, and source attribution
    environment/Dockerfile  # Clones repo at pre-fix commit
    tests/test.sh       # Deterministic graders → reward.txt / reward.json
research/               # Research docs and analysis
```

## Task Selection Criteria

Tasks must come from repos that have agent instruction files:
- CLAUDE.md, AGENTS.md, .claude/skills/, .cursorrules, .github/copilot-instructions.md

And satisfy standard requirements:
- Public repo, specific base commit, no secrets/accounts needed
- CPU-testable (no GPU required for verification)
- Fix is non-trivial but contained (1-5 files changed)

## Adding a New Task

1. `/scaffold-task owner/repo#PR_NUMBER` — create task from a PR
2. `/audit-tests <task-name>` — audit tests for gaming/narrowness, rewrite if needed
3. `/validate-task <task-name>` — final sign-off (instruction quality, environment, alignment)

## Evaluation Architecture

Three grader types, unified attribution. See `research/grading-schema-comparison.md` for full rationale.

### The atom: Check

Every assertion — behavioral test, lint check, LLM rubric rule — is a `Check` with:
- `origin`: where it came from (`pr_diff`, `repo_tests`, `agent_config`, `static`)
- `source`: optional `SourceRef` pointing to exact file + lines + commit in the repo
- `weight`: how much it contributes to its grader's score

### Graders compose checks

| Grader | Type | What it runs | Weight budget |
|--------|------|-------------|---------------|
| `behavioral` | deterministic | Fail-to-pass tests from the PR | >=0.60 |
| `regression` | deterministic | Pass-to-pass + anti-stub | ~0.10–0.20 |
| `config` | deterministic | Programmatic rules from agent configs | <=0.15 |
| `style_rubric` | model_based | LLM judge on soft rules | ~0.10–0.15 |

A grader can be a **gate** — if it scores 0, the whole task scores 0 (e.g., syntax check).

### Source attribution

Every check with `origin: agent_config` MUST have a `source` pointing to the exact markdown file and line range. Use **full repo-relative paths** (`extensions/CLAUDE.md`, not `CLAUDE.md`).

In test.sh, every check MUST have a comment:
```bash
# [pr_diff] (0.20): Malformed lines don't crash
# [agent_config] (0.05): "Run ruff format" — AGENTS.md:32-33 @ abc123
```

### Output

test.sh writes `reward.txt` (single float) and optionally `reward.json`:
```json
{"reward": 0.85, "behavioral": 0.65, "regression": 0.10, "config": 0.05, "style_rubric": 0.05}
```

For RL: `execution_bucket` (deterministic) + `model_reward` (LLM judge) follow the SWE-RM additive pattern.

## Rubric Source Traceability

Known repos with multiple config files — always enumerate before citing:
- `openclaw/openclaw`: root + `extensions/`, `src/channels/`, `src/plugins/`, `src/gateway/protocol/`
- `anomalyco/opencode`: root + `packages/app/`, `packages/opencode/`, `packages/desktop/`
- `pytorch/pytorch`: root + `torch/_dynamo/`

Enumerate with: `gh api repos/OWNER/REPO/git/trees/COMMIT?recursive=1 --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md")) | .path'`
