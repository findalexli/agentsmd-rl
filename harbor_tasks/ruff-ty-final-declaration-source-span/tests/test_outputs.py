"""
Task: ruff-ty-final-declaration-source-span
Repo: astral-sh/ruff @ 929eb5238c82bfadad4549ff526f02efc0163dd0
PR:   #24194

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
TY = None  # built lazily


def _build_ty():
    """Build the ty binary and return its path."""
    global TY
    if TY is not None:
        return TY
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo build --bin ty failed:\n{r.stderr.decode()[-2000:]}"
    TY = f"{REPO}/target/debug/ty"
    return TY


def _run_ty(code: str, filename: str = "test.py") -> str:
    """Write code to a temp file, run ty check on it, return combined output."""
    ty = _build_ty()
    with tempfile.NamedTemporaryFile(mode="w", suffix=f"_{filename}", delete=False) as f:
        f.write(code)
        f.flush()
        r = subprocess.run(
            [ty, "check", f.name],
            capture_output=True,
            timeout=120,
        )
    return r.stdout.decode() + r.stderr.decode()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified Rust code must compile."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic", "--quiet"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_method_assignment_shows_final_source():
    """Diagnostic for method assignment to Final attr must show 'declared as Final here'."""
    output = _run_ty("""\
from typing import Final

class C:
    x: Final[int] = 1

    def f(self):
        self.x = 2
""")
    assert "invalid-assignment" in output, f"Expected invalid-assignment diagnostic:\n{output}"
    assert re.search(r"(?i)declared as.*Final.*here|Final.*declared.*here", output), \
        f"Missing Final declaration annotation:\n{output}"


# [pr_diff] fail_to_pass
def test_init_reassignment_shows_final_source():
    """__init__ assignment after class-body value shows Final source + 'already has a value'."""
    output = _run_ty("""\
from typing import Final

class C:
    x: Final[int] = 1

    def __init__(self):
        self.x = 2
""")
    assert "invalid-assignment" in output, f"Expected invalid-assignment diagnostic:\n{output}"
    assert "already has a value" in output, f"Missing 'already has a value' message:\n{output}"
    assert re.search(r"(?i)declared as.*Final.*here|Final.*declared.*here", output), \
        f"Missing Final declaration annotation:\n{output}"


# [pr_diff] fail_to_pass
def test_inherited_final_shows_parent_annotation():
    """Inherited Final attribute assignment shows declaration site from base class."""
    output = _run_ty("""\
from typing import Final

class Base:
    x: Final[int] = 1

class Child(Base):
    def f(self):
        self.x = 2
""")
    assert "invalid-assignment" in output, f"Expected invalid-assignment diagnostic:\n{output}"
    assert re.search(r"(?i)declared as.*Final.*here|Final.*declared.*here", output), \
        f"Missing Final declaration annotation for inherited attr:\n{output}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_nonfinal_attr_no_final_annotation():
    """Regular (non-Final) attribute assignment must NOT mention 'declared as Final'."""
    output = _run_ty("""\
class D:
    y: int = 10

    def g(self):
        self.y = 20
""")
    assert not re.search(r"(?i)declared as.*Final.*here|Final.*declared.*here", output), \
        f"Non-Final attribute incorrectly shows Final annotation:\n{output}"


# [repo_tests] pass_to_pass
def test_final_without_value_still_diagnosed():
    """Module-level Final without value must still report final-without-value."""
    output = _run_ty("""\
from typing import Final

