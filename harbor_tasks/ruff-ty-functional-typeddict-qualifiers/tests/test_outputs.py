"""
Task: ruff-ty-functional-typeddict-qualifiers
Repo: astral-sh/ruff @ 8c2a9cfbd6d22fdfff452d7e899595d4fa6ecc92
PR:   #24176

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = "/workspace/ruff"


@pytest.fixture(scope="session")
def ty_binary():
    """Build ty binary (incremental) and return its path."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty", "--quiet"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Failed to build ty:\n{r.stderr.decode()}"
    binary = Path(REPO) / "target" / "debug" / "ty"
    assert binary.exists(), f"ty binary not found at {binary}"
    return str(binary)


def ty_check(ty_binary: str, code: str) -> str:
    """Write code to a temp file and run ty check, return combined output."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        r = subprocess.run(
            [ty_binary, "check", f.name],
            capture_output=True,
            timeout=60,
        )
    return r.stdout.decode() + r.stderr.decode()


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified Rust code must compile."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic", "--quiet"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readonly_enforced_functional(ty_binary):
    """Assigning to a ReadOnly field in functional TypedDict must error."""
    # Test with multiple field types to avoid hardcoding
    output = ty_check(ty_binary, """\
from typing_extensions import TypedDict, ReadOnly

TD1 = TypedDict("TD1", {"id": ReadOnly[int], "name": str})
d1 = TD1(id=1, name="x")
d1["id"] = 2     # should error: read-only
d1["name"] = "y"  # fine: not read-only

TD2 = TypedDict("TD2", {"label": ReadOnly[str], "count": int})
d2 = TD2(label="a", count=0)
d2["label"] = "b"  # should error: read-only
d2["count"] = 5    # fine
""")
    # Should see exactly 2 invalid-assignment errors (one per ReadOnly field mutation)
    count = output.count("invalid-assignment")
    assert count >= 2, (
        f"Expected at least 2 invalid-assignment errors for ReadOnly fields, got {count}:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_notrequired_allows_omission(ty_binary):
    """Omitting a NotRequired field must not produce missing-typed-dict-key."""
    output = ty_check(ty_binary, """\
from typing_extensions import TypedDict, NotRequired

TD = TypedDict("TD", {"name": str, "year": NotRequired[int]})
ok1 = TD(name="x")
ok2 = TD(name="x", year=1)

TD2 = TypedDict("TD2", {"a": str, "b": NotRequired[str], "c": NotRequired[int]})
ok3 = TD2(a="hello")
ok4 = TD2(a="hello", b="world")
ok5 = TD2(a="hello", b="world", c=42)
""")
    assert "missing-typed-dict-key" not in output, (
        f"NotRequired field wrongly treated as required:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_required_enforced_total_false(ty_binary):
    """Required field in total=False TypedDict must produce missing-typed-dict-key when omitted."""
    output = ty_check(ty_binary, """\
from typing_extensions import TypedDict, Required

TD = TypedDict("TD", {"name": Required[str], "year": int}, total=False)
ok = TD(name="x")
bad1 = TD()
bad2 = TD(year=1)
""")
    # bad1 and bad2 should both trigger missing-typed-dict-key for "name"
    count = output.count("missing-typed-dict-key")
    assert count >= 2, (
        f"Expected at least 2 missing-typed-dict-key errors, got {count}:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_string_annotation_qualifier(ty_binary):
    """String annotation 'NotRequired[int]' must be respected as a qualifier."""
    output = ty_check(ty_binary, """\
from typing_extensions import TypedDict, NotRequired

TD = TypedDict("TD", {"required": str, "optional": "NotRequired[int]"})
ok = TD(required="hello")

TD2 = TypedDict("TD2", {"a": str, "b": "NotRequired[str]"})
ok2 = TD2(a="world")
""")
    assert "missing-typed-dict-key" not in output, (
        f"String NotRequired wrongly treated as required:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_string_annotation_required_total_false(ty_binary):
    """String 'Required[str]' in total=False must enforce requiredness."""
    output = ty_check(ty_binary, """\
