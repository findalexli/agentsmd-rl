# Scaffold Steps (Reference)

Detailed execution steps for creating a benchmark task from a GitHub PR.

## §1. Fetch PR metadata

```bash
gh pr view <N> --repo <owner/repo> --json title,body,files,mergeCommit
gh api repos/<owner/repo>/commits/<merge_sha> --jq '.parents[0].sha'   # base commit
gh pr diff <N> --repo <owner/repo>                                      # full diff
```

## §2. Discover and load ALL agent config files

**Step 2a: Discover all config files at the base commit:**
```bash
gh api "repos/OWNER/REPO/git/trees/BASE_COMMIT?recursive=1" \
  --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md|\\.cursorrules|\\.cursor/rules|copilot-instructions\\.md|\\.windsurfrules|\\.clinerules|\\.continuerules|\\.cody|CONVENTIONS\\.md|README\\.md")) | .path'
```

**Step 2b: Fetch the FULL content of every config file found:**
```bash
gh api "repos/OWNER/REPO/contents/PATH?ref=BASE_COMMIT" --jq '.content' | base64 -d
```

Read completely — do NOT grep for snippets. We need full context.

**Step 2c: Determine which configs apply:**
- Root-level configs (CLAUDE.md, AGENTS.md, .cursorrules) → always apply
- Subdirectory configs → apply if PR touches files in that subtree
- `.claude/skills/*/SKILL.md` → apply if task matches the skill's domain

**Step 2d: Classify every rule in applicable configs:**
1. **Programmatic + relevant** → pytest check with `origin: agent_config` and `source` ref
2. **Soft/subjective + relevant** → `rubric` section of eval_manifest.yaml
3. **Irrelevant** (process, PR, commit, tooling rules) → skip

## §3. Copy template and fill placeholders

```bash
TASK_NAME="<repo-short>-<descriptive-slug>"
cp -r taskforge/templates/task_template/ harbor_tasks/$TASK_NAME/
```

Replace all `{{PLACEHOLDER}}` tokens:

| Placeholder | Value |
|-------------|-------|
| `{{OWNER}}` | GitHub org/user |
| `{{REPO}}` | Repository name |
| `{{BASE_COMMIT}}` | Parent of merge commit |
| `{{MERGE_COMMIT}}` | Merge commit SHA |
| `{{PR_NUMBER}}` | PR number |
| `{{TASK_NAME}}` | Task slug |
| `{{PATCH_CONTENT}}` | Full gold patch diff |
| `{{DISTINCTIVE_LINE}}` | Unique string from the patch (for idempotency) |

## §4. Write files (this order)

### Dockerfile
- Base image: `python:3.12-slim` / `node:22-slim` / `rust:1.85-slim`
- For non-Python repos, ensure `python3` is available (needed by pytest runner)
- Clone with `--filter=blob:none` (default) or `--depth=N` for large repos
- Install ONLY deps needed by test_outputs.py
- Always `mkdir -p /logs/verifier`

### solve.sh
- Gold patch in HEREDOC (single-quoted `<<'PATCH'`)
- Idempotency grep for a distinctive line
- `cd /workspace/{{REPO_SHORT}}` at the top

### task.toml
- Set difficulty, tags, time estimates
- Adjust timeouts if needed (default: 1800s agent, 120s verifier)

### test_outputs.py
See [test-design.md](../scaffold-task/test-design.md) for the full design guide.

### test.sh — DO NOT MODIFY
Standardized boilerplate. Installs pytest, runs test_outputs.py, writes binary reward.

### eval_manifest.yaml
- One `check` entry per `def test_*` function (keep ids in sync)
- Add `source` refs for all `agent_config` checks
- Add rubric rules or leave empty `[]`

### instruction.md — WRITE THIS LAST
- Lead with what's broken, not why
- Point to relevant file(s) and function(s)
- Do NOT copy from PR body, reveal patch details, or mention test files
- Some ambiguity is OK

## §5. Self-audit

```
Self-audit:
  Tests: N total (X f2p, Y p2p)
  Stub score: 0 (all must fail on stub)
  Alternative fix passes: yes
  Anti-patterns: none
  Manifest sync: yes
```
