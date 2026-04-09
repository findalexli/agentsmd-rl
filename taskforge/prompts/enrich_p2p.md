# Enrich Pass-to-Pass Tests

Add the repo's actual CI/CD tests as pass_to_pass gates in an existing task's test_outputs.py.

## Context

Read `/workspace/task/status.json` if it exists — the `nodes` section has notes from previous steps. Update the `p2p_enrichment` node in status.json when done with what CI commands you found and what tests you added.

## Input

Task directory at `/workspace/task/` with all files.

## Goal

The repo has its own CI/CD pipeline (tests, lints, typechecks, builds) that run before any PR is merged. Our benchmark task should verify that those CI/CD checks pass on BOTH the base commit AND after the gold fix. This ensures candidate solutions don't break existing functionality.

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

### 3. Discover the repo's CI/CD

From the Dockerfile, find the repo's WORKDIR. Then check:
- `package.json` → `scripts.test`, `scripts.lint`, `scripts.check`, `scripts.typecheck`, `scripts.build`
- `Makefile` / `Justfile` → test/lint/check targets
- `Cargo.toml` → `cargo test`, `cargo check`, `cargo clippy`
- `pyproject.toml` → pytest config, ruff, mypy
- `go.mod` → `go test`, `go vet`
- `.github/workflows/*.yml` → actual CI commands

### 4. Test which CI commands work

For each discovered command, run it inside the Docker container:
```bash
docker run --rm task-env <command>
```
Only add commands that actually succeed on the base commit. Skip commands that:
- Require network access (download models, npm publish)
- Take >120 seconds
- Require GPU/special hardware
- Are flaky (check if they pass consistently)

### 5. Add p2p tests to test_outputs.py

For each working CI command, add a `pass_to_pass` test:

```python
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"
```

If the repo has a large test suite, run only the relevant subset:
```python
def test_repo_tests_relevant():
    """Tests for modified module pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "jest", "--testPathPattern", "src/module-name"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr[-500:]}"
```

### 6. Update eval_manifest.yaml

Add matching checks for each new p2p test:
```yaml
  - id: test_repo_typecheck
    type: pass_to_pass
    origin: repo_tests
    description: Repo's TypeScript typecheck passes
```

### 7. Verify

After adding p2p tests, verify they pass on the base commit:
```bash
rm -f /logs/verifier/reward.txt
docker run --rm -v /workspace/task/tests:/tests:ro -v /logs/verifier:/logs/verifier task-env bash /tests/test.sh
cat /logs/verifier/reward.txt
```

## What NOT to do

- Do NOT modify the Dockerfile, instruction.md, or solve.sh
- Do NOT remove existing fail_to_pass tests
- Do NOT add tests that only pass after the fix (those are f2p, not p2p)
- Do NOT add tests that require internet/GPU/special accounts
- If the full test suite is very slow, pick the relevant subset for the modified files
