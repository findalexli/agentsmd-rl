"""
Task: ruff-ty-callable-slash-star-ordering
Repo: astral-sh/ruff @ 8106a4b299fa63e9f7b91b14eccbd70e7a064a9f
PR:   24497

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
DISPLAY_RS = Path(REPO) / "crates/ty_python_semantic/src/types/display.rs"

# Snapshot assertions to inject into the signature_display test function.
# These test the bugfix: '/' must appear before '*' when both separators are needed.
_INJECTED_ASSERTIONS = """\

        // [harness] positional-only + keyword-only: slash before star
        assert_snapshot!(
            display_signature(
                &db,
                [
                    Parameter::positional_only(Some(Name::new_static("a"))),
                    Parameter::keyword_only(Name::new_static("x")),
                    Parameter::keyword_only(Name::new_static("y")),
                ],
                Some(Type::none(&db))
            ),
            @"(a, /, *, x, y) -> None"
        );

        // [harness] multiple positional-only then keyword-only
        assert_snapshot!(
            display_signature(
                &db,
                [
                    Parameter::positional_only(Some(Name::new_static("p"))),
                    Parameter::positional_only(Some(Name::new_static("q"))),
                    Parameter::keyword_only(Name::new_static("k")),
                ],
                Some(Type::none(&db))
            ),
            @"(p, q, /, *, k) -> None"
        );
"""

# Marker in the Rust test file used to locate the insertion point.
_INSERTION_MARKER = '@"(x, *, y) -> None"'


def _ensure_test_cases_injected():
    """Inject harness snapshot assertions into the Rust test file if not already present."""
    content = DISPLAY_RS.read_text()
    # Check both assertions — skip if already present (gold patch or agent added them)
    if "(a, /, *, x, y) -> None" in content and "(p, q, /, *, k) -> None" in content:
        return
    # Find insertion point after the existing (x, *, y) -> None assertion
    marker_pos = content.find(_INSERTION_MARKER)
    assert marker_pos != -1, (
        f"Cannot find insertion marker {_INSERTION_MARKER!r} in display.rs"
    )
    # Find the closing ");" of that assert_snapshot! block
    close_pos = content.find(");", marker_pos)
    assert close_pos != -1, "Cannot find closing ');' after insertion marker"
    insert_at = close_pos + 2
    content = content[:insert_at] + _INJECTED_ASSERTIONS + content[insert_at:]
    DISPLAY_RS.write_text(content)


def _extract_display_impl() -> str:
    """Extract the FmtDetailed<DisplayParameters> impl block from display.rs."""
    source = DISPLAY_RS.read_text()
    impl_start = source.find("impl<'db> FmtDetailed<'db> for DisplayParameters")
    assert impl_start != -1, "DisplayParameters FmtDetailed impl not found"
    # Find the next top-level impl or mod block
    for boundary in ["\nimpl<", "\nimpl ", "\nmod "]:
        end = source.find(boundary, impl_start + 10)
        if end != -1:
            return source[impl_start:end]
    return source[impl_start:]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """Modified ty_python_semantic crate compiles successfully."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass tests — verified on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — cargo clippy
def test_repo_clippy():
    """ty_python_semantic crate passes clippy lints (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--all-targets", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass — cargo fmt check
def test_repo_fmt():
    """Code passes formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — unit tests in types::display module
def test_repo_display_tests():
    """types::display module unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "--test-threads=4", "types::display"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Display tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_slash_star_display():
    """Callable with positional-only + keyword-only params displays '/' before '*'."""
    _ensure_test_cases_injected()
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "signature_display"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, (
        f"Display snapshot tests failed (expected '/' before '*'):\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_display_ordering_structure():
    """In the display loop, is_positional_only() check must precede is_keyword_only()."""
    source = DISPLAY_RS.read_text()
    # Find the FmtDetailed impl for DisplayParameters
    impl_start = source.find("impl<'db> FmtDetailed<'db> for DisplayParameters")
    assert impl_start != -1, "DisplayParameters FmtDetailed impl not found"

    # Find the 'for parameter in parameters' loop within the impl
    loop_start = source.find("for parameter in parameters", impl_start)
    assert loop_start != -1, "Parameter display loop not found"

    # Limit search to next ~200 lines of the loop body
    loop_section = source[loop_start:loop_start + 3000]

    pos_only_pos = loop_section.find("parameter.is_positional_only()")
    kw_only_pos = loop_section.find("parameter.is_keyword_only()")

    assert pos_only_pos != -1, "is_positional_only() check not found in display loop"
    assert kw_only_pos != -1, "is_keyword_only() check not found in display loop"
    assert pos_only_pos < kw_only_pos, (
        f"is_positional_only() (offset {pos_only_pos}) must come before "
        f"is_keyword_only() (offset {kw_only_pos}) in the display loop — "
        f"'/' separator must be emitted before '*'"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 8106a4b299fa63e9f7b91b14eccbd70e7a064a9f
def test_no_panic_unwrap_in_display_fn():
    """No panic!/unwrap in the DisplayParameters FmtDetailed impl (AGENTS.md:79)."""
    impl_body = _extract_display_impl()
    for i, line in enumerate(impl_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "panic!(" not in stripped, f"panic! at line {i}: {stripped}"
        assert ".unwrap()" not in stripped, f".unwrap() at line {i}: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:76 @ 8106a4b299fa63e9f7b91b14eccbd70e7a064a9f
def test_no_local_imports_in_display_fn():
    """No local use statements inside the display impl (AGENTS.md:76)."""
    impl_body = _extract_display_impl()
    for i, line in enumerate(impl_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert not stripped.startswith("use "), (
            f"Local import at line {i}: {stripped}"
        )


# [agent_config] pass_to_pass — AGENTS.md:81 @ 8106a4b299fa63e9f7b91b14eccbd70e7a064a9f
def test_no_allow_lint_suppression():
    """Prefer #[expect()] over #[allow()] for lint suppression (AGENTS.md:81)."""
    impl_body = _extract_display_impl()
    for i, line in enumerate(impl_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "#[allow(" not in stripped, (
            f"Use #[expect()] instead of #[allow()] at line {i}: {stripped}"
        )
