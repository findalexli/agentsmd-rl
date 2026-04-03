"""
Task: ruff-ty-functional-typeddict-qualifiers
Repo: astral-sh/ruff @ 8c2a9cfbd6d22fdfff452d7e899595d4fa6ecc92
PR:   #24176

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/ruff"

# Files modified by the PR (where agent changes are expected)
CHANGED_FILES = [
    "crates/ty_python_semantic/src/types/typed_dict.rs",
    "crates/ty_python_semantic/src/types/infer.rs",
    "crates/ty_python_semantic/src/types/infer/builder.rs",
    "crates/ty_python_semantic/src/types/infer/builder/annotation_expression.rs",
    "crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs",
]


def _build_ty():
    """Build the ty binary once (cached by file existence)."""
    bin_path = Path(REPO) / "target" / "debug" / "ty"
    if not bin_path.exists():
        r = subprocess.run(
            ["cargo", "build", "--bin", "ty"],
            cwd=REPO, capture_output=True, timeout=600,
        )
        assert r.returncode == 0, f"cargo build --bin ty failed:\n{r.stderr.decode()[-3000:]}"
    assert bin_path.exists(), "ty binary not found after build"
    return str(bin_path)


def _run_ty(code: str) -> str:
    """Write code to a temp file, run ty check, return combined output."""
    ty = _build_ty()
    tmp = Path("/tmp/ty_test")
    tmp.mkdir(exist_ok=True)
    test_file = tmp / "test_input.py"
    test_file.write_text(textwrap.dedent(code))
    r = subprocess.run(
        [ty, "check", str(test_file)],
        cwd=REPO, capture_output=True, timeout=120,
    )
    return r.stdout.decode() + r.stderr.decode()


def _get_added_lines() -> str:
    """Return only the '+' lines from git diff for changed files."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--unified=0", "--"] + CHANGED_FILES,
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added = []
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])  # strip leading +
    return "\n".join(added)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty_python_semantic crate must compile."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-3000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readonly_enforced_functional():
    """Assigning to a ReadOnly field in functional TypedDict must error."""
    output = _run_ty("""\
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
    count = output.count("invalid-assignment")
    assert count >= 2, (
        f"Expected at least 2 invalid-assignment errors for ReadOnly fields, got {count}:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_notrequired_allows_omission():
    """Omitting a NotRequired field must not produce missing-typed-dict-key."""
    output = _run_ty("""\
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
def test_required_enforced_total_false():
    """Required field in total=False TypedDict must produce missing-typed-dict-key when omitted."""
    output = _run_ty("""\
        from typing_extensions import TypedDict, Required

        TD = TypedDict("TD", {"name": Required[str], "year": int}, total=False)
        ok = TD(name="x")
        bad1 = TD()
        bad2 = TD(year=1)
    """)
    count = output.count("missing-typed-dict-key")
    assert count >= 2, (
        f"Expected at least 2 missing-typed-dict-key errors, got {count}:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_string_annotation_qualifier():
    """String annotation 'NotRequired[int]' must be respected as a qualifier."""
    output = _run_ty("""\
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
def test_string_annotation_required_total_false():
    """String 'Required[str]' in total=False must enforce requiredness."""
    output = _run_ty("""\
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
def test_basic_functional_typeddict():
    """Basic functional TypedDict without qualifiers must not regress."""
    output = _run_ty("""\
        from typing_extensions import TypedDict

        Movie = TypedDict("Movie", {"name": str, "year": int})
        m = Movie(name="The Matrix", year=1999)

        Point = TypedDict("Point", {"x": float, "y": float})
        p = Point(x=1.0, y=2.0)
    """)
    error_lines = [l for l in output.splitlines() if "error" in l.lower()]
    assert not error_lines, f"Basic functional TypedDict has errors:\n{output}"


# [repo_tests] pass_to_pass
def test_class_based_qualifiers():
    """Class-based TypedDict with qualifiers must still work correctly."""
    output = _run_ty("""\
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
def test_total_false_without_qualifiers():
    """total=False without Required/NotRequired must allow omitting all fields."""
    output = _run_ty("""\
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
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 8c2a9cfbd6d22fdfff452d7e899595d4fa6ecc92
def test_no_unwrap_panic():
    """New code must not introduce .unwrap(), panic!(), or unreachable!()."""
    added = _get_added_lines()
    if not added.strip():
        return  # no changes yet (base commit) — pass
    unwrap_hits = re.findall(r"\.unwrap\(\)", added)
    panic_hits = re.findall(r"\bpanic!\s*\(", added)
    unreachable_hits = re.findall(r"\bunreachable!\s*\(", added)
    violations = []
    if unwrap_hits:
        violations.append(f".unwrap() x{len(unwrap_hits)}")
    if panic_hits:
        violations.append(f"panic!() x{len(panic_hits)}")
    if unreachable_hits:
        violations.append(f"unreachable!() x{len(unreachable_hits)}")
    assert not violations, (
        f"Unsafe patterns in new code (AGENTS.md:79): {', '.join(violations)}"
    )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 8c2a9cfbd6d22fdfff452d7e899595d4fa6ecc92
def test_imports_at_top():
    """New code must not add `use` imports inside function bodies."""
    added = _get_added_lines()
    if not added.strip():
        return  # no changes yet (base commit) — pass
    local_use = re.findall(r"^(\s{12,}use\s+.+;)", added, re.MULTILINE)
    assert not local_use, (
        f"Local `use` imports found inside functions (AGENTS.md:76):\n"
        + "\n".join(local_use)
    )


# [agent_config] pass_to_pass — AGENTS.md:81 @ 8c2a9cfbd6d22fdfff452d7e899595d4fa6ecc92
def test_expect_over_allow():
    """New lint suppressions must use #[expect()] not #[allow()]."""
    added = _get_added_lines()
    if not added.strip():
        return  # no changes yet (base commit) — pass
    allow_hits = re.findall(r"#\[allow\(", added)
    assert not allow_hits, (
        f"Use #[expect()] instead of #[allow()] for lint suppression "
        f"(AGENTS.md:81): found {len(allow_hits)} occurrence(s)"
    )


# [agent_config] pass_to_pass — AGENTS.md:84 @ 8c2a9cfbd6d22fdfff452d7e899595d4fa6ecc92
def test_salsa_node_access():
    """Methods accessing .node() must be #[salsa::tracked] for incrementality."""
    added = _get_added_lines()
    if not added.strip():
        return  # no changes yet (base commit) — pass
    node_calls = re.findall(r"\.node\(\)", added)
    if not node_calls:
        return  # No .node() calls added, nothing to check
    # If .node() calls were added, verify there's a #[salsa::tracked] nearby
    r = subprocess.run(
        ["git", "diff", "HEAD", "--"] + CHANGED_FILES,
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    assert "#[salsa::tracked]" in diff, (
        f"Added .node() call(s) without #[salsa::tracked] (AGENTS.md:84)"
    )
