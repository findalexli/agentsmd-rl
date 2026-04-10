# Enrich Pass-to-Pass Tests

Add the repo's actual CI/CD tests as pass_to_pass gates in an existing task's test_outputs.py.

## Context

Read `/workspace/task/status.json` if it exists — the `nodes` section has notes from previous steps. Update the `p2p_enrichment` node in status.json when done with what CI commands you found and what tests you added.

## Input

- Task directory at `/workspace/task/` with all files.
- **The full repo is cloned at `/workspace/repo/`** at the base commit. You can browse source code, test files, and CI configs here.

**IMPORTANT — Two different repo paths:**
- `/workspace/repo/` — the repo in YOUR sandbox. Use this to BROWSE code, find test files, read CI configs. Do NOT reference this path in test_outputs.py.
- The Docker-internal path (e.g., `/workspace/gradio`, `/workspace/bun`) — this is where the repo lives INSIDE the Docker container. Check the Dockerfile's `WORKDIR` to find it. The `REPO` variable in test_outputs.py MUST use this Docker-internal path, NOT `/workspace/repo/`.

## Goal

Following the SWE-bench approach: select a **curated subset** of the repo's existing tests that cover the modified code. Don't run the full CI — find the 3-10 most relevant test functions and import them as pass_to_pass gates.

## Steps

### 1. Read the task files

Read these files from `/workspace/task/`:
- `tests/test_outputs.py` — current tests
- `eval_manifest.yaml` — current checks
- `environment/Dockerfile` — tells you what repo, commit, and tooling is available
- `solution/solve.sh` — the gold patch

### 2. Build the Docker image

```bash
cd /workspace/task/environment && docker build -t task-env .
```
If it fails, read the error but do NOT modify the Dockerfile — just note the failure in status.json and stop. The validate agent will fix Docker issues later.

### 3. Browse the repo to find relevant tests

**The repo is at `/workspace/repo/`.** This is your primary resource. Explore it:

**3a. Find which files the PR modifies** (from solve.sh):
```bash
grep -oP '(?:^diff --git a/)(\S+)' /workspace/task/solution/solve.sh | sort -u
# or: look at the patch paths in solve.sh
```

**3b. Find existing test files that cover the modified code:**
```bash
# For Python repos
find /workspace/repo -name "test_*.py" -o -name "*_test.py" | head -20
# For JS/TS repos
find /workspace/repo -name "*.test.ts" -o -name "*.test.js" -o -name "*.spec.ts" | head -20
# For Rust repos
find /workspace/repo -name "*.rs" -path "*/tests/*" | head -20
# For Go repos
find /workspace/repo -name "*_test.go" | head -20
```

**3c. Read the test files** that are most relevant to the modified code. Look for test functions that exercise the changed functions/modules.

**3d. Check CI configuration:**
- `.github/workflows/*.yml` — what commands does CI actually run?
- `package.json` scripts, `Makefile` targets, `pyproject.toml` tool configs
- `Cargo.toml`, `go.mod`, etc.

### 4. Test which CI commands ACTUALLY WORK inside Docker

**CRITICAL: You must actually run each command inside Docker, not just read about it.**

For each discovered command, test it:
```bash
docker run --rm task-env bash -c "<command> 2>&1; echo EXIT:$?"
```

Record the exit code and output. Only add commands that exit 0.

Skip commands that:
- Require network access at runtime (downloading models, npm publish)
- Require GPU/special hardware
- Need credentials (AWS, API keys)

**DO NOT write file-read/regex tests and label them `repo_tests`.** A p2p test with `origin: repo_tests` MUST use `subprocess.run()` to execute an actual command that the repo's CI runs. Reading a file and checking for patterns is `origin: static`, not `origin: repo_tests`.

### 5. Add p2p tests — MUST be subprocess.run() commands

**Every p2p test with `origin: repo_tests` MUST call subprocess.run() with a real command.**

Good examples (actually run repo CI):
```python
def test_repo_lint():
    """Repo's linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "src/"], capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"

def test_repo_typecheck():
    """TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"], capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"

def test_repo_unit_tests():
    """Repo's unit tests for modified module pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_utils.py", "-x"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr[-500:]}"

def test_repo_cargo_check():
    """Rust compilation succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--manifest-path", f"{REPO}/Cargo.toml"],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-500:]}"
```

**BAD examples (DO NOT do this — these are file reads, not CI commands):**
```python
# BAD: reading file content is NOT a repo_tests check
def test_repo_no_tabs():
    content = Path(f"{REPO}/src/file.py").read_text()
    assert "\t" not in content  # This is origin: static, NOT repo_tests

# BAD: checking file existence is NOT a repo_tests check  
def test_repo_structure():
    assert Path(f"{REPO}/src/main.py").exists()  # This is origin: static
```

If a file-read check is genuinely useful, use `origin: static` or `origin: agent_config`, NOT `origin: repo_tests`.

### 6. For compiled-language repos where full build is infeasible

If the repo is C++/Zig/Rust and full compilation takes >10 min, look for lightweight CI checks:
- `clang-format --check` or `clang-tidy` on changed files
- `cargo fmt --check` or `cargo clippy` on the crate
- `zig fmt` on changed .zig files
- Python CI tooling (many C++ repos have Python CI scripts)
- `black --check`, `ruff check`, `mypy` on Python CI code
- Shell script linting (`shellcheck`)

Run these inside Docker and add as p2p tests. Even one real CI command is better than 10 file-read checks.

### 7. Update eval_manifest.yaml

Add matching checks for each new p2p test:
```yaml
  - id: test_repo_lint
    type: pass_to_pass
    origin: repo_tests      # ONLY use this if the test runs a real command
    description: Repo's linter passes

  - id: test_no_tabs
    type: pass_to_pass
    origin: static           # Use this for file-content checks
    description: No tab characters in source
```

### 8. Verify

After adding p2p tests, verify they pass on the base commit:
```bash
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh
cat /logs/verifier/reward.txt
```
Reward must be `1`. If any p2p test fails, either fix it or remove it.

## What NOT to do

- Do NOT modify the Dockerfile, instruction.md, or solve.sh
- Do NOT remove existing fail_to_pass tests
- Do NOT add tests that only pass after the fix (those are f2p, not p2p)
- Do NOT add tests that require internet/GPU/special accounts
- Do NOT label file-read/regex checks as `origin: repo_tests` — use `origin: static` instead
- Do NOT pad with redundant tests (3 good CI tests > 20 file-existence checks)
- If the full test suite is very slow, pick the relevant subset for the modified files
