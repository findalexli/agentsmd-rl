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

### 1b. Abandon check

After reading the PR metadata and diff, decide if this PR is suitable for a benchmark task. **Abandon immediately** by writing this file and stopping:

```bash
echo '{"abandoned": true, "reason": "your reason"}' > /workspace/task/status.json
```

Abandon if ANY of these apply:
- **Docs/CI only**: PR only changes markdown, workflows, configs with no functional code
- **Too large**: PR touches >10 files or >500 lines of functional code changes
- **Needs secrets/accounts**: Requires API keys, OAuth tokens, cloud accounts, or paid services
- **Needs GPU/special hardware**: CUDA kernels, model weights, TPU, etc. that can't be tested on CPU
- **Repo deleted/archived**: Can't clone or checkout the base commit
- **Trivial rename/typo**: One-line change with no behavioral difference to test
- **Reverted PR**: The merge commit was later reverted
- **No testable behavior**: The change is purely visual (CSS, UI layout) with no programmatic way to verify

If the PR looks good, continue to step 2.

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

**IMPORTANT**: All task files MUST be created under `/workspace/task/`. This is the expected output location.

```bash
mkdir -p /workspace/task/{environment,solution,tests}
```

Create all files from scratch in `/workspace/task/` — there is no template to copy from.

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
- Set `name = "<repo-short>-<descriptive-slug>"` (e.g., `name = "ruff-dedent-formfeed-strip"`)
- Set difficulty, tags, time estimates

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
    r = subprocess.run(["cargo", "check"], cwd=REPO, capture_output=True, timeout=600)
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
- Add rubric rules from agent config files. Every soft/subjective rule from CLAUDE.md, AGENTS.md, SKILL.md etc. that is relevant to this PR's changes MUST become a rubric entry with source ref. If the repo has agent configs, the rubric section MUST NOT be empty — extract at least 2-3 rules. Only leave `rubric: []` if the repo has NO agent config files at all.

#### instruction.md — WRITE THIS LAST

By now you know exactly what test_outputs.py checks. Describe the *symptom* those tests capture.

- Lead with what's broken, not why
- Point to relevant file(s) and function(s)
- Do NOT copy from the PR body, reveal patch details, or mention test files
- Some ambiguity is OK — the agent should explore
- Delete the HTML comment guidelines before finishing

### 5. Build Docker and discover repo CI/CD

**5a. Build the Docker image first:**
```bash
cd /workspace/task/environment && docker build -t task-env .
```
If it fails, fix the Dockerfile and retry until it builds.

**5b. Discover CI/CD commands.** From the Dockerfile WORKDIR, check:
- `package.json` → `scripts.test`, `scripts.lint`, `scripts.check`, `scripts.typecheck`, `scripts.build`
- `Makefile` / `Justfile` → test/lint/check targets
- `Cargo.toml` → `cargo test`, `cargo check`, `cargo clippy`
- `pyproject.toml` → pytest, ruff, mypy
- `go.mod` → `go test`, `go vet`
- `.github/workflows/*.yml` → actual CI commands

**5c. Test which commands work** inside the Docker container on the base commit:
```bash
docker run --rm task-env <command>
```
Only add commands that actually succeed on the base commit. Skip commands that require network access, GPU, or special accounts. When writing test timeouts, use what you observe — if a command takes 30s, set timeout=60; if it takes 200s, set timeout=600. Check `.github/workflows/` for the repo's own CI timeout settings as a reference.

**5d. Add p2p tests** to test_outputs.py for each working CI command:
```python
def test_repo_lint():
    """Repo's linter passes (pass_to_pass)."""
    r = subprocess.run(["npm", "run", "lint"], capture_output=True, text=True, timeout=600, cwd=REPO)
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"
```

**5e. Add matching checks** in eval_manifest.yaml:
```yaml
  - id: test_repo_lint
    type: pass_to_pass
    origin: repo_tests
    description: Repo's linter passes
```

### 6. Docker validation (REQUIRED)

The image is already built from step 5a. Now validate:

**6b. NOP test (base commit — expect reward=0):**
```bash
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh
cat /logs/verifier/reward.txt
```
Must be `0`. If `1`, your f2p tests are too weak — they pass even without the fix. Rewrite them.

**6c. Gold test (apply fix — expect reward=1):**
```bash
docker rm -f task-solved 2>/dev/null || true
docker run --name task-solved -v /workspace/task/solution:/solution:ro task-env bash /solution/solve.sh
docker commit task-solved task-env-gold
docker rm task-solved
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env-gold bash /tests/test.sh
cat /logs/verifier/reward.txt
```
Must be `1`. If `0`, read the pytest output (`-v --tb=short`), fix solve.sh or tests, rebuild and retry.

**Keep iterating until NOP=0 and GOLD=1.** Do not finish without passing both.

### 7. Self-audit

After Docker validation passes:

1. **Anti-pattern scan**: check each test against the 10 anti-patterns above.
2. **Manifest sync**: every `def test_*` has a matching check in eval_manifest.yaml.
3. **P2P coverage**: at least 1 pass_to_pass test from repo CI/CD.
4. **F2P coverage**: at least 2 fail_to_pass tests that fail on base commit.

```
Self-audit:
  Docker: NOP=0, GOLD=1
  Tests: N total (X f2p, Y p2p)
  CI/CD tests: [list commands added]
  Anti-patterns: none
  Manifest sync: yes
```
