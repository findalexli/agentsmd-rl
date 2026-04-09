"""
Task: ruff-em101-msg-shadow-fix
Repo: astral-sh/ruff @ 37f5d61595f88591b91b914aa05550644300ce19
PR:   24363

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import pytest
from pathlib import Path

REPO = "/workspace/ruff"
STRING_IN_EXCEPTION = f"{REPO}/crates/ruff_linter/src/rules/flake8_errmsg/rules/string_in_exception.rs"


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


def _apply_em101_fix(ruff_bin, code, tmp_path, suffix=""):
    """Write code to a temp file, apply EM101 unsafe fix, return fixed content."""
    test_file = tmp_path / f"em101{suffix}.py"
    test_file.write_text(code)
    subprocess.run(
        [ruff_bin, "check", "--select", "EM101", "--fix", "--unsafe-fixes",
         "--no-cache", str(test_file)],
        capture_output=True, text=True, timeout=30,
    )
    return test_file.read_text()


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
def test_em101_fix_no_shadow(ruff_bin, tmp_path):
    """When `msg` is already defined in the same scope, the EM101 fix must
    not shadow it — it should use `msg_0` (or another fresh name) instead.

    On the base commit, the fix always uses `msg`, clobbering the existing binding.
    """
    code = (
        'def f():\n'
        '    msg = "existing"\n'
        '    raise RuntimeError("boom")\n'
    )
    fixed = _apply_em101_fix(ruff_bin, code, tmp_path, suffix="_shadow")
    # The fix must assign to msg_0 (or msg_1, etc.), NOT bare msg
    lines = fixed.splitlines()
    new_assigns = [l.strip() for l in lines if "= " in l and l.strip().startswith("msg")]
    # There must be an assignment like `msg_0 = "boom"` (with underscore + digit)
    has_fresh = any(re.match(r'msg_\d+\s*=', a) for a in new_assigns)
    assert has_fresh, (
        f"Expected fresh binding (msg_0, msg_1, ...) to avoid shadowing 'msg', "
        f"but got:\n{fixed}"
    )


# [pr_diff] fail_to_pass
def test_em101_fix_no_shadow_varied(ruff_bin, tmp_path):
    """Multiple patterns where `msg` is already taken — fix must avoid shadowing.

    Tests varied inputs to prevent hardcoded constants.
    """
    cases = [
        # msg as a parameter — fix should use msg_0
        (
            'def handler(msg):\n'
            '    raise ValueError("invalid input")\n',
            "param",
            "invalid input",
        ),
        # msg defined earlier, raise in try block — fix should use msg_0
        (
            'def process():\n'
            '    msg = "context"\n'
            '    try:\n'
            '        raise TypeError("type error")\n'
            '    except TypeError:\n'
            '        return msg\n',
            "try_block",
            "type error",
        ),
        # both msg and msg_0 taken — fix should use msg_1
        (
            'def double():\n'
            '    msg = "first"\n'
            '    msg_0 = "second"\n'
            '    raise RuntimeError("third")\n',
            "double_taken",
            "third",
        ),
    ]
    for code, label, exc_text in cases:
        fixed = _apply_em101_fix(ruff_bin, code, tmp_path, suffix=f"_{label}")
        # Find the line that assigns the exception string to a variable
        assign_match = re.search(
            rf'(msg(?:_\d+)?)\s*=\s*"{re.escape(exc_text)}"', fixed
        )
        assert assign_match, (
            f"[{label}] Expected exception string to be extracted to a variable, "
            f"got:\n{fixed}"
        )
        var_name = assign_match.group(1)
        assert re.match(r'msg_\d+$', var_name), (
            f"[{label}] Expected fresh binding (msg_N) but got '{var_name}', "
            f"in:\n{fixed}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_em101_fix_uses_msg_when_available(ruff_bin, tmp_path):
    """When `msg` is NOT already defined, the fix should still use plain `msg`."""
    cases = [
        (
            'def simple():\n'
            '    raise RuntimeError("simple error")\n',
            "simple",
        ),
        (
            'def another():\n'
            '    x = 1\n'
            '    raise ValueError("bad value")\n',
            "no_msg",
        ),
    ]
    for code, label in cases:
        fixed = _apply_em101_fix(ruff_bin, code, tmp_path, suffix=f"_{label}")
        # Should use plain `msg = ...` (no suffix)
        assert re.search(r'^\s+msg\s*=\s*"', fixed, re.MULTILINE), (
            f"[{label}] Expected plain 'msg' variable when name is available, "
            f"got:\n{fixed}"
        )
        # Must NOT use msg_0 when msg is free
        assert not re.search(r'\bmsg_\d+\s*=', fixed), (
            f"[{label}] Should not use msg_0/msg_1 when 'msg' is available, "
            f"got:\n{fixed}"
        )


# [repo_tests] pass_to_pass
def test_em101_snapshot_tests():
    """Upstream EM snapshot tests must pass."""
    r = subprocess.run(
        ["cargo", "test", "--package", "ruff_linter", "--", "flake8_errmsg"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
        env={
            **__import__("os").environ,
            "INSTA_FORCE_PASS": "1",
            "INSTA_UPDATE": "always",
        },
    )
    assert r.returncode == 0, (
        f"EM snapshot tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 37f5d61595f88591b91b914aa05550644300ce19
def test_no_unwrap_or_panic():
    """Modified rule file must not introduce panic!(), unreachable!(), or .unwrap()."""
    content = Path(STRING_IN_EXCEPTION).read_text()
    for pattern, label in [
        (r'\bunwrap\(\)', '.unwrap()'),
        (r'\bpanic!\s*\(', 'panic!()'),
        (r'\bunreachable!\s*\(', 'unreachable!()'),
    ]:
        matches = re.findall(pattern, content)
        assert not matches, (
            f"Found {label} in string_in_exception.rs — "
            f"AGENTS.md line 79 says to avoid these patterns"
        )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 37f5d61595f88591b91b914aa05550644300ce19
def test_rust_imports_at_top():
    """Rust imports must be at the top of the file, not locally inside functions."""
    content = Path(STRING_IN_EXCEPTION).read_text()
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
