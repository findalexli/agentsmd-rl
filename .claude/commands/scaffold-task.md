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
6. **Create all files** (see below)

## Output Structure

```
harbor_tasks/<task-name>/
├── instruction.md          # Bug description (NOT the fix)
├── task.toml               # Metadata
├── rubric.yaml             # Rules from agent configs for LLM judge
├── solution/
│   └── solve.sh            # Gold patch (idempotent)
├── environment/
│   └── Dockerfile          # Clone repo at base commit
└── tests/
    ├── test.sh             # Deterministic tests → reward.txt
    ├── judge.py            # LLM rubric judge (copy from agentsmd_rl/judge.py)
    └── judge_hook.sh       # Hook sourced at end of test.sh
```

## instruction.md

Describe the BUG, not the fix:
- Point to relevant file(s) and function(s)
- Do NOT reveal: exact code change, variable names from the patch, or PR number
- Keep it natural — as if a developer filed an internal bug report

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

## solution/solve.sh

Apply the gold patch idempotently:
- Check if already applied (grep for a distinctive line from the fix)
- Use `git apply - <<'PATCH'` (single HEREDOC, never double)
- `set -euo pipefail`

## Dockerfile

- Base: `python:3.12-slim` (or `node:22-slim` for TS, add `python3` for scoring)
- Install: `git curl ca-certificates build-essential tmux`
- Clone repo at exact base commit (BEFORE the fix)
- Install MINIMAL deps (only what test.sh needs — no torch/GPU)
- Set PYTHONPATH, configure git user, WORKDIR to repo root

## tests/test.sh

Weight budget: behavioral >=0.60, structural <=0.40, config-derived <=0.15. Total = 1.0.

| Tier | Weight | What |
|------|--------|------|
| GATE | 0 | Syntax check — abort on failure |
| Fail-to-pass | >=0.60 | Behavioral tests that FAIL on buggy code, PASS on fix |
| Pass-to-pass | ~0.10 | Existing behavior must not break |
| Structural | <=0.15 | AST checks + anti-stub |
| Config-derived | <=0.15 | Programmatic rules from agent configs |

Each check MUST have a source comment:
```bash
# [pr_diff] (0.20): Malformed lines don't crash
# [agent_config] (0.05): "No wildcard imports" — AGENTS.md:30
```

Anti-patterns (per OpenAI SWE-bench critique, see `/audit-tests` for full criteria):
- Do NOT check for specific variable names from the gold patch
- Do NOT require a specific API when alternatives work
- Do NOT import modules that chain into torch/triton — extract and exec
- ALWAYS verify: does buggy code fail? Does fixed code pass?

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

**ONLY include rules evaluable from a code diff.** Exclude:
- Process rules ("read files before modifying", "run pre-commit")
- PR/commit rules ("add Co-authored-by", "disclose AI usage")
- Tooling rules ("use uv not pip", "run make style") — these go in test.sh as config-derived checks instead
- Subjective size rules ("PRs should be brief", "minimize the diff")

Include only code quality visible in a diff: style, architecture, safety, naming.

**Validation**: mentally apply the gold patch and ask — would it pass every rule? If not, remove the rule.

If a config rule is programmatically verifiable (formatter, grep pattern, AST check), add it to test.sh as a `[agent_config]` check instead of rubric.yaml.

## Self-Check

Before finishing, verify:
1. instruction.md doesn't leak the fix
2. solve.sh applies cleanly and is idempotent
3. test.sh weights sum to 1.0, behavioral >= 0.60
4. rubric.yaml rules exist verbatim in the cited files at the base commit
5. Dockerfile builds and test.sh runs
