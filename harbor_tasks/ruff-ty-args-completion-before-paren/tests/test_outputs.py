"""
Task: ruff-ty-args-completion-before-paren
Repo: astral-sh/ruff @ d81266252aaf0820346d55edbed79c4f25ba13d2
PR:   astral-sh/ruff#24167 (fixes astral-sh/ty#3087)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/ruff"
COMPLETION_RS = Path(REPO) / "crates/ty_ide/src/completion.rs"

# Injected INSIDE the mod tests block to share scope with completion_test_builder.
INJECTED_TESTS = r"""
    // Injected by test harness — exercises the panic path from ty#3087
    #[test]
    fn injected_no_panic_list_subscript_before_paren() {
        let builder = completion_test_builder(
            r#"
list[int]<CURSOR>()
"#,
        );
        let _ = builder.skip_keywords().skip_builtins().skip_auto_import().build();
    }

    #[test]
    fn injected_no_panic_dict_subscript_before_paren() {
        let builder = completion_test_builder(
            r#"
dict[str, int]<CURSOR>()
"#,
        );
        let _ = builder.skip_keywords().skip_builtins().skip_auto_import().build();
    }

    #[test]
    fn injected_no_panic_tuple_subscript_before_paren() {
        let builder = completion_test_builder(
            r#"
tuple[int, str]<CURSOR>()
"#,
        );
        let _ = builder.skip_keywords().skip_builtins().skip_auto_import().build();
    }
"""


def _find_mod_tests_close(content: str) -> int:
    """Return the index of the closing } of the top-level mod tests block."""
    idx = content.find("mod tests {")
    assert idx != -1, (
        f"Could not find 'mod tests {{' in {COMPLETION_RS}. "
        f"File has {len(content)} chars."
    )
    brace_pos = content.index("{", idx)
    depth = 0
    for i in range(brace_pos, len(content)):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    raise AssertionError("Unbalanced braces in mod tests block")


@pytest.fixture(scope="module", autouse=True)
def inject_rust_tests():
    """Inject test functions inside mod tests, restore after the session."""
    assert COMPLETION_RS.exists(), f"Source file not found: {COMPLETION_RS}"
    original = COMPLETION_RS.read_text()
    close = _find_mod_tests_close(original)
    patched = original[:close] + INJECTED_TESTS + original[close:]
    COMPLETION_RS.write_text(patched)
    yield
    COMPLETION_RS.write_text(original)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified code must compile (including injected tests)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_ide", "--tests", "--quiet"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_panic_list_subscript_before_paren():
    """list[int]<CURSOR>() must not panic — exercises the exact buggy code path."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "--",
         "injected_no_panic_list_subscript_before_paren", "--exact"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Test panicked or failed:\n{out[-2000:]}"


# [pr_diff] fail_to_pass
def test_no_panic_dict_subscript_before_paren():
    """dict[str, int]<CURSOR>() must not panic — variant with different subscript."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "--",
         "injected_no_panic_dict_subscript_before_paren", "--exact"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Test panicked or failed:\n{out[-2000:]}"


# [pr_diff] fail_to_pass
def test_no_panic_tuple_subscript_before_paren():
    """tuple[int, str]<CURSOR>() must not panic — third subscript variant."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "--",
         "injected_no_panic_tuple_subscript_before_paren", "--exact"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Test panicked or failed:\n{out[-2000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_completion_tests_pass():
    """Upstream completion tests must still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "--",
         "completion", "--skip", "injected_"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Completion tests failed:\n{out[-2000:]}"


# [repo_tests] pass_to_pass
def test_argument_completion_still_works():
    """Argument completion tests must still pass when cursor IS inside arguments."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "--",
         "argument", "--skip", "injected_"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Argument completion tests failed:\n{out[-2000:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ d81266252aaf0820346d55edbed79c4f25ba13d2
def test_no_panic_patterns_in_diff():
    """No .unwrap(), panic!(), or unreachable!() in added lines (AGENTS.md:79)."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "crates/ty_ide/src/completion.rs"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added_lines = [
        l for l in diff.splitlines()
        if l.startswith("+") and not l.startswith("+++")
    ]
    for pattern in [".unwrap()", "panic!(", "unreachable!("]:
        violations = [l for l in added_lines if pattern in l]
        assert not violations, (
            f"{pattern} found in added lines:\n" + "\n".join(violations)
        )


# [agent_config] pass_to_pass — AGENTS.md:76 @ d81266252aaf0820346d55edbed79c4f25ba13d2
def test_no_local_use_statements():
    """Rust imports must be at top of file, not locally in functions (AGENTS.md:76)."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "crates/ty_ide/src/completion.rs"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added_lines = [
        l for l in diff.splitlines()
        if l.startswith("+") and not l.startswith("+++")
    ]
    local_imports = [
        l for l in added_lines
        if l[1:].lstrip().startswith("use ") and l[1:] != l[1:].lstrip()
    ]
    assert not local_imports, (
        "Local use statements found (imports must be at top of file):\n"
        + "\n".join(local_imports)
    )


# [agent_config] pass_to_pass — AGENTS.md:81 @ d81266252aaf0820346d55edbed79c4f25ba13d2
def test_no_allow_lint_suppression():
    """Use #[expect()] over #[allow()] for lint suppression (AGENTS.md:81)."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "crates/ty_ide/src/completion.rs"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added_lines = [
        l for l in diff.splitlines()
        if l.startswith("+") and not l.startswith("+++")
    ]
    allow_lines = [l for l in added_lines if "#[allow(" in l]
    assert not allow_lines, (
        "#[allow()] found in added lines — use #[expect()] instead:\n"
        + "\n".join(allow_lines)
    )
