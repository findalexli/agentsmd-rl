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

```bash
TASK_NAME="<repo-short>-<descriptive-slug>"
cp -r taskforge/templates/task_template/ harbor_tasks_agentmd_edits/$TASK_NAME/
```

Replace all `{{PLACEHOLDER}}` tokens across files.

### 5. Fill in the files (this order)

#### Dockerfile
- Choose base image: `python:3.12-slim` / `node:22-slim` / `rust:1.85-slim`
- For non-Python repos, ensure `python3` is available (needed by pytest runner)
- Clone with `--filter=blob:none` (default) or `--depth=N` for large repos
- Install ONLY deps needed by test_outputs.py — no torch, no GPU libs
- Always `mkdir -p /logs/verifier`

#### solve.sh
- Paste the FULL gold patch into the HEREDOC — this MUST include BOTH code AND config file changes
- The gold patch must modify the agent config files too (README.md, CLAUDE.md, etc.)
- Set idempotency grep to a distinctive line from the patch
- Ensure `cd /workspace/{{REPO_SHORT}}` at the top

#### task.toml
- Set difficulty, tags, time estimates
- Add tag `agentmd-edit` to mark this as a config-edit task
- Adjust timeouts if needed

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
    r = subprocess.run(["cargo", "check"], cwd=REPO, capture_output=True, timeout=120)
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()}"

# Go: build and test
def test_go_build():
    r = subprocess.run(["go", "build", "./..."], cwd=REPO, capture_output=True, timeout=120)
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

#### eval_manifest.yaml

- Fill in source PR metadata
- One `check` entry per `def test_*` function in test_outputs.py (keep ids in sync)
- **REQUIRED**: At least one check that verifies the config/instruction file update
- Add `source` refs for all `agent_config` checks (pointing to the rule in CLAUDE.md/AGENTS.md, NOT the file being edited)
- Add rubric rules (soft, LLM-judge-only) or leave empty `[]`

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

### 6. Self-audit

After filling all files, verify:

1. **Python validity**: Run `python3 -c "import ast; ast.parse(open('test_outputs.py').read())"` mentally. Every assertion is inside a `def test_*():`. No orphaned code blocks, no bare assertions, no raw non-Python code pasted into the file.
2. **Subprocess check**: At least one f2p test uses `subprocess.run()` to execute the actual code (not just read files as text). Exception: pure Python repos can import directly.
3. **Stub walk**: mentally run every test with `def f(): pass`. All must fail → reward 0.
4. **F2P coverage**: at least 2 tests must fail on the base commit (at least 1 code + 1 config).
5. **Gold patch completeness**: solve.sh includes BOTH code and config changes.
6. **Anti-pattern scan**: check each test against the 10 anti-patterns above.
7. **Manifest sync**: every `def test_*` has a matching check in eval_manifest.yaml. No extra, no missing.
8. **Source ref verification**: For every `agent_config` check, verify the `source.path` file actually EXISTS at the `source.commit` (base commit). Run mentally: `gh api repos/OWNER/REPO/contents/PATH?ref=COMMIT`. If the file doesn't exist, the ref is fabricated — change origin to `pr_diff` or find the correct file. Source refs MUST use the **base commit** (not merge commit) — the rule must have existed before this PR.

```
Self-audit:
  Python valid: yes (no orphaned blocks, no bare assertions)
  Subprocess tests: N (for non-Python: _run_ts, cargo check, etc.)
  Tests: N total (X f2p code, Y f2p config, Z p2p)
  Stub score: 0 (all must fail on stub)
  Gold patch includes config changes: yes
  Anti-patterns: none
  Manifest sync: yes
  Source refs verified: yes (all agent_config paths exist at base commit)
```
