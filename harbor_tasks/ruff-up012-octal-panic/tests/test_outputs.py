"""
Task: ruff-up012-octal-panic
Repo: astral-sh/ruff @ 5ac54ec2a708b46ec964465ce5d09cb9b80a3dc2
PR:   24390

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import pytest
from pathlib import Path

REPO = "/workspace/ruff"
RULE_FILE = f"{REPO}/crates/ruff_linter/src/rules/pyupgrade/rules/unnecessary_encode_utf8.rs"


@pytest.fixture(scope="session")
def ruff_bin():
    """Build ruff (incremental) and return binary path."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo build failed:\n{r.stderr[-3000:]}"
    binary = Path(REPO) / "target" / "debug" / "ruff"
    assert binary.exists(), f"Binary not found at {binary}"
    return str(binary)


def _run_ruff_check(ruff_bin, code, tmp_path, suffix=""):
    """Write code to a temp file and run ruff check --select UP012."""
    test_file = tmp_path / f"test_input{suffix}.py"
    test_file.write_text(code)
    return subprocess.run(
        [ruff_bin, "check", "--select", "UP012", "--no-cache", str(test_file)],
        capture_output=True, text=True, timeout=30,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """The crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "--bin", "ruff"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-3000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_panic_on_null_terminated_encode(ruff_bin, tmp_path):
    r"""ruff check --select UP012 must not panic on strings ending with \\0.

    On the base commit, "$IMURAW\\0".encode("ascii") causes a thread panic
    due to an off-by-one error in cursor.skip_bytes for octal escapes.
    """
    code = 'IMR_HEADER = "$IMURAW\\0".encode("ascii")\n'
    r = _run_ruff_check(ruff_bin, code, tmp_path)
    assert r.returncode != 101, f"ruff panicked (exit 101):\n{r.stderr}"
    assert "panic" not in r.stderr.lower(), f"ruff panicked:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_octal_named_escape_no_false_positive(ruff_bin, tmp_path):
    r"""UP012 must not trigger on strings with \\000 followed by \\N{name}.

    The off-by-one causes the cursor to skip past \\N{DIGIT ONE},
    making the function miss this string-only escape and incorrectly
    trigger UP012.
    """
    code = '"\\000\\N{DIGIT ONE}".encode()\n'
    r = _run_ruff_check(ruff_bin, code, tmp_path)
    msg = r"UP012 false positive on '\000\N{DIGIT ONE}':"
    assert "UP012" not in r.stdout and "UP012" not in r.stderr, f"{msg}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_varied_octal_endings_no_crash(ruff_bin, tmp_path):
    """Strings ending in various short octal escapes must not crash ruff.

    The off-by-one in skip_bytes causes panics when the octal escape is
    at the end of the string. Test with multiple different patterns.
    """
    test_cases = [
        ('"end\\0".encode("utf-8")\n', "single_digit_zero"),
        ('"test\\7".encode("utf-8")\n', "single_digit_seven"),
        ('"data\\00".encode("utf-8")\n', "two_digit_octal"),
    ]
    for code, label in test_cases:
        test_file = tmp_path / f"octal_{label}.py"
        test_file.write_text(code)
        r = subprocess.run(
            [ruff_bin, "check", "--select", "UP012", "--no-cache", str(test_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode != 101, (
            f"ruff panicked on {label} (exit 101):\n{r.stderr}"
        )
        assert "panic" not in r.stderr.lower(), (
            f"ruff panicked on {label}:\n{r.stderr}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — upstream snapshot tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_up012_snapshot_tests():
    """Upstream UP012 snapshot tests must pass (verifies snapshots are updated)."""
    r = subprocess.run(
        ["cargo", "test", "--package", "ruff_linter", "--", "UP012"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"UP012 snapshot tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_cargo_clippy():
    """Repo's cargo clippy passes on ruff_linter package (pass_to_pass)."""
    # Install clippy component if needed
    subprocess.run(
        ["rustup", "component", "add", "clippy"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["cargo", "clippy", "--package", "ruff_linter", "--all-targets", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-2000:]}"


# [repo_tests] pass_to_pass
def test_repo_pyupgrade_tests():
    """Repo's pyupgrade rule tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "--package", "ruff_linter", "pyupgrade"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"pyupgrade tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 5ac54ec2a708b46ec964465ce5d09cb9b80a3dc2
def test_no_unwrap_or_panic():
    """Modified rule file must not introduce panic!(), unreachable!(), or .unwrap()."""
    content = Path(RULE_FILE).read_text()
    for pattern, label in [
        (r'\bunwrap\(\)', '.unwrap()'),
        (r'\bpanic!\s*\(', 'panic!()'),
        (r'\bunreachable!\s*\(', 'unreachable!()'),
    ]:
        matches = re.findall(pattern, content)
        assert not matches, (
            f"Found {label} in unnecessary_encode_utf8.rs — "
            f"AGENTS.md line 79 says to avoid these patterns"
        )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 5ac54ec2a708b46ec964465ce5d09cb9b80a3dc2
def test_rust_imports_at_top():
    """Rust imports must be at the top of the file, not locally inside functions."""
    content = Path(RULE_FILE).read_text()
    in_function = False
    brace_depth = 0
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r'(pub(\(crate\))?\s+)?fn\s+', stripped):
            in_function = True
        if in_function:
            brace_depth += line.count('{') - line.count('}')
            if stripped.startswith('use '):
                assert False, (
                    f"Found local import inside function body: {stripped!r} — "
                    f"AGENTS.md line 76 says imports must be at the top of the file"
                )
            if brace_depth <= 0:
                in_function = False
                brace_depth = 0
