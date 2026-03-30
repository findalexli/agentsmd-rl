# Task Fill Agent Prompt Template

You are filling in a scaffolded SWE benchmark task. The directory structure already exists at `harbor_tasks/{task_name}/`. Your job is to create production-quality content for each file.

## Input Context

Read `harbor_tasks/{task_name}/_pr_meta.json` for:
- repo, pr_number, title, body, merge_commit, base_commit, files, language, diff

## Files to Create/Update

### 1. instruction.md
Describe the BUG, not the fix. Rules:
- Write as if a developer filed an internal bug report
- Point to relevant file(s) and function(s)
- Do NOT reveal: exact code change, variable names from the patch, or PR number
- Do NOT include diff or fix code
- Include reproduction steps or symptoms

### 2. tests/test.sh
Follow the behavioral-first test design:
- GATE: syntax check (non-scoring)
- FAIL-TO-PASS (>=60% weight): Tests that fail on buggy code, pass on fix
- PASS-TO-PASS (~10-20%): Regression tests
- STRUCTURAL (<=40%): AST checks as partial credit
- ANTI-STUB (~15%): Verify function isn't stubbed out

For Python: Use AST extraction + exec with mocks to avoid heavy imports.
For TypeScript/JavaScript: Use node to parse/run isolated code.
For Rust: Use AST analysis or compile-check specific patterns.

Write to `/logs/verifier/reward.txt`. Total weight = 1.0. Use `set +e`.

### 3. solution/solve.sh
Apply the gold patch idempotently:
- Check if already applied (grep for distinctive line from fix)
- Use `git apply` with the exact diff from the PR
- Set `set -euo pipefail`

### 4. rubric.yaml
Extract rules from the repo's agent config files at the base_commit.
Use the GitHub API to fetch config file contents:
```
gh api repos/OWNER/REPO/contents/CLAUDE.md?ref=BASE_COMMIT --jq '.content' | base64 -d
gh api repos/OWNER/REPO/contents/AGENTS.md?ref=BASE_COMMIT --jq '.content' | base64 -d
```

Each rule must have:
- id: stable slug
- text: rule statement for LLM judge
- source: {file, lines, commit} traceable to actual config content
- scope: repo or task
- weight, applicability, tags

### 5. environment/Dockerfile
Update if needed:
- Ensure correct base commit is checked out
- Add any minimal dependencies the tests need (no GPU packages)
- Set correct PYTHONPATH or equivalent

### 6. Remove _pr_meta.json
Delete the scaffolding metadata file after filling is complete.

## Quality Checks
After creating all files:
1. Verify test.sh has >=60% behavioral weight
2. Verify solve.sh applies cleanly
3. Verify rubric rules trace to actual config file content at base_commit
4. Verify instruction.md doesn't leak the fix
