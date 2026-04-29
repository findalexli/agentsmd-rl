# Rubric Audit Findings (2026-03-29)

Audit of all 106 task rubrics for source-path accuracy and the case for adding config-derived programmatic tests.

## Batch-generated rubrics have systematic errors

Rubric YAMLs are the most error-prone artifact in overnight parallel-subagent task generation. Agents produce plausible-looking source references that don't survive verification.

| Error type | Count | Example |
|---|---:|---|
| Bare filename in multi-config repo | 12 | `"CLAUDE.md"` in openclaw (which has 20 `CLAUDE.md` files) |
| Wrong line numbers | ~30 | `lines: [82, 82]` when the rule is at line 8 |
| File doesn't exist at cited commit | 6 | `extensions/CLAUDE.md` cited before it was created |
| Hallucinated rules | 7 | "kumquat" rule at line 63 of a 49-line file |
| Invalid field names | ~10 | `section: "Useful commands"` instead of `lines: [N, M]` |
| Missing commit field | ~15 | `source.commit` omitted entirely |

Root causes:

| # | Cause |
|---|---|
| 1 | **Agents extrapolate from HEAD.** They read current repo state and assume it was the same at base commit. Files get added, lines shift, rules change. |
| 2 | **Line numbers are guessed.** No agent fetched the file and counted; they estimate from section headers. |
| 3 | **Multi-config repos are novel.** Training data rarely has `CLAUDE.md` in 10+ subdirectories — agents default to the simplest path. |

## Solution: three-step verification

```
1. Enumerate    →  gh api .../git/trees/COMMIT?recursive=1   (find ALL config files)
2. Fetch        →  gh api .../contents/PATH?ref=COMMIT       (read content at commit)
3. Validate     →  CI script: file exists, lines match rule.text  [TODO]
```

Concrete commands:

```bash
# 1. Enumerate
gh api "repos/OWNER/REPO/git/trees/BASE_COMMIT?recursive=1" \
  --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md")) | .path'

# 2. Fetch + verify
gh api "repos/OWNER/REPO/contents/PATH?ref=COMMIT" --jq '.content' | base64 -d
```

Step 3 is the missing piece — automated CI that, for each rubric rule, checks `source.file` exists at `source.commit` and `source.lines` contain text matching `rule.text`.

## Config-derived programmatic tests

Rules from agent config files that can be verified by a shell command rather than an LLM judge.

| Category | Repos | Example rule | Verification |
|---|---:|---|---|
| Formatter / linter | 8/10 | "Run ruff format" | `ruff check --select I FILE` |
| Type checker | 5/10 | "Run make typing" | `make typing` |
| Import boundary | 2/10 | "Extensions must import from `plugin-sdk/*`" | `grep` for disallowed imports |
| Forbidden patterns | 4/10 | "No `@ts-nocheck`", "No wildcard imports" | `grep` for pattern absence |
| Base class requirement | 1/10 | "Use `CustomTestCase` not `unittest.TestCase`" | AST check |
| Deprecated API | 1/10 | "Don't use `check()`, use `retry()`" | `grep` for deprecated call |

### Design decisions

| Decision | Value | Rationale |
|---|---|---|
| Per-test weight | 0.05–0.10, ≤ 0.15 total | Supplementary, not primary signal |
| Oracle tolerance | ≥ 0.95 acceptable | Real-PR gold patches sometimes don't pass repo's own lint; 0.95 is informative RL signal, not failure |
| Scope | Changed files only | Pre-existing violations aren't the agent's fault |
| Convention | Source comments in `test.sh` | Origin + file path + line range traceable from the test |

## Repos with multiple config files

| Repo | Config locations |
|---|---|
| openclaw/openclaw | root, `extensions/`, `src/channels/`, `src/plugins/`, `src/gateway/protocol/`, `docs/` |
| anomalyco/opencode | root, `packages/app/`, `packages/opencode/`, `packages/desktop/`, `packages/desktop-electron/` |
| pytorch/pytorch | root, `torch/_dynamo/` |
| huggingface/transformers | root, `.ai/` |
| All others | Root only |
