"""
Task: ruff-sim113-sibling-loop-false-negative
Repo: astral-sh/ruff @ 5f7e0346bc946d7fb484b285d49d351d3a54d526
PR:   #24235

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/ruff"
RUFF_BIN = None  # built lazily
RULE_FILE = "crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs"


def _build_ruff():
    """Build ruff binary if not already built, return path."""
    global RUFF_BIN
    if RUFF_BIN is not None:
        return RUFF_BIN
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo build failed:\n{r.stderr.decode()[-2000:]}"
    RUFF_BIN = str(Path(REPO) / "target/debug/ruff")
    assert Path(RUFF_BIN).is_file(), "ruff binary not found after build"
    return RUFF_BIN


def _run_ruff(code: str) -> str:
    """Write code to a temp file and run ruff --select SIM113 on it."""
    tmp = Path("/tmp/sim113_test.py")
    tmp.write_text(textwrap.dedent(code))
    ruff = _build_ruff()
    r = subprocess.run(
        [ruff, "check", "--select", "SIM113", "--no-cache", str(tmp)],
        capture_output=True, timeout=30,
    )
    return r.stdout.decode() + r.stderr.decode()


def _count_sim113(output: str) -> int:
    return output.count("SIM113")


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """enumerate_for_loop.rs must exist and compile."""
    rule_path = Path(REPO) / RULE_FILE
    assert rule_path.is_file(), f"{RULE_FILE} does not exist"
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_linter"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sibling_loops_both_flagged():
    """Two sibling loops reusing the same counter variable must both be flagged."""
    output = _run_ruff("""\
        def func():
            i = 0
            for val in [1, 2, 3]:
                print(f"{i}: {val}")
                i += 1

            i = 0
            for val in [1, 2, 3]:
                print(f"{i}: {val}")
                i += 1
    """)
    assert _count_sim113(output) >= 2, (
        f"Expected >=2 SIM113 violations for sibling loops, got {_count_sim113(output)}\n{output}"
    )


# [pr_diff] fail_to_pass
def test_enumerate_then_manual():
    """enumerate() loop followed by manual counter — second loop must be flagged."""
    output = _run_ruff("""\
        def func():
            for i, val in enumerate([1, 2, 3]):
                print(f"{i}: {val}")

            i = 0
            for val in [1, 2, 3]:
                print(f"{i}: {val}")
                i += 1
    """)
    assert _count_sim113(output) >= 1, (
        f"Expected >=1 SIM113 for enumerate-then-manual, got {_count_sim113(output)}\n{output}"
    )


# [pr_diff] fail_to_pass
def test_three_sibling_loops():
    """Three sibling loops with same counter — all three must be flagged."""
    output = _run_ruff("""\
        def func():
            i = 0
            for val in [1, 2, 3]:
                print(f"{i}: {val}")
                i += 1

            i = 0
            for val in [4, 5, 6]:
                print(f"{i}: {val}")
                i += 1

            i = 0
            for val in [7, 8, 9]:
                print(f"{i}: {val}")
                i += 1
    """)
    assert _count_sim113(output) >= 3, (
        f"Expected >=3 SIM113 for three sibling loops, got {_count_sim113(output)}\n{output}"
    )


# [pr_diff] fail_to_pass
def test_counter_used_between_sibling_loops():
    """Counter used after first loop, reset before second — second loop still flagged."""
    output = _run_ruff("""\
        def func():
            i = 0
            for val in [1, 2, 3]:
                print(f"{i}: {val}")
                i += 1
            print(f"After first: {i}")

            i = 0
            for val in [4, 5, 6]:
                print(f"{i}: {val}")
                i += 1
    """)
    # Second loop should be flagged (counter is reset, fresh lifetime)
    assert _count_sim113(output) >= 1, (
        f"Expected >=1 SIM113 for second loop after counter reset, got {_count_sim113(output)}\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_single_loop_still_flagged():
    """Single loop with manual counter — must still be flagged (regression guard)."""
    output = _run_ruff("""\
        def func():
            idx = 0
            for x in range(10):
                print(idx)
                idx += 1
    """)
    assert _count_sim113(output) >= 1, (
        f"Single loop regression: expected >=1 SIM113, got {_count_sim113(output)}\n{output}"
    )


# [pr_diff] pass_to_pass
def test_counter_used_after_loop_not_flagged():
    """Counter used after the loop — must NOT be flagged."""
    output = _run_ruff("""\
        def func():
            i = 0
            for val in [1, 2, 3]:
                print(f"{i}: {val}")
                i += 1
            print(f"Total: {i}")
    """)
    assert _count_sim113(output) == 0, (
        f"Counter-used-after should not be flagged, got {_count_sim113(output)}\n{output}"
    )


# [pr_diff] pass_to_pass
def test_different_counter_names_both_flagged():
    """Sibling loops with different counter names — both independently flagged."""
    output = _run_ruff("""\
        def func():
            i = 0
            for val in [1, 2, 3]:
                print(f"{i}: {val}")
                i += 1

            j = 0
            for val in [4, 5, 6]:
                print(f"{j}: {val}")
                j += 1
    """)
    assert _count_sim113(output) >= 2, (
        f"Different counters: expected >=2 SIM113, got {_count_sim113(output)}\n{output}"
    )


# [repo_tests] pass_to_pass
def test_existing_sim113_tests():
    """Upstream SIM113 snapshot tests still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_linter", "--", "SIM113", "--test-threads=1"],
        cwd=REPO, capture_output=True, timeout=300,
        env={**__import__("os").environ, "INSTA_UPDATE": "new"},
    )
    assert r.returncode == 0, (
        f"Upstream SIM113 tests failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ 5f7e0346
def test_no_local_imports_in_functions():
    """Rust imports should go at the top of the file, not inside functions."""
    rule_src = (Path(REPO) / RULE_FILE).read_text()
    in_function = False
    for line in rule_src.splitlines():
        stripped = line.strip()
        if stripped.startswith("fn ") or stripped.startswith("pub fn ") or stripped.startswith("pub(crate) fn "):
            in_function = True
        if in_function and stripped.startswith("use "):
            assert False, f"Found local import inside function body: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:79 @ 5f7e0346
def test_no_new_unwraps():
    """No new .unwrap() calls added to enumerate_for_loop.rs."""
    r_base = subprocess.run(
        ["git", "show", f"HEAD:{ RULE_FILE}"],
        cwd=REPO, capture_output=True,
    )
    base_src = r_base.stdout.decode() if r_base.returncode == 0 else ""
    curr_src = (Path(REPO) / RULE_FILE).read_text()
    base_unwraps = base_src.count(".unwrap()")
    curr_unwraps = curr_src.count(".unwrap()")
    assert curr_unwraps <= base_unwraps, (
        f"New .unwrap() calls added: {base_unwraps} -> {curr_unwraps}"
    )


# [agent_config] pass_to_pass — AGENTS.md:81 @ 5f7e0346
def test_prefer_expect_over_allow():
    """No new #[allow()] attributes — prefer #[expect()] instead."""
    r_base = subprocess.run(
        ["git", "show", f"HEAD:{RULE_FILE}"],
        cwd=REPO, capture_output=True,
    )
    base_src = r_base.stdout.decode() if r_base.returncode == 0 else ""
    curr_src = (Path(REPO) / RULE_FILE).read_text()
    base_allows = base_src.count("#[allow(")
    curr_allows = curr_src.count("#[allow(")
    assert curr_allows <= base_allows, (
        f"New #[allow()] added ({base_allows} -> {curr_allows}). "
        "Use #[expect()] instead per AGENTS.md:81"
    )
