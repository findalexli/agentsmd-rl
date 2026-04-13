"""
Task: ruff-fstring-multiline-pre-312
Repo: ruff @ 9a55bc6568caeba0c78c6f3358cd2f9475006f72
PR:   24377

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
RUFF_BIN = os.path.join(REPO, "target", "debug", "ruff")


def _ensure_ruff():
    """Build ruff binary if not already built."""
    if not os.path.exists(RUFF_BIN):
        r = subprocess.run(
            ["cargo", "build", "--bin", "ruff"],
            cwd=REPO, capture_output=True, timeout=600,
        )
        assert r.returncode == 0, f"Build failed:\n{r.stderr.decode()}"


def _format_code(code: str, target_version: str) -> str:
    """Run ruff format on code with the given target version, return formatted output."""
    _ensure_ruff()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            [RUFF_BIN, "format", "--target-version", target_version, tmp],
            capture_output=True, timeout=30,
        )
        return Path(tmp).read_text()
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ruff_builds():
    """Ruff compiles successfully after changes."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cargo_check_formatter():
    """Repo's cargo check passes on ruff_python_formatter (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_python_formatter"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_clippy_formatter():
    """Repo's cargo clippy passes on ruff_python_formatter (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ruff_python_formatter", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Cargo clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_test_formatter():
    """Repo's cargo test passes on ruff_python_formatter (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_python_formatter", "--features", "serde", "--", "--test-threads=4"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Cargo test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_fmt_check():
    """Repo's code formatting passes cargo fmt --check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Cargo fmt check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_formatter_fstring_fixtures():
    """Repo's formatter fstring fixture tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_python_formatter", "--features", "serde", "--", "fstring", "--test-threads=4"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Formatter fstring fixture tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_help():
    """Built ruff binary can show format help (pass_to_pass)."""
    _ensure_ruff()
    r = subprocess.run(
        [RUFF_BIN, "format", "--help"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Ruff format --help failed:\n{r.stderr[-500:]}"
    assert "target-version" in r.stdout, "Expected target-version option in help output"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fstring_no_multiline_expansion_pre312():
    """Non-triple-quoted f-string replacement fields must not expand to multiline on pre-3.12."""
    # A compact list with trailing comma in an f-string that exceeds line width.
    # On the buggy base, the formatter expands {[ttttteeeeeeeeest,]} to a multiline
    # list, introducing invalid syntax for Python <3.12.
    input_code = (
        'if f"aaaaaaaaaaa {[ttttteeeeeeeeest,]}'
        ' more {aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}":\n'
        '    pass\n'
    )
    formatted = _format_code(input_code, "py311")
    # The list must NOT be expanded across multiple lines
    assert "{\n    [" not in formatted, (
        f"Replacement field expanded to multiline on py311 (should stay flat):\n{formatted}"
    )
    # Verify the list stays inline (trailing comma may be removed by formatter)
    assert "{[ttttteeeeeeeeest" in formatted, (
        f"Expected inline list expression in output:\n{formatted}"
    )


# [pr_diff] fail_to_pass
def test_fstring_mixed_fields_pre312():
    """Already-multiline fields preserved, but compact fields stay flat on pre-3.12."""
    # The second replacement field is already multiline in source (should be preserved).
    # The first field is compact (should NOT be expanded on pre-3.12).
    input_code = (
        'if f"aaaaaaaaaaa {[ttttteeeeeeeeest,]} more {\n'
        '    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n'
        '}":\n'
        '    pass\n'
    )
    formatted = _format_code(input_code, "py311")
    # First field: must stay flat (no multiline expansion of the list)
    assert "{[ttttteeeeeeeeest" in formatted, (
        f"First replacement field should stay flat on py311:\n{formatted}"
    )
    # The already-multiline second field should be preserved
    lines = formatted.strip().splitlines()
    assert len(lines) >= 3, (
        f"Already-multiline second field should be preserved:\n{formatted}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — verify 3.12 behavior not broken
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_fstring_multiline_allowed_on_312():
    """On Python 3.12+, f-strings with already-multiline fields preserve/allow expansion."""
    # The second field is already multiline (from unsupported syntax), so on 3.12+
    # the formatter is allowed to expand other fields too.
    input_code = (
        'if f"aaaaaaaaaaa {[ttttteeeeeeeeest,]} more {\n'
        '    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n'
        '}":\n'
        '    pass\n'
    )
    formatted = _format_code(input_code, "py312")
    # On 3.12+, since there's already a multiline field, the list CAN expand
    assert "{\n    [" in formatted, (
        f"List should expand to multiline on py312:\n{formatted}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 9a55bc6568caeba0c78c6f3358cd2f9475006f72
def test_no_unwrap_panic_in_modified_file():
    """AGENTS.md:79 — No .unwrap()/panic!/unreachable! in production code of modified file."""
    src = Path(
        REPO, "crates", "ruff_python_formatter", "src", "other",
        "interpolated_string_element.rs"
    ).read_text()
    # Exclude test code
    test_marker = "#[cfg(test)]"
    idx = src.find(test_marker)
    production = src[:idx] if idx != -1 else src
    for pattern in [".unwrap()", "panic!", "unreachable!"]:
        occurrences = [
            (i + 1, line.strip())
            for i, line in enumerate(production.splitlines())
            if pattern in line and not line.strip().startswith("//")
        ]
        assert len(occurrences) == 0, (
            f"Found '{pattern}' in interpolated_string_element.rs at lines: "
            f"{occurrences}. AGENTS.md requires avoiding these patterns."
        )
