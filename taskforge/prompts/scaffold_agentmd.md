# Scaffold AgentMD-Edit Task

Create a benchmark task from a GitHub PR that includes BOTH functional code changes AND agent config file updates (CLAUDE.md, AGENTS.md, README.md, SKILL.md, etc.).

The key difference from standard tasks: this PR updates agent instruction files alongside code. The task MUST test whether the agent makes the correct config/documentation update in addition to the code fix.

## Input

`$ARGUMENTS` = PR URL or `owner/repo#number` (e.g., `sgl-project/sglang#21471`).

## Steps

### 1. Fetch PR metadata

```bash
gh pr view <N> --repo <owner/repo> --json title,body,files,mergeCommit
gh api repos/<owner/repo>/commits/<merge_sha> --jq '.parents[0].sha'   # base commit
gh pr diff <N> --repo <owner/repo>                                      # full diff
```

### 2. Classify PR files into code vs config changes

Split the PR diff into two parts:
- **Code changes**: functional source code modifications
- **Config changes**: updates to agent config / documentation files

Agent config files include:
- `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `CONVENTIONS.md`
- `.cursorrules`, `.cursor/rules/`, `copilot-instructions.md`
- `.windsurfrules`, `.clinerules`, `.continuerules`, `.cody/`
- `README.md` (at any level)
- `CONTRIBUTING.md`

**IMPORTANT**: Both parts must be non-trivial. If the config change is just a version bump, date update, or trivial formatting, STOP and report: `SKIP: trivial config change`.

Understand:
1. What functional change does the code diff make?
2. What does the config/doc update say? Why was it needed alongside the code change?
3. How do they relate? (e.g., new feature → document new API, bug fix → update troubleshooting, refactor → update architecture docs, new lint rule → add to CLAUDE.md)

### 2b. Abandon check

After reading the PR metadata and diff, decide if this PR is suitable. **Abandon immediately** by writing this file and stopping:

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
- **No config edit**: PR doesn't actually change any agent instruction files (misclassified)
- **No testable behavior**: The change is purely visual (CSS, UI layout) with no programmatic way to verify

If the PR looks good, continue to step 3.

### 3. Discover and load ALL agent config files

This is critical — our benchmark tests how well agents follow repo instructions.

**Step 3a: Discover all agent instruction files at the base commit:**
```bash
gh api "repos/OWNER/REPO/git/trees/BASE_COMMIT?recursive=1" \
  --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md|CONVENTIONS\\.md|\\.cursorrules|\\.cursor/rules|copilot-instructions\\.md|\\.windsurfrules|\\.clinerules|\\.continuerules|\\.cody|\\.mdc$|\\.claude/rules/|\\.claude/skills/|\\.claude/agents/|README\\.md")) | .path'
