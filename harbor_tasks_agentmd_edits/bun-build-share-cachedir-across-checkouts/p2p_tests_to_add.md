# Pass-to-Pass Tests to Add

These tests should be added to `tests/test_outputs.py` once Node.js is installed in the Docker image.

## Python Tests to Add

```python
# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD gates
# ---------------------------------------------------------------------------

def test_repo_typescript_syntax():
    """Modified TypeScript files have valid syntax (pass_to_pass)."""
    files = [
        "scripts/build/config.ts",
        "scripts/build/download.ts",
        "scripts/build/clean.ts",
        "scripts/build/configure.ts",
    ]
    for f in files:
        r = subprocess.run(
            ["node", "--check", f],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Syntax error in {f}:\n{r.stderr}"


def test_repo_typescript_types_basic():
    """scripts/build TypeScript has no type errors (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--project", "scripts/build/tsconfig.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript type errors:\n{r.stderr[-500:]}"


def test_repo_build_script_runnable():
    """Build entry point script is syntactically valid (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--check", "scripts/build.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert "SyntaxError" not in r.stderr, f"Syntax error in build.ts: {r.stderr}"
```

## eval_manifest.yaml Additions

Add these to the `checks:` list in `eval_manifest.yaml`:

```yaml
  - id: test_repo_typescript_syntax
    type: pass_to_pass
    origin: repo_tests
    description: Modified TypeScript files have valid syntax

  - id: test_repo_typescript_types_basic
    type: pass_to_pass
    origin: repo_tests
    description: scripts/build TypeScript has no type errors

  - id: test_repo_build_script_runnable
    type: pass_to_pass
    origin: repo_tests
    description: Build entry point script is syntactically valid
```

## Required Dockerfile Changes

The Dockerfile needs Node.js installed. Add this before the git clone:

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends nodejs npm && \
    rm -rf /var/lib/apt/lists/*
```
