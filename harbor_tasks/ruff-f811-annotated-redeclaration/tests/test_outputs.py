"""
Task: ruff-f811-annotated-redeclaration
Repo: astral-sh/ruff @ 29bf84e064567bde67320efd164a02b7322cc664
PR:   #23802 (annotated variable redeclaration detection for F811)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/ruff"
RUFF_BIN = f"{REPO}/target/debug/ruff"
RULE_FILE = f"{REPO}/crates/ruff_linter/src/rules/pyflakes/rules/redefined_while_unused.rs"
PREVIEW_FILE = f"{REPO}/crates/ruff_linter/src/preview.rs"


def _build_ruff():
    """Build ruff binary if not already built."""
    if Path(RUFF_BIN).exists():
        return
    subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, timeout=600,
    )


def _run_ruff(src: str, *, preview: bool = True, fix: bool = False) -> subprocess.CompletedProcess:
    """Write src to a temp file and run ruff check --select F811 on it."""
    _build_ruff()
    tmp = Path("/tmp/_ruff_test.py")
    tmp.write_text(textwrap.dedent(src))
    cmd = [RUFF_BIN, "check", "--select", "F811", "--no-cache"]
    if preview:
        cmd.append("--preview")
    if fix:
        cmd.append("--fix")
    cmd.append(str(tmp))
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ruff_linter crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_linter"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_annotated_redeclarations_flagged():
    """Annotated redeclarations are flagged as F811 in preview mode."""
    r = _run_ruff("""\
        bar: int = 1
        bar: int = 2
        x: str = "hello"
        x: str = "world"
    """)
    out = r.stdout + r.stderr
    f811_count = out.count("F811")
    assert f811_count >= 2, f"Expected >=2 F811 violations, got {f811_count}.\nOutput: {out}"


# [pr_diff] fail_to_pass
def test_diagnostic_mentions_variable_names():
    """F811 diagnostic output identifies the redefined variable names."""
    r = _run_ruff("""\
        bar: int = 1
        bar: int = 2
        x: str = "hello"
        x: str = "world"
    """)
    out = r.stdout + r.stderr
    assert "bar" in out.lower(), f"Diagnostic should mention 'bar'.\nOutput: {out}"
    assert "`x`" in out, f"Diagnostic should mention `x`.\nOutput: {out}"


# [pr_diff] fail_to_pass
def test_fix_removes_first_annotated_assignment():
    """--fix mode removes the shadowed (first) annotated assignment."""
    _build_ruff()
    tmp = Path("/tmp/_ruff_fix_test.py")
    tmp.write_text("bar: int = 1\nbar: int = 2\n")
    subprocess.run(
        [RUFF_BIN, "check", "--select", "F811", "--preview", "--fix", "--no-cache", str(tmp)],
        capture_output=True, timeout=60,
    )
    fixed = tmp.read_text()
    assert "bar: int = 2" in fixed, f"Second assignment should remain.\nFixed: {fixed}"
    assert "bar: int = 1" not in fixed, f"First assignment should be removed.\nFixed: {fixed}"


# [pr_diff] fail_to_pass
def test_single_pair_flagged():
    """A single annotated redeclaration pair with a different variable name is also flagged."""
    r = _run_ruff("""\
        myvar: float = 3.14
        myvar: float = 2.72
    """)
    out = r.stdout + r.stderr
    assert "F811" in out, f"Single annotated pair should be flagged.\nOutput: {out}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — negative behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_plain_reassignment_not_flagged():
    """Plain reassignments (no annotations) are NOT flagged."""
    r = _run_ruff("""\
        y = 1
        y = 2
    """)
    out = r.stdout + r.stderr
    assert "F811" not in out, f"Plain reassignment should not trigger F811.\nOutput: {out}"


# [pr_diff] pass_to_pass
def test_mixed_assignment_not_flagged():
    """Mixed assignments (one annotated, one plain) are NOT flagged."""
    r = _run_ruff("""\
        z = 1
        z: int = 2
        w: int = 1
        w = 2
    """)
    out = r.stdout + r.stderr
    assert "F811" not in out, f"Mixed assignment should not trigger F811.\nOutput: {out}"


# [pr_diff] pass_to_pass
def test_used_between_not_flagged():
    """If the first binding is used between assignments, it is NOT flagged."""
    r = _run_ruff("""\
        a: int = 1
        print(a)
        a: int = 2
    """)
    out = r.stdout + r.stderr
    assert "F811" not in out, f"Used-between should not trigger F811.\nOutput: {out}"


# [pr_diff] pass_to_pass
def test_non_preview_mode_skips():
    """Non-preview mode does NOT flag annotated redeclarations."""
    r = _run_ruff("""\
        bar: int = 1
        bar: int = 2
    """, preview=False)
    out = r.stdout + r.stderr
    assert "F811" not in out, f"Non-preview mode should not flag annotated redeclarations.\nOutput: {out}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — upstream regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_f811_tests_pass():
    """Existing upstream F811 snapshot tests still pass (new annotated_assignment snapshot is excluded)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_linter", "--", "f811",
         "--skip", "annotated_assignment_redefinition", "--test-threads=1"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Existing F811 tests failed:\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_rule_file_not_truncated():
    """redefined_while_unused.rs must have substantial content (not stubbed out)."""
    lines = Path(RULE_FILE).read_text().splitlines()
    assert len(lines) > 200, f"Rule file has only {len(lines)} lines — likely truncated or stubbed"


# [static] pass_to_pass
def test_preview_file_not_truncated():
    """preview.rs must have substantial content (not stubbed out)."""
    lines = Path(PREVIEW_FILE).read_text().splitlines()
    assert len(lines) > 5, f"Preview file has only {len(lines)} lines — likely truncated or stubbed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ 29bf84e064567bde67320efd164a02b7322cc664
def test_no_local_imports_in_functions():
    """Rust imports go at the top of the file, never locally in functions."""
    src = Path(RULE_FILE).read_text()
    in_fn = False
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("fn ") or stripped.startswith("pub fn ") or stripped.startswith("pub(crate) fn "):
            in_fn = True
        elif in_fn and stripped.startswith("use "):
            assert False, f"Found local import inside function body: {stripped}"
        elif stripped == "}" and in_fn:
            in_fn = False


# [agent_config] pass_to_pass — AGENTS.md:79 @ 29bf84e064567bde67320efd164a02b7322cc664
def test_no_new_unsafe_patterns():
    """No new .unwrap(), panic!(), or unreachable!() calls added to the rule file."""
    r = subprocess.run(
        ["git", "show", "HEAD:crates/ruff_linter/src/rules/pyflakes/rules/redefined_while_unused.rs"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    base = r.stdout
    curr = Path(RULE_FILE).read_text()
    for pattern in [".unwrap()", "panic!(", "unreachable!("]:
        base_count = base.count(pattern)
        curr_count = curr.count(pattern)
        assert curr_count <= base_count, (
            f"New {pattern} added to rule file: {base_count} -> {curr_count}"
        )


# [agent_config] pass_to_pass — AGENTS.md:81 @ 29bf84e064567bde67320efd164a02b7322cc664
def test_expect_over_allow():
    """If lint suppression attributes are added, use #[expect()] not #[allow()]."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", RULE_FILE, PREVIEW_FILE],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    added_lines = [l for l in r.stdout.splitlines() if l.startswith("+") and not l.startswith("+++")]
    for line in added_lines:
        assert "#[allow(" not in line, (
            f"Use #[expect()] instead of #[allow()] per AGENTS.md: {line.strip()}"
        )
