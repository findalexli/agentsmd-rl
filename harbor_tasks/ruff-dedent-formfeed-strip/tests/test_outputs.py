"""
Task: ruff-dedent-formfeed-strip
Repo: ruff @ 1f430e68af6e627569776dfbcd03b98ac7c29eb6
PR:   24381

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


def _ruff_fix(code: str, rule: str = "RUF072") -> str:
    """Run ruff check --fix --preview on code, return the fixed content."""
    _ensure_ruff()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        subprocess.run(
            [RUFF_BIN, "check", "--preview", "--select", rule, "--fix", tmp],
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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_formfeed_ruf072_fix_valid_python():
    """RUF072 fix on code preceded by form feed must produce valid Python."""
    # Form feed (\x0c) before try: triggers the bug in dedent_to
    code = "\x0ctry:\n    1\nfinally:\n    pass\n"
    fixed = _ruff_fix(code)
    # The fix should produce syntactically valid Python
    try:
        compile(fixed, "<ruf072-fix>", "exec")
    except SyntaxError as e:
        raise AssertionError(
            f"RUF072 fix produced invalid Python:\n{fixed!r}\nError: {e}"
        ) from e


# [pr_diff] fail_to_pass
def test_formfeed_ruf072_fix_correct_dedent():
    """RUF072 fix on form-feed-prefixed try must produce correctly dedented output."""
    code = "\x0ctry:\n    1\nfinally:\n    pass\n"
    fixed = _ruff_fix(code)
    # After fix, the body "1" should be at column 0 (properly dedented).
    # On base, the form feed causes wrong indent calculation, leaving "1" indented.
    lines = [l for l in fixed.splitlines() if l.strip() and not l.strip().startswith("#")]
    found_correctly_dedented = any(
        l.lstrip("\x0c").startswith("1") for l in lines
    )
    assert found_correctly_dedented, (
        f"Expected '1' at column 0 (properly dedented), but got:\n{fixed!r}"
    )


# [pr_diff] fail_to_pass
def test_multiple_formfeeds_ruf072_fix():
    """RUF072 fix works with multiple consecutive form feeds before try."""
    code = "\x0c\x0ctry:\n    x = 1\nfinally:\n    pass\n"
    fixed = _ruff_fix(code)
    try:
        compile(fixed, "<ruf072-multi-ff>", "exec")
    except SyntaxError as e:
        raise AssertionError(
            f"RUF072 fix with multiple form feeds produced invalid Python:\n{fixed!r}\nError: {e}"
        ) from e
    assert "finally" not in fixed, (
        f"Expected empty finally clause removed, but got:\n{fixed!r}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_dedent_tests_pass():
    """Upstream dedent unit tests in ruff_python_trivia still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_python_trivia", "--", "dedent"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Upstream dedent tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [repo_tests] pass_to_pass — CI/CD gates
def test_repo_cargo_fmt():
    """Repo code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        cwd=REPO, capture_output=True, timeout=60,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass — CI/CD gates
def test_repo_cargo_clippy():
    """Repo clippy linting passes on ruff_python_trivia (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ruff_python_trivia", "--all-targets", "--all-features", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass — CI/CD gates
def test_repo_cargo_doc():
    """Repo documentation builds for ruff_python_trivia (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "doc", "--no-deps", "-p", "ruff_python_trivia"],
        cwd=REPO, capture_output=True, timeout=60,
    )
    assert r.returncode == 0, f"cargo doc failed:\n{r.stderr.decode()[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 1f430e68af6e627569776dfbcd03b98ac7c29eb6
def test_no_unwrap_panic_in_dedent_to():
    """AGENTS.md:79 — Avoid panic!/unreachable!/.unwrap() in dedent_to function."""
    src = Path(REPO, "crates", "ruff_python_trivia", "src", "textwrap.rs").read_text()

    # Extract the dedent_to function body (up to the next pub fn or mod block)
    start_marker = "pub fn dedent_to("
    start = src.find(start_marker)
    assert start != -1, "dedent_to function not found in textwrap.rs"

    # Find the end: next top-level pub fn, or #[cfg(test)] module
    rest = src[start:]
    end_markers = ["\npub fn ", "\n#[cfg(test)]", "\nmod "]
    end = len(rest)
    for marker in end_markers:
        idx = rest.find(marker, 100)  # skip past the signature
        if idx != -1 and idx < end:
            end = idx
    func_body = rest[:end]

    for pattern in [".unwrap()", "panic!", "unreachable!"]:
        violations = [
            (i + 1, line.strip())
            for i, line in enumerate(func_body.splitlines())
            if pattern in line and not line.strip().startswith("//")
        ]
        assert len(violations) == 0, (
            f"Found '{pattern}' in dedent_to body: {violations}. "
            f"AGENTS.md:79 requires avoiding these patterns."
        )
