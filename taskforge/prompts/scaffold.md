# Scaffold Task

Create a benchmark task from a GitHub PR. Copies `templates/task/` → `harbor_tasks/<task-name>/`, then fills in placeholders.

## Input

`$ARGUMENTS` = PR URL or `owner/repo#number` (e.g., `sgl-project/sglang#21471`).

## Steps

### 1. Fetch PR metadata

```bash
gh pr view <N> --repo <owner/repo> --json title,body,files,mergeCommit
gh api repos/<owner/repo>/commits/<merge_sha> --jq '.parents[0].sha'   # base commit
gh pr diff <N> --repo <owner/repo>                                      # full diff
```

### 2. Discover and load ALL agent config files

This is critical — our benchmark tests how well agents follow repo instructions.

**Step 2a: Discover all config files at the base commit:**
```bash
gh api "repos/OWNER/REPO/git/trees/BASE_COMMIT?recursive=1" \
  --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md|\\.cursorrules|\\.cursor/rules|copilot-instructions\\.md|\\.windsurfrules|\\.clinerules|\\.continuerules|\\.cody|CONVENTIONS\\.md|README\\.md")) | .path'
```

**Step 2b: Fetch the FULL content of every config file found:**
```bash
gh api "repos/OWNER/REPO/contents/PATH?ref=BASE_COMMIT" --jq '.content' | base64 -d
```

Read completely — do NOT grep for snippets. We need full context to find all rules, not just keyword matches.

**Step 2c: Determine which configs apply:**
- Root-level configs (CLAUDE.md, AGENTS.md, .cursorrules) → always apply
- Subdirectory configs → apply if PR touches files in that subtree
- `.claude/skills/*/SKILL.md` → apply if task matches the skill's domain

**Step 2d: Classify every rule in applicable configs:**
1. **Programmatic + relevant** → pytest check with `origin: agent_config` and `source` ref
2. **Soft/subjective + relevant** → `rubric` section of eval_manifest.yaml
3. **Irrelevant** (process, PR, commit, tooling rules) → skip
4. **Trivially vague** ("follow existing style" without specifics) → skip

Aim for **more rules rather than fewer** — better to include a borderline rule than miss a relevant one.

### 3. Copy template and fill placeholders

```bash
TASK_NAME="<repo-short>-<descriptive-slug>"
cp -r taskforge/templates/task_template/ harbor_tasks/$TASK_NAME/
```

Replace all `{{PLACEHOLDER}}` tokens across files:

| Placeholder | Value |
|-------------|-------|
| `{{OWNER}}` | GitHub org/user |
| `{{REPO}}` | Repository name |
| `{{REPO_SHORT}}` | Short repo name (for paths) |
| `{{BASE_COMMIT}}` | Parent of merge commit |
| `{{MERGE_COMMIT}}` | Merge commit SHA |
| `{{PR_NUMBER}}` | PR number |
| `{{TASK_NAME}}` | Task slug |
| `{{TASK_TITLE}}` | Human-readable title |
| `{{TARGET_FILE}}` | Primary file(s) the PR modifies |
| `{{DISTINCTIVE_LINE}}` | Unique string from the patch (for idempotency) |
| `{{PATCH_CONTENT}}` | Full gold patch diff |
| `{{CONFIG_FILE}}`, `{{LINES}}`, `{{COMMIT}}` | Agent config source refs |

### 4. Fill in the files (this order)

#### Dockerfile
- Choose base image: `python:3.12-slim` / `node:22-slim` / `rust:1.85-slim`
- For non-Python repos, ensure `python3` is available (needed by pytest runner)
- Clone with `--filter=blob:none` (default) or `--depth=N` for large repos
- Install ONLY deps needed by test_outputs.py — no torch, no GPU libs
- Always `mkdir -p /logs/verifier`