from typing_extensions import TypedDict, Required

TD = TypedDict("TD", {"required": "Required[str]", "optional": int}, total=False)
ok = TD(required="hello")
bad = TD(optional=42)
""")
    assert "missing-typed-dict-key" in output, (
        f"String Required not enforced with total=False:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_basic_functional_typeddict(ty_binary):
    """Basic functional TypedDict without qualifiers must not regress."""
    output = ty_check(ty_binary, """\
from typing_extensions import TypedDict

Movie = TypedDict("Movie", {"name": str, "year": int})
m = Movie(name="The Matrix", year=1999)

Point = TypedDict("Point", {"x": float, "y": float})
p = Point(x=1.0, y=2.0)
""")
    error_lines = [l for l in output.splitlines() if "error" in l.lower()]
    assert not error_lines, f"Basic functional TypedDict has errors:\n{output}"


# [repo_tests] pass_to_pass
def test_class_based_qualifiers(ty_binary):
    """Class-based TypedDict with qualifiers must still work correctly."""
    output = ty_check(ty_binary, """\
from typing_extensions import TypedDict, ReadOnly, NotRequired

class Movie(TypedDict):
    name: str
    year: NotRequired[int]
    id: ReadOnly[int]

m = Movie(name="The Matrix", id=1)
m["id"] = 2  # should error: read-only
""")
    assert "invalid-assignment" in output, (
        f"Class-based ReadOnly not enforced:\n{output}"
    )


# [repo_tests] pass_to_pass
def test_total_false_without_qualifiers(ty_binary):
    """total=False without Required/NotRequired must allow omitting all fields."""
    output = ty_check(ty_binary, """\
from typing_extensions import TypedDict

TD = TypedDict("TD", {"a": str, "b": int}, total=False)
ok1 = TD()
ok2 = TD(a="x")
ok3 = TD(a="x", b=1)
""")
    assert "missing-typed-dict-key" not in output, (
        f"total=False fields wrongly treated as required:\n{output}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 8c2a9cfbd6d22fdfff452d7e899595d4fa6ecc92
def test_no_unwrap_panic():
    """New code must not introduce .unwrap(), panic!(), or unreachable!()."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added = [l for l in diff.splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    violations = [l for l in added
                  if any(p in l for p in [".unwrap()", "panic!(", "unreachable!("])]
    assert not violations, (
        "Found unwrap/panic in new code:\n" + "\n".join(violations)
    )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 8c2a9cfbd6d22fdfff452d7e899595d4fa6ecc92
def test_imports_at_top():
    """Rust imports must be at file top, not locally inside functions."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added = [l for l in diff.splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    # Local imports are indented `use` statements (inside fn bodies)
    local_imports = [l for l in added if "    use " in l]
    assert not local_imports, (
        "Found local imports (should be at top):\n" + "\n".join(local_imports)
    )


# [agent_config] pass_to_pass — AGENTS.md:81 @ 8c2a9cfbd6d22fdfff452d7e899595d4fa6ecc92
def test_expect_over_allow():
    """Must use #[expect()] over #[allow()] for Clippy lint suppression."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added = [l for l in diff.splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    violations = [l for l in added if "#[allow(" in l]
    assert not violations, (
        "Use #[expect()] instead of #[allow()]:\n" + "\n".join(violations)
    )


# [agent_config] pass_to_pass — AGENTS.md:84 @ 8c2a9cfbd6d22fdfff452d7e899595d4fa6ecc92
def test_salsa_node_access():
    """Methods accessing .node() must be #[salsa::tracked] for incrementality."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added = [l for l in diff.splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    node_calls = [l for l in added if ".node()" in l]
    if not node_calls:
        return  # No .node() calls added, nothing to check
    # If .node() calls were added, verify there's a #[salsa::tracked] nearby
    # This is a heuristic — check the full diff context for the attribute
    assert "#[salsa::tracked]" in diff, (
        "Added .node() call(s) without #[salsa::tracked]:\n" + "\n".join(node_calls)
    )
