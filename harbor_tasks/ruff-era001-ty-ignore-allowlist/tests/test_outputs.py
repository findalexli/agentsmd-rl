"""
Task: ruff-era001-ty-ignore-allowlist
Repo: astral-sh/ruff @ 55c5d90699afabf3e01340b7ff8e645fe4a237a2
PR:   #24192

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = "/repo"


@pytest.fixture(scope="module")
def ruff_bin():
    """Build ruff once for all tests that need it."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr.decode()[-1000:]}"
    return f"{REPO}/target/debug/ruff"


def _check_era001(ruff_bin: str, code: str) -> str:
    """Run ruff check --select ERA001 on code snippet, return combined output."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        r = subprocess.run(
            [ruff_bin, "check", "--select", "ERA001", "--no-cache", f.name],
            capture_output=True, text=True, timeout=30,
        )
    return r.stdout + r.stderr


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ty_ignore_not_flagged(ruff_bin):
    """ty: ignore comments (with and without error codes) must not trigger ERA001."""
    code = (
        "import foo  # ty: ignore[unresolved-import]\n"
        "# ty: ignore\n"
        'x: int = "hello"  # ty: ignore[invalid-assignment]\n'
        "# ty: ignore[missing-argument, invalid-argument-type]\n"
        "# ty: ignore[]\n"
    )
    output = _check_era001(ruff_bin, code)
    assert "ERA001" not in output, f"ty: ignore was flagged:\n{output}"


# [pr_diff] fail_to_pass
def test_ty_ignore_no_space_not_flagged(ruff_bin):
    """ty:ignore (no space after colon) must not trigger ERA001."""
    code = (
        "# ty:ignore\n"
        "# ty:ignore[some-code]\n"
        "x = 1  # ty:ignore[invalid-assignment]\n"
    )
    output = _check_era001(ruff_bin, code)
    assert "ERA001" not in output, f"ty:ignore (no space) was flagged:\n{output}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_real_commented_code_still_flagged(ruff_bin):
    """ERA001 must still detect actual commented-out Python code."""
    code = (
        "# import os\n"
        "# x = 1 + 2\n"
        "# if True:\n"
        "# for i in range(10):\n"
        '# print("hello")\n'
    )
    output = _check_era001(ruff_bin, code)
    assert "ERA001" in output, f"ERA001 failed to detect real commented-out code:\n{output}"


# [pr_diff] pass_to_pass
def test_type_ignore_still_allowlisted(ruff_bin):
    """type: ignore comments must remain allowlisted (not regressed)."""
    code = (
        "# type: ignore\n"
        "# type: ignore[import]\n"
        "# type:ignore\n"
    )
    output = _check_era001(ruff_bin, code)
    assert "ERA001" not in output, f"type: ignore was incorrectly flagged:\n{output}"


# [pr_diff] pass_to_pass
def test_mypy_pyright_still_allowlisted(ruff_bin):
    """mypy/pyright suppression comments must remain allowlisted."""
    code = (
        "# mypy: ignore-errors\n"
        "# pyright: ignore-errors\n"
    )
    output = _check_era001(ruff_bin, code)
    assert "ERA001" not in output, f"mypy/pyright was incorrectly flagged:\n{output}"


# [repo_tests] pass_to_pass
def test_upstream_detection_unit_tests():
    """Upstream Rust unit tests for eradicate::detection must pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_linter", "--", "eradicate::detection"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Upstream detection tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:72 @ 55c5d90699afabf3e01340b7ff8e645fe4a237a2
def test_changes_are_tested():
    """All changes must be tested (AGENTS.md:72). Rust unit tests must cover ty:ignore."""
    detection_rs = Path(
        f"{REPO}/crates/ruff_linter/src/rules/eradicate/detection.rs"
    ).read_text()
    tests_start = detection_rs.find("mod tests")
    assert tests_start != -1, "No mod tests section found in detection.rs"
    tests_section = detection_rs[tests_start:]
    assert "ty" in tests_section and "ignore" in tests_section, (
        "No ty:ignore test assertions found in detection.rs mod tests"
    )


# [agent_config] pass_to_pass — AGENTS.md:79 @ 55c5d90699afabf3e01340b7ff8e645fe4a237a2
def test_no_new_unwrap_in_detection():
    """Avoid .unwrap() (AGENTS.md:79). Agent must not add new .unwrap() calls."""
    # AST-only because: Rust source cannot be imported/executed from Python
    detection_rs = Path(
        f"{REPO}/crates/ruff_linter/src/rules/eradicate/detection.rs"
    ).read_text()
    # Baseline has exactly 4 .unwrap() calls in the existing code
    BASELINE_UNWRAP_COUNT = 4
    unwrap_count = detection_rs.count(".unwrap()")
    assert unwrap_count <= BASELINE_UNWRAP_COUNT, (
        f"detection.rs has {unwrap_count} .unwrap() call(s) (baseline: {BASELINE_UNWRAP_COUNT}); "
        "use ? operator or proper error handling instead (AGENTS.md:79)"
    )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 55c5d90699afabf3e01340b7ff8e645fe4a237a2
def test_no_local_imports_in_detection():
    """Rust imports at file top (AGENTS.md:76). No 'use' inside function bodies."""
    # AST-only because: Rust source cannot be imported/executed from Python
    import re
    detection_rs = Path(
        f"{REPO}/crates/ruff_linter/src/rules/eradicate/detection.rs"
    ).read_text()
    # Filter out 'use' inside mod tests {} which is acceptable (test-only imports)
    tests_start = detection_rs.find("mod tests")
    main_section = detection_rs[:tests_start] if tests_start != -1 else detection_rs
    # Top-level 'use' starts at column 0; local imports are indented inside fn bodies
    local_uses = re.findall(r"^\s{4,}use\s+", main_section, re.MULTILINE)
    assert len(local_uses) == 0, (
        f"Found {len(local_uses)} local 'use' import(s) in function bodies in detection.rs; "
        "Rust imports should go at the top of the file (AGENTS.md:76)"
    )