#### solve.sh
- Paste the gold patch into the HEREDOC (single-quoted `<<'PATCH'`)
- Set idempotency grep to a distinctive line from the patch
- Ensure `cd /workspace/{{REPO_SHORT}}` at the top

#### task.toml
- Set difficulty, tags, time estimates
- Adjust timeouts if needed (default: 1800s agent, 120s verifier)

#### test_outputs.py — THE CORE WORK

Replace each `raise NotImplementedError(...)` placeholder with real tests. Every `def test_*` function maps 1:1 to a check in eval_manifest.yaml.

**Design principles:**

1. **Call code, don't inspect it.** Import the function, call it with bug-triggering input, assert the result. AST is a last resort (only for GPU kernels, CUDA C++, or code needing unavailable model weights).

2. **Fail-to-pass is primary.** Each f2p test MUST fail on the base commit and pass on a correct fix. Test the *behavior*, not the *structure*.

3. **Vary inputs.** Never test with a single parameter value — agents hardcode constants.

4. **Anti-stub.** Verify return values, not just "doesn't crash". `assert result == expected`, not `assert result is not None`.

5. **Upstream P2P.** If the repo has pytest/jest/vitest tests that run on CPU, include them. Don't invent fake regression tests.

6. **For non-Python repos:** Use `subprocess.run()` to compile/run/test. Python is the universal test harness.

```python
# Rust example
def test_cargo_check():
    r = subprocess.run(["cargo", "check"], cwd=REPO, capture_output=True, timeout=120)
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()}"

# Node example
def test_build():
    r = subprocess.run(["node", "-e", "require('./dist/index.js')"], cwd=REPO, capture_output=True)
    assert r.returncode == 0
```

**10 anti-patterns to avoid:**

| # | Pattern | Fix |
|---|---------|-----|
| 1 | Self-referential constant extraction | Compare against ground-truth values |
| 2 | Import fallback to AST | Import fails = test fails |
| 3 | Grep-only frontend tests | Execute functions, not grep |
| 4 | Stub-passable tests | Assert return values |
| 5 | Superficial guard checks | Assert state CHANGED |
| 6 | Single parameter value | Vary across multiple values |
| 7 | Ungated structural tests | Gate behind behavioral pass |
| 8 | Compilation-ungated structural | Gate behind syntax check |
| 9 | Keyword stuffing | Check coherence |
| 10 | File-exists fallback | No existence checks for points |

#### test.sh — DO NOT MODIFY

The template test.sh is standardized boilerplate. It installs pytest, runs test_outputs.py, and writes binary reward. Do not add task-specific logic here.

#### eval_manifest.yaml

- Fill in source PR metadata
- One `check` entry per `def test_*` function in test_outputs.py (keep ids in sync)
- Add `source` refs for all `agent_config` checks
- Add rubric rules (soft, LLM-judge-only) or leave empty `[]`
- Repos with NO agent configs: remove the agent_config check and rubric section

#### instruction.md — WRITE THIS LAST

By now you know exactly what test_outputs.py checks. Describe the *symptom* those tests capture.

- Lead with what's broken, not why
- Point to relevant file(s) and function(s)
- Do NOT copy from the PR body, reveal patch details, or mention test files
- Some ambiguity is OK — the agent should explore
- Delete the HTML comment guidelines before finishing

### 5. Self-audit

After filling all files, verify:

1. **Stub walk**: mentally run every test with `def f(): pass`. All must fail → reward 0.
2. **Alternative fix**: think of a different valid implementation. Does it pass all tests? If not, the test is too narrow — fix it.
3. **F2P coverage**: at least 2 tests must fail on the base commit.
4. **Anti-pattern scan**: check each test against the 10 anti-patterns above.
5. **Manifest sync**: every `def test_*` has a matching check in eval_manifest.yaml.

```
Self-audit:
  Tests: N total (X f2p, Y p2p)
  Stub score: 0 (all must fail on stub)
  Alternative fix passes: yes
  Anti-patterns: none
  Manifest sync: yes
```
