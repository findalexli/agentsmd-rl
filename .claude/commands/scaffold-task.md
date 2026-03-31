# Scaffold Task

Create a complete benchmark task from a GitHub PR: `harbor_tasks/$ARGUMENTS/`.

## Inputs

PR URL or `owner/repo#number` (e.g., `sgl-project/sglang#21471`).

## Steps

1. **Fetch PR metadata** — `gh pr view <N> --repo <owner/repo> --json title,body,files,mergeCommit`
2. **Get base commit** — parent of merge commit: `gh api repos/<owner/repo>/commits/<merge_sha> --jq '.parents[0].sha'`
3. **Check for agent configs** — does the repo have CLAUDE.md, AGENTS.md, .claude/, .cursorrules, .github/copilot-instructions.md?
4. **Read the PR diff** — `gh pr diff <N> --repo <owner/repo>`
5. **Choose task name** — `<repo-short>-<descriptive-slug>`
6. **Create files in this order:** Dockerfile → solve.sh → task.toml → test.sh → rubric.yaml → **instruction.md (LAST)**

## Output Structure

```
harbor_tasks/<task-name>/
├── instruction.md          # Bug description — written LAST
├── task.toml               # Metadata
├── rubric.yaml             # Rules from agent configs for LLM judge
├── solution/
│   └── solve.sh            # Gold patch (idempotent)
├── environment/
│   └── Dockerfile          # Clone repo at base commit
└── tests/
    ├── test.sh             # Deterministic tests → /logs/verifier/reward.txt
    ├── judge.py            # LLM rubric judge (copy from agentsmd_rl/judge.py)
    └── judge_hook.sh       # Hook sourced at end of test.sh
```

## Dockerfile

- Base: `python:3.12-slim` (or `node:22-slim` for TS, add `python3` for scoring)
- Install: `git curl ca-certificates build-essential tmux`
- Use sanitized snapshot (no .git history): `git fetch --depth=1 origin <COMMIT>` → `rm -rf .git` → `git init` → `git add -A` → `git commit -m "snapshot"`
- Install MINIMAL deps (only what test.sh needs — no torch/GPU)
- Set PYTHONPATH, configure git user, WORKDIR to `/workspace/<repo-name>`
- Always `mkdir -p /logs/verifier`

## solution/solve.sh

Apply the gold patch idempotently:
- Check if already applied (grep for a distinctive line from the fix)
- Use `git apply - <<'PATCH'` (single HEREDOC, never double)
- `set -euo pipefail`

## task.toml

```toml
version = "1.0"

[metadata]
author_name = "Alex Li"
author_email = "alex@example.com"
difficulty = "medium"
category = "bugfix"
tags = ["repo-name", "relevant", "tags"]
expert_time_estimate_min = 10.0
junior_time_estimate_min = 30.0

[verifier]
env = { LLM_JUDGE = "${LLM_JUDGE:-0}", ANTHROPIC_API_KEY = "${ANTHROPIC_API_KEY:-}" }
timeout_sec = 60.0

[agent]
timeout_sec = 1200.0

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 4096
storage_mb = 10240
allow_internet = true
```

## tests/test.sh

**REWARD PATH**: MUST write to `/logs/verifier/reward.txt` (Harbor convention). Use this template at the top:
```bash
#!/usr/bin/env bash
set +e
set -uo pipefail

REWARD_FILE="/logs/verifier/reward.txt"
REWARD_JSON="/logs/verifier/reward.json"

# ... scoring logic ...

echo "$SCORE" > "$REWARD_FILE"
```

NEVER write to `/tests/reward.txt`, `/workspace/reward.txt`, `$TASK_DIR/tests/reward.txt`, or any other path. Harbor's verifier ONLY reads from `/logs/verifier/`.

Weight budget: behavioral >=0.60, structural <=0.40, config-derived <=0.15. Total = 1.0.

| Tier | Weight | What |
|------|--------|------|
| GATE | 0 | Syntax check — abort on failure |
| Fail-to-pass | >=0.60 | Behavioral tests that FAIL on buggy code, PASS on fix |
| Pass-to-pass | ~0.10 | Existing behavior must not break |
| Structural | <=0.15 | AST checks + anti-stub |
| Config-derived | <=0.15 | Programmatic rules from agent configs |

**CRITICAL: Prefer calling code over inspecting code.** AST checks are a last resort.
- torch.nn.Module code works on CPU tensors — call `forward()` with small dims
- Pure Python logic — call it directly
- Only use AST for Triton `@triton.jit` kernels, CUDA C++, or code needing unavailable model weights
- For every `ast.parse` check, justify WHY the code can't be called directly

**Pass-to-pass via upstream tests**: Check if the repo has pytest/vitest/jest test suites. If CPU-safe tests exist, use them as P2P regression checks (10-20% weight). Don't invent fake P2P tests.

Each check MUST have a source comment:
```bash
# [pr_diff] (0.20): Malformed lines don't crash
# [agent_config] (0.05): "No wildcard imports" — AGENTS.md:30
```

Anti-patterns (see `/audit-tests` for full 10-pattern checklist):
- No import/AST fallbacks — if import fails, score 0
- No self-referential extraction — never test agent's output against values from that same output
- No stub-passable tests — verify return values, not just "doesn't crash"
- No ungated structural — gate ALL structural points behind behavioral/compilation passing first
- No single-value parameter tests — vary parameters to catch hardcoded constants

Append at end of test.sh:
```bash
# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
```

## rubric.yaml

Enumerate ALL agent config files at the base commit:
```
gh api "repos/OWNER/REPO/git/trees/BASE_COMMIT?recursive=1" \
  --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md|\\.cursorrules|copilot-instructions")) | .path'
```

Fetch each, extract rules **verbatim**, write:
```yaml
rules:
  - rule: "exact text from the config file"
    from: "path/to/AGENTS.md:LINE_NUMBER"
```

**ONLY include rules evaluable from a code diff.** Exclude process rules, PR/commit rules, tooling rules, subjective size rules. Include only code quality visible in a diff.

If a config rule is programmatically verifiable, add it to test.sh as a `[agent_config]` check instead.

## instruction.md — WRITE THIS LAST

**Why last:** By now you've written test.sh and know exactly what behavioral gap the fix addresses. The instruction should describe THAT gap — not echo the PR body (which increasingly is AI-generated and leaks implementation details).

**What to write:** Describe the *symptom* the failing test captures. Think: "what would a developer observe that made them file this bug?"

- If test.sh checks that `f(None)` crashes → instruction says "function crashes on None input"
- If test.sh checks return value is wrong → instruction says "function returns X, expected Y"
- If test.sh checks a race condition → instruction says "intermittent failure under concurrent use"

**Rules:**
- Do NOT copy from the PR body — it likely contains implementation details or was AI-generated
- Do NOT reveal: exact code change, variable names from the patch, or PR number
- Do NOT mention which test file to look at
- DO point to the relevant file(s) and function(s)
- Keep it natural — as if a developer filed an internal bug report
- Some ambiguity is OK — forces the agent to explore the codebase

**Leakage check:** After writing, verify no identifier unique to the added lines of the diff appears in the instruction.

## Self-Check

Before finishing, verify:
1. instruction.md doesn't leak the fix and doesn't parrot the PR body
2. solve.sh applies cleanly and is idempotent
3. test.sh weights sum to 1.0, behavioral >= 0.60
4. rubric.yaml rules exist verbatim in the cited files at the base commit
5. Dockerfile builds and test.sh runs
