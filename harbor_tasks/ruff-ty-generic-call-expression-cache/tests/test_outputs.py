"""
Task: ruff-ty-generic-call-expression-cache
Repo: astral-sh/ruff @ 64c4c96a57a525a36176f9b87dec0b7e7610abc3
PR:   24219

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/repo"
TARGET_FILE = f"{REPO}/crates/ty_python_semantic/src/types/infer/builder.rs"
BASE_COMMIT = "64c4c96a57a525a36176f9b87dec0b7e7610abc3"

CARGO_ENV = {**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"}


def _run_ty(test_file: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run ty type checker on a file. Raises on compilation failure or timeout."""
    r = subprocess.run(
        ["cargo", "run", "--bin", "ty", "--", "check", test_file],
        cwd=REPO,
        capture_output=True,
        timeout=timeout,
        env=CARGO_ENV,
    )
    # Detect compilation failures — cargo run exits quickly with build errors
    stderr = r.stderr.decode(errors="replace")
    if r.returncode != 0 and "could not compile" in stderr:
        raise AssertionError(f"Compilation failed:\n{stderr[-2000:]}")
    return r


def _get_added_lines() -> list[str]:
    """Return lines added by the agent's changes to builder.rs."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--", TARGET_FILE.replace(REPO + "/", "")],
        cwd=REPO,
        capture_output=True,
        timeout=10,
    )
    return [
        line[1:]
        for line in r.stdout.decode(errors="replace").splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """Modified builder.rs must compile."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
        env=CARGO_ENV,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nested_generic_6_levels():
    """6-level nested OrderedDict calls must complete within 30s."""
    tmp = Path("/tmp/test_nested_6.py")
    tmp.write_text(
        "from collections import OrderedDict\n"
        'OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(("one", 1)))))))\n'
    )
    try:
        _run_ty(str(tmp), timeout=30)
    except subprocess.TimeoutExpired:
        raise AssertionError("ty timed out on 6-level nested generic calls (>30s)")


# [pr_diff] fail_to_pass
def test_nested_generic_8_levels():
    """8-level nested OrderedDict calls must complete within 60s."""
    tmp = Path("/tmp/test_nested_8.py")
    tmp.write_text(
        "from collections import OrderedDict\n"
        'OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict(("k", 1)))))))))\n'
    )
    try:
        _run_ty(str(tmp), timeout=60)
    except subprocess.TimeoutExpired:
        raise AssertionError("ty timed out on 8-level nested generic calls (>60s)")


# [pr_diff] fail_to_pass
def test_nested_generic_varied_types():
    """Nested generic calls with different types must also complete quickly."""
    tmp = Path("/tmp/test_nested_varied.py")
    tmp.write_text(
        "from collections import OrderedDict\n"
        "d1 = OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict({1: 'a'})))))\n"
        "d2 = OrderedDict(OrderedDict(OrderedDict(OrderedDict(OrderedDict([(True, 3.14)])))))\n"
    )
    try:
        _run_ty(str(tmp), timeout=30)
    except subprocess.TimeoutExpired:
        raise AssertionError("ty timed out on nested generic calls with varied types (>30s)")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_basic_type_checking():
    """Basic OrderedDict type checking still works (completes without hanging)."""
    tmp = Path("/tmp/test_basic_od.py")
    tmp.write_text(
        "from collections import OrderedDict\n\n"
        "x: OrderedDict[str, int] = OrderedDict()\n"
        'x["hello"] = 42\n'
        "y = list(x.keys())\n"
    )
    try:
        _run_ty(str(tmp), timeout=30)
    except subprocess.TimeoutExpired:
        raise AssertionError("ty timed out on basic OrderedDict type checking")


# [repo_tests] pass_to_pass
def test_nongeneric_code():
    """Non-generic code still type-checks correctly."""
    tmp = Path("/tmp/test_nongeneric.py")
    tmp.write_text(
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n\n"
        "result = add(1, 2)\n"
        "name: str = 'hello'\n"
        "length = len(name)\n"
    )
    try:
        _run_ty(str(tmp), timeout=15)
    except subprocess.TimeoutExpired:
        raise AssertionError("ty timed out on non-generic code")


# ---------------------------------------------------------------------------
# Anti-stub (static, fail_to_pass)
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_builder_modified():
    """builder.rs must be modified from the base commit."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--",
         "crates/ty_python_semantic/src/types/infer/builder.rs"],
        cwd=REPO,
        capture_output=True,
        timeout=10,
    )
    assert r.stdout.strip(), "builder.rs was not modified from the base commit"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ 64c4c96
def test_no_local_imports():
    """Agent must not add function-local Rust imports (AGENTS.md:76)."""
    added = _get_added_lines()
    bad = []
    for line in added:
        stripped = line.strip()
        # Function-local imports are indented `use` inside method bodies
        if re.match(r"^\s{8,}use\s+\S+::", line) and not stripped.startswith("//"):
            bad.append(f"  {stripped}")
    assert not bad, "Found function-local imports in new code:\n" + "\n".join(bad)


# [agent_config] pass_to_pass — AGENTS.md:79 @ 64c4c96
def test_no_unwrap_on_new_code():
    """New code must not use .unwrap(), panic!(), or unreachable!() (AGENTS.md:79)."""
    added = _get_added_lines()
    bad = []
    for line in added:
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        for pattern in [".unwrap()", "panic!(", "unreachable!("]:
            if pattern in stripped:
                bad.append(f"  {stripped}  [{pattern}]")
    assert not bad, "Found unsafe patterns in new code:\n" + "\n".join(bad)


# [agent_config] pass_to_pass — AGENTS.md:81 @ 64c4c96
def test_no_allow_lint_suppression():
    """New code must use #[expect()] not #[allow()] for lint suppression (AGENTS.md:81)."""
    added = _get_added_lines()
    bad = []
    for line in added:
        stripped = line.strip()
        if "#[allow(" in stripped and not stripped.startswith("//"):
            bad.append(f"  {stripped}")
    assert not bad, (
        "Found #[allow()] in new code — use #[expect()] instead:\n" + "\n".join(bad)
    )
