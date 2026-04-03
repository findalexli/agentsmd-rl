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

**Step 3a: Discover all config files at the base commit:**
```bash
gh api "repos/OWNER/REPO/git/trees/BASE_COMMIT?recursive=1" \
  --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md|\\.cursorrules|\\.cursor/rules|copilot-instructions\\.md|\\.windsurfrules|\\.clinerules|\\.continuerules|\\.cody|CONVENTIONS\\.md|README\\.md|CONTRIBUTING\\.md")) | .path'
```

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

This file has two categories of tests:

**Category 1: Code behavior tests (standard)**
- Same as regular tasks: call code, assert behavior, fail-to-pass
- These test the functional code change

**Category 2: Config/documentation update tests (NEW — REQUIRED)**
At least ONE test must verify the config file was updated correctly. These tests check that the agent made the right documentation/config edit. Examples:

```python
def test_readme_documents_new_api():
    """README.md must document the new batch endpoint."""
    readme = Path(REPO) / "README.md"
    content = readme.read_text()
    # Check the key content was added, not exact wording
    assert "batch" in content.lower(), "README should mention batch endpoint"
    assert "/api/batch" in content or "/data/batch" in content, \
        "README should document the batch API path"

def test_claude_md_updates_lint_rule():
    """CLAUDE.md must include the new no-wildcard-imports rule."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    assert "wildcard" in content.lower() or "import *" in content, \
        "CLAUDE.md should document the no-wildcard-imports rule"

def test_agents_md_documents_new_module():
    """AGENTS.md must reference the new processing module."""
    agents_md = Path(REPO) / "src" / "AGENTS.md"
    content = agents_md.read_text()
    assert "processor" in content.lower(), \
        "AGENTS.md should document the new processor module"
```

**Design principles for config tests:**
1. **Check semantic content, not exact wording.** The agent might phrase things differently — that's fine. Check for key concepts, API names, file references.
2. **Be specific enough to fail on base commit.** The test must fail before the config update and pass after. Check for content that was genuinely added by the PR.
3. **Don't check formatting/structure.** Check that the right information is present, not where exactly it appears.
4. **Use multiple keywords/concepts.** Check 2-3 key terms that the update should contain, not just one word.
5. **Mark origin as `config_edit` in eval_manifest.yaml** — this is a new origin type for this dataset.

**Standard design principles (same as regular tasks):**
1. Call code, don't inspect it (for code tests)
2. Fail-to-pass is primary
3. Vary inputs
4. Anti-stub: verify return values
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
- **REQUIRED**: At least one check with `origin: config_edit` for the config file update test
- Add `source` refs for all `agent_config` and `config_edit` checks
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

  # Config file update checks (NEW - at least one required)
  - id: readme_documents_new_feature
    type: fail_to_pass
    origin: config_edit
    description: "README.md updated to document the new batch API"
    source:
      path: "README.md"
      lines: "45-52"
      commit: "merge_commit_sha"  # use merge commit since this is what was added

  # Agent config compliance checks (from existing configs)
  - id: no_wildcard_imports
    type: pass_to_pass
    origin: agent_config
    source:
      path: "CLAUDE.md"
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

1. **Stub walk**: mentally run every test with `def f(): pass`. All must fail → reward 0.
2. **Alternative fix**: think of a different valid implementation. Does it pass all tests? If not, the test is too narrow — fix it.
3. **F2P coverage**: at least 2 tests must fail on the base commit (at least 1 code + 1 config).
4. **Config test**: at least 1 test checks the config file update. It MUST fail on base commit.
5. **Gold patch completeness**: solve.sh includes BOTH code and config changes.
6. **Anti-pattern scan**: check each test against the 10 anti-patterns above.
7. **Manifest sync**: every `def test_*` has a matching check in eval_manifest.yaml.

```
Self-audit:
  Tests: N total (X f2p code, Y f2p config, Z p2p)
  Config tests: N (checking: FILE1, FILE2)
  Stub score: 0 (all must fail on stub)
  Alternative fix passes: yes
  Gold patch includes config changes: yes
  Anti-patterns: none
  Manifest sync: yes
```
