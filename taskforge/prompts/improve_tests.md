# Improve Tests

Upgrade tests in an existing agentmd-edit task from grep/structural to behavioral (code-executing) tests.

## Input

`$ARGUMENTS` = task name in `$TASK_DIR/` (e.g., `remix-add-charset-to-contenttype-for`)

## Problem

The task's `test_outputs.py` currently only reads files and checks strings (grep-only). These tests don't actually execute code, so they can't reliably distinguish between the base commit (broken) and a correct fix. We need behavioral tests that run the actual code.

## Steps

### 1. Read ALL task files

Read every file in `$TASK_DIR/$ARGUMENTS/`:
- `instruction.md` — what the task asks the agent to do
- `solution/solve.sh` — the gold patch (shows exactly what changed)
- `tests/test_outputs.py` — CURRENT tests (you will rewrite these)
- `eval_manifest.yaml` — check declarations (you will update to match)
- `environment/Dockerfile` — build environment (tells you what tools are available)

### 2. Fetch the PR diff

Read `task.toml` for `source_repo` and `source_pr`. If present:
```bash
gh pr diff <PR_NUMBER> --repo <REPO>
```
This shows you the exact changes. Understand:
- What functional behavior changed?
- What inputs trigger the old (broken) behavior?
- What is the correct output after the fix?

### 3. Understand the execution environment

From the Dockerfile, determine:
- **Language runtime**: node, python, rust, go, dotnet, etc.
- **Package manager**: npm, pnpm, yarn, pip, cargo, etc.
- **Test framework**: jest, vitest, pytest, cargo test, go test, etc.
- **Working directory**: usually `/workspace/<repo-name>`

### 4. Rewrite tests with code execution

**CRITICAL RULE**: At least ONE `fail_to_pass` test MUST use `subprocess.run()` to execute actual code. Grep-only tests are not acceptable for f2p checks.

#### For Node/TypeScript repos:

```python
import subprocess, json
from pathlib import Path

REPO = "/workspace/<repo-name>"

def _run_ts(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript/JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)

def test_core_behavior():
    """The function returns the correct result for the bug-triggering input."""
    r = _run_ts("""
import { targetFunction } from './src/module.js';
const result = targetFunction(bugTriggeringInput);
console.log(JSON.stringify(result));
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data == expectedValue
```

#### For Python repos:

```python
def test_core_behavior():
    """The function handles the edge case correctly."""
    r = subprocess.run(
        ["python3", "-c", """
from module import target_function
result = target_function(edge_case_input)
assert result == expected, f"Got {result}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
```

#### For Rust repos:

```python
def test_compilation():
    """Modified crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "--manifest-path", f"{REPO}/Cargo.toml"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Compile failed: {r.stderr}"
```

#### For Go repos:

```python
def test_go_vet():
    """Package passes go vet."""
    r = subprocess.run(
        ["go", "vet", "./..."],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"go vet failed: {r.stderr}"
```

### 5. Preserve config/structural tests

Keep existing pass_to_pass and agent_config tests if they are correct. Only rewrite the fail_to_pass tests that are grep-only.

If the task has `agent_config` checks with proper source refs, KEEP them.

### 6. Two-phase writing

**Phase 1 — Write ALL function signatures first:**
```python
def test_core_behavior():
    """Function returns correct result."""
    ...  # fill

def test_edge_case():
    """Handles empty input."""
    ...  # fill

def test_config_updated():
    """CLAUDE.md documents the change."""
    ...  # fill
```

**Phase 2 — Fill each body.** This prevents orphaned code blocks.

### 7. Update eval_manifest.yaml

Ensure every `def test_*()` function has a matching check in eval_manifest.yaml:
```yaml
checks:
  - id: test_core_behavior      # must match function name exactly
    type: fail_to_pass
    origin: pr_diff
    description: ...
```

### 8. Self-audit

Before finishing, verify:
1. `python3 -c "import ast; ast.parse(open('tests/test_outputs.py').read())"` — no syntax errors
2. At least ONE f2p test uses `subprocess.run()`
3. Every `def test_*()` has a matching check in eval_manifest.yaml
4. No `NotImplementedError`, no `{{` placeholders, no orphaned code
5. Source refs use base commit, not merge commit
6. `source.path` points to the config file with the rule, NOT the file being edited

## What NOT to do

- Do NOT rewrite the Dockerfile, instruction.md, or solve.sh
- Do NOT add new tests that test things outside the PR's scope
- Do NOT use `origin: config_edit` — valid origins are: `pr_diff`, `repo_tests`, `agent_config`, `static`
- Do NOT use `assert True` or `assert "string"` as real assertions
- Do NOT write tests that pass on both base and fix (those are useless f2p tests)
