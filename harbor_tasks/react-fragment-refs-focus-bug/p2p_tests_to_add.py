# Additional pass-to-pass tests that should be added to test_outputs.py
# These tests verify the repo's CI/CD checks pass on both base and fixed code.

# Add this helper function after _run_node():

def _run_yarn_command(cmd: list, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a yarn command in the repo directory."""
    return subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# Add these p2p tests after test_capture_listener_cleanup():

# ---------------------------------------------------------------------------
# Pass-to-pass (repo CI) — verify repo's own checks pass
# ---------------------------------------------------------------------------

def test_repo_lint():
    """Repo's ESLint check passes on the modified file (pass_to_pass).

    The React repo runs ESLint on all source files. This test verifies that
    the modified ReactFiberConfigDOM.js passes linting.
    """
    # Run eslint on the specific file that was modified
    r = _run_yarn_command(
        ["node", "./scripts/tasks/eslint.js", TARGET],
        timeout=60
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_flow():
    """Repo's Flow typecheck passes (pass_to_pass).

    React uses Flow for type checking. The 'dom' inline config includes
    the react-dom-bindings package where the fix is applied.
    """
    r = _run_yarn_command(
        ["node", "./scripts/tasks/flow.js", "dom"],
        timeout=120
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_unit_tests_relevant():
    """Unit tests for react-dom-bindings pass (pass_to_pass).

    The full test suite takes too long, so we run only tests for the
    package containing the modified file.
    """
    r = _run_yarn_command(
        ["yarn", "test", "--testPathPattern=react-dom-bindings", "-r=stable", "--env=development", "--ci"],
        timeout=120
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