UNINITIALIZED: Final[int]
INITIALIZED: Final[int] = 42
""")
    assert "final-without-value" in output, f"Missing final-without-value diagnostic:\n{output}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ 929eb5238c82
def test_no_local_imports_in_functions():
    """Rust imports must be at the top of the file, not inside function bodies."""
    fa_path = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs"
    types_path = Path(REPO) / "crates/ty_python_semantic/src/types.rs"

    for fpath in [fa_path, types_path]:
        if not fpath.exists():
            continue
        content = fpath.read_text()
        in_fn = False
        brace_depth = 0
        for line in content.splitlines():
            stripped = line.strip()
            if re.match(r"(pub\s+)?(fn|async\s+fn)\s+", stripped):
                in_fn = True
                brace_depth = 0
            if in_fn:
                brace_depth += stripped.count("{") - stripped.count("}")
                if brace_depth > 0 and re.match(r"use\s+", stripped):
                    assert False, f"Found import inside function body in {fpath.name}: {stripped}"
                if brace_depth <= 0 and "{" in line:
                    in_fn = False


# [agent_config] pass_to_pass — AGENTS.md:79 @ 929eb5238c82
def test_no_new_unsafe_patterns():
    """No new .unwrap(), panic!(), or unreachable!() calls in modified files."""
    modified_files = [
        Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs",
        Path(REPO) / "crates/ty_python_semantic/src/types.rs",
    ]
    patterns = [".unwrap()", "panic!", "unreachable!"]

    for fpath in modified_files:
        if not fpath.exists():
            continue
        rel = str(fpath.relative_to(REPO))
        # Get base version
        r = subprocess.run(
            ["git", "show", f"HEAD:{rel}"],
            cwd=REPO,
            capture_output=True,
        )
        base_content = r.stdout.decode() if r.returncode == 0 else ""
        curr_content = fpath.read_text()

        for pat in patterns:
            base_count = base_content.count(pat)
            curr_count = curr_content.count(pat)
            assert curr_count <= base_count, \
                f"New {pat} added in {fpath.name} ({base_count} -> {curr_count})"


# [agent_config] pass_to_pass — AGENTS.md:81 @ 929eb5238c82
def test_no_allow_lint_attributes():
    """New #[allow(...)] attributes should use #[expect(...)] instead."""
    modified_files = [
        Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs",
        Path(REPO) / "crates/ty_python_semantic/src/types.rs",
    ]

    for fpath in modified_files:
        if not fpath.exists():
            continue
        rel = str(fpath.relative_to(REPO))
        r = subprocess.run(
            ["git", "show", f"HEAD:{rel}"],
            cwd=REPO,
            capture_output=True,
        )
        base_content = r.stdout.decode() if r.returncode == 0 else ""
        curr_content = fpath.read_text()

        base_allows = len(re.findall(r"#\[allow\(", base_content))
        curr_allows = len(re.findall(r"#\[allow\(", curr_content))
        assert curr_allows <= base_allows, \
            f"New #[allow(...)] in {fpath.name} — use #[expect(...)] instead ({base_allows} -> {curr_allows})"


# [agent_config] pass_to_pass — AGENTS.md:84 @ 929eb5238c82
def test_salsa_node_access_tracking():
    """Methods accessing .node() must be #[salsa::tracked] for incrementality."""
    modified_files = [
        Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs",
        Path(REPO) / "crates/ty_python_semantic/src/types.rs",
    ]

    for fpath in modified_files:
        if not fpath.exists():
            continue
        content = fpath.read_text()
        lines = content.splitlines()

        for i, line in enumerate(lines):
            stripped = line.strip()
            # Skip comments and string literals
            if stripped.startswith("//") or stripped.startswith("///"):
                continue
            if ".node()" in stripped:
                # Check if the enclosing function has #[salsa::tracked]
                # Walk backwards to find the fn definition
                found_tracked = False
                for j in range(i - 1, max(i - 20, -1), -1):
                    prev = lines[j].strip()
                    if "salsa::tracked" in prev:
                        found_tracked = True
                        break
                    if re.match(r"(pub\s+)?(fn|async\s+fn)\s+", prev):
                        break
                if not found_tracked:
                    # Check if .node() is on the fn definition line itself or
                    # the fn has the attribute on a preceding line
                    fn_line = None
                    for j in range(i, max(i - 30, -1), -1):
                        if re.match(r"\s*(pub\s+)?(fn|async\s+fn)\s+", lines[j]):
                            fn_line = j
                            break
                    if fn_line is not None:
                        for j in range(fn_line - 1, max(fn_line - 10, -1), -1):
                            if "salsa::tracked" in lines[j]:
                                found_tracked = True
                                break
                            if lines[j].strip() and not lines[j].strip().startswith("#["):
                                break

                # Only fail for NEW .node() calls (not in base)
                if not found_tracked:
                    rel = str(fpath.relative_to(REPO))
                    r = subprocess.run(
                        ["git", "show", f"HEAD:{rel}"],
                        cwd=REPO,
                        capture_output=True,
                    )
                    base_content = r.stdout.decode() if r.returncode == 0 else ""
                    if stripped not in base_content:
                        assert False, \
                            f"New .node() call at {fpath.name}:{i+1} without #[salsa::tracked]: {stripped}"
