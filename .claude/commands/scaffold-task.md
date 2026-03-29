# Scaffold Task

Create `harbor_tasks/$ARGUMENTS/` from a GitHub PR in a repo with agent instruction files.

## Inputs

Provide the PR URL or `owner/repo#number` as the argument (e.g., `sgl-project/sglang#21471`).

## Steps

1. **Fetch PR metadata** -- `gh pr view <N> --repo <owner/repo> --json title,body,files,mergeCommit`
2. **Get base commit** -- parent of the merge commit: `gh api repos/<owner/repo>/commits/<merge_sha> --jq '.parents[0].sha'`
3. **Check for agent configs** -- does the repo have CLAUDE.md, AGENTS.md, .claude/, .cursorrules, .github/copilot-instructions.md?
4. **Read the PR diff** -- `gh pr diff <N> --repo <owner/repo>`
5. **Choose task name** -- `<repo-short>-<descriptive-slug>` (e.g., `sglang-detokenizer-unbound-fix`)
6. **Create directory structure**:

```
harbor_tasks/$ARGUMENTS/
├── instruction.md          # Bug description (from PR body, NOT the fix)
├── task.toml               # Metadata
├── environment/
│   └── Dockerfile          # Clone repo at base commit, minimal deps
└── tests/
    └── test.sh             # Fail-to-pass verification
```

## instruction.md

Derive from the PR description / linked issue. Rules:
- Describe the BUG, not the fix
- Point to the relevant file(s) and function(s)
- Do NOT reveal: the exact code change, variable names from the patch, or the PR number
- Do NOT include the diff or any code from the fix
- Keep it natural -- as if a developer filed an internal bug report

## task.toml

```toml
version = "1.0"

[metadata]
author_name = "Alex Li"
author_email = "alex@example.com"
difficulty = "medium"          # easy/medium/hard
category = "bugfix"            # bugfix/feature/performance
tags = ["repo-name", "relevant", "tags"]
expert_time_estimate_min = 10.0
junior_time_estimate_min = 30.0

[verifier]
timeout_sec = 60.0

[agent]
timeout_sec = 1200.0

[environment]
build_timeout_sec = 600.0
cpus = 1
memory = "4G"
storage = "10G"
allow_internet = true
```

## Dockerfile

- Base: `python:3.12-slim`
- Install: `git curl ca-certificates build-essential tmux`
- Clone repo at the exact base commit (BEFORE the fix)
- Install MINIMAL deps (only what test.sh needs -- avoid torch/GPU packages)
- Set PYTHONPATH
- Configure git user
- WORKDIR to the repo root

## tests/test.sh

Follow the test design philosophy from research/test-design-audit.md:

1. **GATE**: Python syntax check (non-scoring, abort on failure)
2. **FAIL-TO-PASS** (primary, >=60% weight): Behavioral tests that fail on buggy code, pass on correct fix. Extract functions via AST + exec with mocks to avoid importing heavy deps.
3. **PASS-TO-PASS** (regression): Existing behavior that must not break
4. **STRUCTURAL** (supplementary, <=40%): AST checks as partial credit, accepting multiple valid implementations

Anti-patterns to avoid (per OpenAI SWE-bench critique):
- Do NOT check for specific variable names from the gold patch
- Do NOT require a specific API when alternatives work (e.g., `setdefault` vs `if not in`)
- Do NOT import modules that chain into torch/triton -- extract and exec instead
- ALWAYS test: does the buggy code fail this test? Does the fixed code pass?
