"""
Task: ruff-async115-anyio-submodule-import
Repo: astral-sh/ruff @ 6c8101a5b3ca4a6833f93e93cf8a33ea83f88616
PR:   24166

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
import re
from pathlib import Path

REPO = "/repo"
RUFF = None


def _build_ruff():
    """Build ruff once and cache the path."""
    global RUFF
    if RUFF is not None:
        return RUFF
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo build failed:\n{r.stderr.decode()[-2000:]}"
    RUFF = f"{REPO}/target/debug/ruff"
    return RUFF


def _run_ruff_fix(source: str) -> str:
    """Run ruff check --select ASYNC115 --fix --diff on given source, return diff output."""
    ruff = _build_ruff()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(source)
        f.flush()
        r = subprocess.run(
            [ruff, "check", "--select", "ASYNC115", "--fix", "--no-cache", "--diff", f.name],
            capture_output=True,
            text=True,
            timeout=30,
        )
    return r.stdout + r.stderr


def _run_ruff_check(source: str) -> str:
    """Run ruff check --select ASYNC115 on given source, return output."""
    ruff = _build_ruff()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(source)
        f.flush()
        r = subprocess.run(
            [ruff, "check", "--select", "ASYNC115", "--no-cache", f.name],
            capture_output=True,
            text=True,
            timeout=30,
        )
    return r.stdout + r.stderr


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_rust_syntax():
    """async_zero_sleep.rs must be valid Rust (parseable by rustfmt)."""
    src = f"{REPO}/crates/ruff_linter/src/rules/flake8_async/rules/async_zero_sleep.rs"
    r = subprocess.run(
        ["rustfmt", "--check", "--edition", "2021", src],
        capture_output=True,
        timeout=30,
    )
    # rustfmt returns 0 or 1 for parseable files; 2+ means parse error
    assert r.returncode < 2, f"async_zero_sleep.rs has syntax errors:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_anyio_alias_uses_submodule_import():
    """Autofix for aliased anyio import uses `import anyio.lowlevel`, not `from anyio import lowlevel`."""
    output = _run_ruff_fix(
        "from anyio import sleep as anyio_sleep\n\nasync def func():\n    await anyio_sleep(0)\n"
    )
    assert "import anyio.lowlevel" in output, f"Expected 'import anyio.lowlevel' in:\n{output}"
    assert "from anyio import lowlevel" not in output, f"Should not use from-import:\n{output}"


# [pr_diff] fail_to_pass
def test_anyio_alias_produces_checkpoint_call():
    """Autofix for aliased anyio produces anyio.lowlevel.checkpoint() call."""
    output = _run_ruff_fix(
        "from anyio import sleep as anyio_sleep\n\nasync def func():\n    await anyio_sleep(0)\n"
    )
    assert "anyio.lowlevel.checkpoint()" in output, f"Expected checkpoint() call in:\n{output}"


# [pr_diff] fail_to_pass
def test_anyio_direct_uses_submodule_import():
    """Autofix for direct anyio.sleep(0) uses submodule import."""
    output = _run_ruff_fix(
        "import anyio\n\nasync def func():\n    await anyio.sleep(0)\n"
    )
    assert "import anyio.lowlevel" in output, f"Expected 'import anyio.lowlevel' in:\n{output}"
    assert "from anyio import lowlevel" not in output, f"Should not use from-import:\n{output}"


# [pr_diff] fail_to_pass
def test_anyio_from_import_uses_submodule_import():
    """Autofix for non-aliased from-import also uses submodule import."""
    output = _run_ruff_fix(
        "from anyio import sleep\n\nasync def func():\n    await sleep(0)\n"
    )
    assert "import anyio.lowlevel" in output, f"Expected 'import anyio.lowlevel' in:\n{output}"
    assert "from anyio import lowlevel" not in output, f"Should not use from-import:\n{output}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_trio_autofix_still_works():
    """trio autofix still produces trio.lowlevel.checkpoint() call."""
    output = _run_ruff_fix(
        "import trio\n\nasync def func():\n    await trio.sleep(0)\n"
    )
    assert "trio.lowlevel.checkpoint()" in output, f"Expected trio checkpoint in:\n{output}"


# [pr_diff] pass_to_pass
def test_trio_nonzero_sleep_not_flagged():
    """trio.sleep(1) is NOT flagged by ASYNC115 (only zero-sleep is)."""
    output = _run_ruff_check(
        "import trio\n\nasync def func():\n    await trio.sleep(1)\n"
    )
    assert "ASYNC115" not in output, f"trio.sleep(1) should not be flagged:\n{output}"


# [repo_tests] pass_to_pass
def test_upstream_async115_snapshot_tests():
    """Upstream ASYNC115 snapshot tests pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_linter", "--", "flake8_async::tests::ASYNC115"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert "test result: ok" in r.stdout or "test result: ok" in r.stderr, (
        f"Upstream tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:72 @ 6c8101a5b3ca4a6833f93e93cf8a33ea83f88616
def test_fixture_includes_anyio_test_case():
    """Test fixture includes an anyio-specific test case (AGENTS.md:72 - all changes must be tested)."""
    fixture = Path(f"{REPO}/crates/ruff_linter/resources/test/fixtures/flake8_async/ASYNC115.py")
    assert fixture.exists(), "ASYNC115.py fixture file not found"
    content = fixture.read_text()
    assert re.search(r"anyio.*sleep.*anyio_sleep|from anyio import sleep as", content), (
        "Fixture should include an anyio aliased import test case"
    )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 6c8101a5b3ca4a6833f93e93cf8a33ea83f88616
def test_no_local_imports_in_function():
    """Rust imports at top of file, not locally in functions (AGENTS.md:76)."""
    src = Path(f"{REPO}/crates/ruff_linter/src/rules/flake8_async/rules/async_zero_sleep.rs")
    content = src.read_text()
    # Find the function body and check no `use` statements inside it
    fn_match = re.search(r"pub\(crate\) fn async_zero_sleep\(.*?\{(.*)", content, re.DOTALL)
    assert fn_match, "Could not find async_zero_sleep function"
    fn_body = fn_match.group(1)
    # Check first ~50 lines of function body for local use statements
    fn_lines = fn_body.split("\n")[:50]
    for line in fn_lines:
        stripped = line.strip()
        if stripped.startswith("use "):
            raise AssertionError(f"Local import found in function body: {stripped}")


# [agent_config] pass_to_pass — AGENTS.md:79 @ 6c8101a5b3ca4a6833f93e93cf8a33ea83f88616
def test_no_panic_or_unwrap():
    """No panic!(), unreachable!(), or .unwrap() in modified file (AGENTS.md:79)."""
    src = Path(f"{REPO}/crates/ruff_linter/src/rules/flake8_async/rules/async_zero_sleep.rs")
    content = src.read_text()
    for pattern in [r"\bpanic!\s*\(", r"\bunreachable!\s*\(", r"\.unwrap\(\)"]:
        matches = re.findall(pattern, content)
        assert not matches, f"Found disallowed pattern in async_zero_sleep.rs: {matches}"