```

**Priority**: Focus on Tier 1 files (CLAUDE.md, AGENTS.md, .claude/rules/, .claude/skills/, .cursorrules, CONVENTIONS.md). README.md is Tier 2 — only relevant if a Tier 1 rule references it.

**Step 3b: Fetch the FULL content of every config file found:**
```bash
gh api "repos/OWNER/REPO/contents/PATH?ref=BASE_COMMIT" --jq '.content' | base64 -d
```

Read completely — do NOT grep for snippets.

**Step 3c: Determine which configs apply:**
- Root-level configs → always apply
- Subdirectory configs → apply if PR touches files in that subtree
- `.claude/skills/*/SKILL.md` → apply if task matches the skill's domain

**Step 3d: Classify every rule in applicable configs:**
1. **Programmatic + relevant** → pytest check with `origin: agent_config` and `source` ref
2. **Soft/subjective + relevant** → `rubric` section of eval_manifest.yaml
3. **Irrelevant** (process, PR, commit, tooling rules) → skip

### 4. Copy template and fill placeholders

**IMPORTANT**: All task files MUST be created under `/workspace/task/`. This is the expected output location.

```bash
mkdir -p /workspace/task/{environment,solution,tests}
```

Create all files from scratch in `/workspace/task/` — there is no template to copy from.

Replace all `{{PLACEHOLDER}}` tokens across files.

### 5. Fill in the files (this order)

#### Dockerfile
- Choose base image with **exact tag** (NEVER `:latest`): `python:3.12-slim` / `node:22-slim` / `rust:1.85-slim`
- For non-Python repos, ensure `python3` is available (needed by pytest runner)
- Clone with `--filter=blob:none` (default) or `--depth=N` for large repos
- Install ONLY deps needed by test_outputs.py — no torch, no GPU libs
- **Every binary `test_outputs.py` invokes via `subprocess.run([...])` must
  be installed in the final image.** Enumerate them and verify via
  `docker run task-env command -v <binary>`. Linters like `ruff`, `black`,
  `mypy`, `isort`, `prettier`, `clippy`, `gofmt` are NOT implicit in most
  base images — `pip install` or `apt-get install` them explicitly.
  Rubric `test_deps_in_dockerfile` auto-rejects missing tools.
- Always `mkdir -p /logs/verifier`

#### solve.sh
- Paste the FULL gold patch into the HEREDOC — this MUST include BOTH code AND config file changes
- The gold patch must modify the agent config files too (README.md, CLAUDE.md, etc.)
- Set idempotency grep to a distinctive line from the patch
- Ensure `cd /workspace/{{REPO_SHORT}}` at the top
- **FORBIDDEN: external fetches.** Never `curl`/`wget`/`gh pr diff`/
  `git show <sha>`/`git fetch pull/N` the gold patch. Inline it as a
  HEREDOC. Rubric `oracle_no_external_fetch` auto-rejects this.

#### task.toml
- Set `name = "<repo-short>-<descriptive-slug>"` (e.g., `name = "playwright-chorecli-add-network-route"`)
- Set difficulty, tags, time estimates
- Add tag `agentmd-edit` to mark this as a config-edit task

#### test_outputs.py — THE CORE WORK

**CRITICAL STRUCTURAL RULE**: Every assertion MUST be inside a `def test_*():` function. NEVER write bare assertions, orphaned code blocks, or comments like `# [config_edit] fail_to_pass` without a complete function definition following them. Pytest only discovers `def test_*()` functions — anything else is dead code or causes SyntaxError.

This file has two categories of tests:

**Category 1: Code behavior tests (standard)**
- For non-Python repos: use `subprocess.run()` to execute the actual code. Python is the test harness, not the thing being tested.
- At least ONE f2p test MUST execute code (not just read files as text).

```python
# TypeScript: write a temp .ts file and run it with node
def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    script_path = Path(REPO) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)

def test_core_behavior():
    """Import the module and verify the fix works."""
    result = _run_ts("""
import { myFunction } from './src/lib/module.ts'
let out = myFunction("test-input")
console.log(JSON.stringify({ out }))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["out"] == "expected", f"Got: {data['out']}"

# Rust: compile and run
def test_cargo_check():
    r = subprocess.run(["cargo", "check"], cwd=REPO, capture_output=True, timeout=600)
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()}"

# Go: build and test
def test_go_build():
    r = subprocess.run(["go", "build", "./..."], cwd=REPO, capture_output=True, timeout=600)
    assert r.returncode == 0, f"Build failed:\n{r.stderr.decode()}"
```

**Category 2: Config/documentation update tests (REQUIRED)**
At least ONE test must verify the config file was updated correctly:

```python
def test_readme_documents_new_api():
    """README.md must document the new batch endpoint."""
    readme = Path(REPO) / "README.md"
    content = readme.read_text()
    assert "batch" in content.lower(), "README should mention batch endpoint"
    assert "/api/batch" in content or "/data/batch" in content, \
        "README should document the batch API path"

def test_agents_md_documents_new_module():
    """AGENTS.md must reference the new processing module."""
    agents_md = Path(REPO) / "src" / "AGENTS.md"
    content = agents_md.read_text()
    assert "processor" in content.lower(), \
        "AGENTS.md should document the new processor module"
```

**Design principles for config tests:**
1. **Check semantic content, not exact wording.** Check for key concepts, API names, file references.
2. **Be specific enough to fail on base commit.** Check for content genuinely added by the PR.
3. **Use multiple keywords/concepts.** Check 2-3 key terms, not just one word.
4. **Origin in eval_manifest.yaml**: Use `origin: agent_config` if driven by an existing rule. Use `origin: pr_diff` if just part of the PR. **Only valid origins: `pr_diff`, `repo_tests`, `agent_config`, `static`. Do NOT invent new values.**
5. **Source ref**: Points to **the config file with the rule** (e.g., AGENTS.md line 21), NOT the file being edited. Use the **base commit** (the rule existed before this PR). If `origin: pr_diff`, no source needed.

**Standard design principles:**
1. **Execute code, don't grep it.** At least one test must use `subprocess.run()` for non-Python repos. Reading a file as text and searching for strings is anti-pattern #3.
2. Fail-to-pass is primary
3. Vary inputs — never test with a single parameter value
4. Anti-stub: verify return values, not just "doesn't crash"
5. Upstream P2P if available

**10 anti-patterns to avoid** (same as regular tasks):

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

The template test.sh is standardized boilerplate. Do not add task-specific logic here.

**Hard rules (rubric `reward_is_pure_pytest`, auto-rejected):**
- Reward MUST go to `/logs/verifier/reward.txt` as literal `0` or `1`.
- Reward MUST derive from pytest's exit code (`$?`). No grep/awk/sed on
  pytest output. No `exit` before the `--- LLM Judge ---` block. No
  `|| true` on pytest or plugin installs.
- No JSON-valued reward (`{reward: 1.0, status: "success"}`).

#### eval_manifest.yaml

- Fill in source PR metadata
- One `check` entry per `def test_*` function in test_outputs.py (keep ids in sync)
- **REQUIRED**: At least one check that verifies the config/instruction file update
- Add `source` refs for all `agent_config` checks (pointing to the rule in CLAUDE.md/AGENTS.md, NOT the file being edited)
- Add rubric rules from agent config files. Every soft/subjective rule from CLAUDE.md, AGENTS.md, SKILL.md etc. that is relevant to this PR's changes MUST become a rubric entry with source ref. For agentmd-edit tasks, rubric MUST NOT be empty — extract at least 3-5 rules covering both code style and config/doc conventions.

```yaml
version: "2.0"

source:
  repo: "owner/repo"
  pr: 123
  base_commit: "abc123..."
  merge_commit: "def456..."

checks:
  # Standard code behavior checks
  - id: syntax_check
    type: pass_to_pass
    origin: static
    description: "Modified files parse without errors"

  - id: core_bug_fixed
    type: fail_to_pass
    origin: pr_diff
    description: "Primary behavioral fix verified"

  # Config/instruction file update checks (at least one required)
  # Case A: AGENTS.md has a rule requiring doc updates → agent_config
  - id: agents_md_documents_new_module
    type: fail_to_pass
    origin: agent_config
    description: "AGENTS.md updated to document the new processing module"
    source:
      path: "AGENTS.md"              # the config file with the rule
      lines: "15"                     # the line that says "document new modules"
      commit: "base_commit_sha"       # at base commit (rule existed before this PR)

  # Case B: PR updates a config file (no pre-existing rule mandates it) → pr_diff
  - id: claude_md_adds_lint_rule
    type: fail_to_pass
    origin: pr_diff
    description: "CLAUDE.md adds the new no-wildcard-imports lint rule"

  # Agent config compliance checks (agent follows existing rules while coding)
  - id: uses_let_not_var
    type: pass_to_pass
    origin: agent_config
    description: "Code uses let/const per AGENTS.md style rule"
    source:
      path: "AGENTS.md"
      lines: "30"
      commit: "base_commit_sha"

rubric:
  - rule: "Config update is consistent with the style of existing documentation"
    source:
      path: "README.md"
      lines: "1-10"
      commit: "base_commit_sha"
```

#### instruction.md — WRITE THIS LAST

By now you know exactly what test_outputs.py checks. Describe BOTH:
1. The **functional bug/feature** that needs code changes
2. The **documentation/config update** that should accompany the code change

The instruction should make it clear that updating the relevant config/doc files is part of the task. Use language like:
- "After fixing the code, update the relevant documentation to reflect the change."
- "The project's CLAUDE.md / README.md should be updated to document this new behavior."
- "Don't forget to update the agent instructions to cover this case."

But do NOT reveal exactly what to write — the agent should figure that out.

- Lead with what's broken/needed, not why
- Point to relevant file(s)
- Do NOT copy from the PR body, reveal patch details, or mention test files
- Some ambiguity is OK

### 6. Build Docker and discover repo CI/CD

**6a. Build the Docker image first:**
```bash
cd /workspace/task/environment && docker build -t task-env .
```
If it fails, fix the Dockerfile and retry until it builds.

**6b. Discover CI/CD commands.** From the Dockerfile WORKDIR, check:
- `package.json` → `scripts.test`, `scripts.lint`, `scripts.check`, `scripts.typecheck`, `scripts.build`
- `Makefile` / `Justfile` → test/lint/check targets
- `Cargo.toml` → `cargo test`, `cargo check`, `cargo clippy`
- `pyproject.toml` → pytest, ruff, mypy
- `go.mod` → `go test`, `go vet`
- `.github/workflows/*.yml` → actual CI commands

**6c. Test which commands work** inside the Docker container on the base commit:
```bash
docker run --rm task-env <command>
```
Only add commands that actually succeed on the base commit. Skip commands that require network access, GPU, or special accounts. When writing test timeouts, use what you observe — if a command takes 30s, set timeout=60; if it takes 200s, set timeout=600. Check `.github/workflows/` for the repo's own CI timeout settings as a reference.

**6d. Add p2p tests** for each working CI command and matching checks in eval_manifest.yaml.

### 7. Docker validation (REQUIRED)

The image is already built from step 6a. Now validate:

**7b. NOP test (base commit — expect reward=0):**
```bash
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh
cat /logs/verifier/reward.txt
```
Must be `0`. If `1`, your f2p tests are too weak — rewrite them.

**7c. Gold test (apply fix — expect reward=1):**
```bash
docker rm -f task-solved 2>/dev/null || true
docker run --name task-solved -v /workspace/task/solution:/solution:ro task-env bash /solution/solve.sh
docker commit task-solved task-env-gold
docker rm task-solved
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env-gold bash /tests/test.sh
cat /logs/verifier/reward.txt
```
Must be `1`. If `0`, read pytest output, fix solve.sh or tests, rebuild and retry.

**Keep iterating until NOP=0 and GOLD=1.**

### 8. Self-audit

After Docker validation passes:

1. **Source ref verification**: For every `agent_config` check, verify `source.path` EXISTS at `source.commit` (base commit). Source refs MUST use the base commit, not merge commit.
2. **Gold patch completeness**: solve.sh includes BOTH code and config changes.
3. **F2P coverage**: at least 2 f2p tests (at least 1 code + 1 config).
4. **P2P coverage**: at least 1 pass_to_pass test from repo CI/CD.
5. **Anti-pattern scan**: check each test against the 10 anti-patterns above.
6. **Manifest sync**: every `def test_*` has a matching check in eval_manifest.yaml.

```
Self-audit:
  Docker: NOP=0, GOLD=1
  Tests: N total (X f2p code, Y f2p config, Z p2p)
  CI/CD tests: [list commands added]
  Gold patch includes config changes: yes
  Source refs verified: yes
  Manifest sync: yes
```
