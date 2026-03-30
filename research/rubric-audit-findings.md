# Rubric Audit Findings (2026-03-29)

Findings from auditing all 106 task rubrics for source path accuracy and adding config-derived programmatic tests.

## Problem: Batch-generated rubrics have systematic errors

When generating 100+ tasks overnight via parallel subagents, the rubric.yaml files are the most error-prone artifact. The agents produce plausible-looking source references that don't hold up under verification.

### Error categories found

| Error Type | Count | Example |
|-----------|-------|---------|
| **Bare filename in multi-config repo** | 12 | `"CLAUDE.md"` in openclaw (which has 20 CLAUDE.md files) |
| **Wrong line numbers** | ~30 | `lines: [82, 82]` when actual rule is at line 8 |
| **File doesn't exist at cited commit** | 6 | `extensions/CLAUDE.md` cited at commits before it was created |
| **Hallucinated rules** | 7 | "kumquat" rule at line 63 of a 49-line file |
| **Invalid field names** | ~10 | `section: "Useful commands"` instead of `lines: [N, M]` |
| **Missing commit field** | ~15 | `source.commit` omitted entirely |

### Root causes

1. **Agents extrapolate from HEAD.** They see the current repo state and assume it was the same at the base commit. Files get added, lines shift, rules change.
2. **Line numbers are guessed, not verified.** No agent actually fetched the file and counted lines — they estimated based on section headers.
3. **Multi-config repos are novel.** The agents' training data doesn't include repos with `CLAUDE.md` in 10+ subdirectories. They default to the simplest path.

## Solution: Three-step verification

### 1. Enumerate before citing
```bash
gh api "repos/OWNER/REPO/git/trees/BASE_COMMIT?recursive=1" \
  --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md")) | .path'
```

### 2. Fetch and verify content at commit
```bash
gh api "repos/OWNER/REPO/contents/PATH?ref=COMMIT" --jq '.content' | base64 -d
```
Then grep for the rule text to find actual line numbers.

### 3. Automated validation (TODO)
A CI script that for each rubric rule:
- Checks `source.file` exists at `source.commit`
- Checks `source.lines` contain text matching `rule.text`
- Flags any mismatches

## Config-derived programmatic tests

### What they are
Rules from agent config files that can be verified with a shell command rather than an LLM judge.

### Categories found across 10 repos

| Category | Repos | Example rule | Verification |
|----------|-------|-------------|-------------|
| Formatter/linter | 8/10 | "Run ruff format" | `ruff check --select I FILE` |
| Type checker | 5/10 | "Run make typing" | `make typing` |
| Import boundary | 2/10 | "Extensions must import from plugin-sdk/*" | `grep` for disallowed imports |
| Forbidden patterns | 4/10 | "No @ts-nocheck", "No wildcard imports" | `grep` for pattern absence |
| Base class requirement | 1/10 | "Use CustomTestCase not unittest.TestCase" | AST check |
| Deprecated API | 1/10 | "Don't use check(), use retry()" | `grep` for deprecated call |

### Design decisions

- **Weight: 0.05-0.10 per test, <=0.15 total.** Config-derived tests are supplementary, not primary.
- **Oracle tolerance: >=0.95 acceptable.** Gold patches from real PRs sometimes don't pass the repo's own lint. A score of 0.95 (missing only the config test) is informative RL signal, not a test failure.
- **Target changed files only.** Pre-existing violations are not the agent's fault.
- **Convention:** source comments in test.sh with origin + file path + line range.

## Repos with multiple config files (reference)

| Repo | Config locations |
|------|-----------------|
| openclaw/openclaw | root, extensions/, src/channels/, src/plugins/, src/gateway/protocol/, docs/ |
| anomalyco/opencode | root, packages/app/, packages/opencode/, packages/desktop/, packages/desktop-electron/ |
| pytorch/pytorch | root, torch/_dynamo/ |
| huggingface/transformers | root, .ai/ |
| All others | Root only (single CLAUDE.md and/or AGENTS.md) |
