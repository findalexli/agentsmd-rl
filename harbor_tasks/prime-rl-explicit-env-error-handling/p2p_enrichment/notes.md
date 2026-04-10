# P2P Enrichment Results

## CI Commands Found and Verified

### 1. Ruff Lint Check
- **Command**: `ruff check src/prime_rl/orchestrator/trajectories.py src/prime_rl/orchestrator/orchestrator.py`
- **Status**: Verified working in Docker container (exit code 0)
- **Files checked**: Modified orchestrator files from the PR

### 2. Ruff Format Check
- **Command**: `ruff format --check src/prime_rl/orchestrator/trajectories.py src/prime_rl/orchestrator/orchestrator.py`
- **Status**: Verified working in Docker container (exit code 0)
- **Files checked**: Modified orchestrator files from the PR

## Tests to Add to test_outputs.py

```python
# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "src/prime_rl/orchestrator/trajectories.py", "src/prime_rl/orchestrator/orchestrator.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "src/prime_rl/orchestrator/trajectories.py", "src/prime_rl/orchestrator/orchestrator.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"
```

## Checks to Add to eval_manifest.yaml

```yaml
  # P2P Enrichment - CI/CD checks from the repo
  - id: repo_ruff_lint
    type: pass_to_pass
    origin: repo_tests
    description: "Ruff linter passes on modified orchestrator files"

  - id: repo_ruff_format
    type: pass_to_pass
    origin: repo_tests
    description: "Ruff format check passes on modified orchestrator files"
```

## Notes on Full Unit Tests

The upstream unit tests in `tests/unit/orchestrator/test_trajectories.py` require extensive dependencies:
- verifiers (complex dependency with git source)
- msgspec, tomli, loguru
- procps (for pkill used in conftest.py cleanup_zombies fixture)
- Many other ML/RL-specific packages

These dependencies would significantly increase the Docker image size and build time. The ruff-based checks provide lightweight CI validation instead.

## Updated Files Location

Since the tests/ directory is owned by `user:user`, the updated files are saved to:
- `/tmp/test_outputs_new.py` - Updated test_outputs.py with new p2p tests
- `/workspace/task/eval_manifest.yaml` - Already updated successfully

To apply the test_outputs.py changes:
```bash
sudo cp /tmp/test_outputs_new.py /workspace/task/tests/test_outputs.py
```
