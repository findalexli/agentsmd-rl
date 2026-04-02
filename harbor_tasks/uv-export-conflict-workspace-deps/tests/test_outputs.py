"""
Task: uv-export-conflict-workspace-deps
Repo: astral-sh/uv @ 3d4cb95c809aef28c4c527435948c0aae5c2f3d2
PR:   18635

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Source inspection because: Rust crate — cannot be imported or called from
Python. Building the full uv binary exceeds the 120s verifier timeout.
All regex patterns strip comments first to prevent comment-injection gaming.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/repo")
FILE = REPO / "crates" / "uv-resolver" / "src" / "lock" / "export" / "mod.rs"


def _strip_comments(text: str) -> str:
    """Remove Rust line comments (// ...) to prevent gaming via comment insertion."""
    return re.sub(r"//.*", "", text)


def _read_file() -> str:
    return FILE.read_text()


def _read_stripped() -> str:
    return _strip_comments(_read_file())


def _fix_region() -> str:
    """Extract the region between find_by_name(root_name) and if groups.prod().
    This is where the fix must insert conflict tracking."""
    src = _read_stripped()
    m_start = re.search(r"find_by_name\(root_name\)", src)
    assert m_start, "Cannot find find_by_name(root_name) — file structure changed"
    m_end = re.search(r"if groups\.prod\(\)", src[m_start.end() :])
    assert m_end, "Cannot find 'if groups.prod()' after find_by_name — file structure changed"
    return src[m_start.start() : m_start.end() + m_end.end()]


def _from_lock_body() -> str:
    """Full from_lock function body, comments stripped."""
    src = _read_stripped()
    m_start = re.search(r"fn from_lock", src)
    assert m_start, "Cannot find fn from_lock — file structure changed"
    m_end = re.search(r"\n    fn ", src[m_start.end() :])
    if m_end:
        return src[m_start.start() : m_start.end() + m_end.end()]
    return src[m_start.start() :]


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_compiles():
    """uv-resolver crate must compile (cargo check)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-resolver"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_root_package_conflict_tracking():
    """Root workspace package must be inserted into the conflicts map
    (via ConflictItem) between find_by_name and groups.prod().
    Without this, resolve_conflicts() drops all deps for package-level conflicts."""
    section = _fix_region()
    assert re.search(
        r"conflicts.*insert.*ConflictItem", section
    ), "Missing conflicts.insert(ConflictItem) for root package in the fix region"
    # The insert must reference the package name
    assert re.search(
        r"ConflictItem.*(dist\.id\.name|root_name)", section
    ), "ConflictItem must be created from dist.id.name or root_name"


# [pr_diff] fail_to_pass
def test_unconditional_marker_activation():
    """The ConflictItem must use MarkerTree::TRUE for unconditional activation —
    workspace member is always active when exported with --package."""
    section = _fix_region()
    assert "MarkerTree::TRUE" in section, (
        "Missing MarkerTree::TRUE in the fix region — "
        "root package activation must be unconditional"
    )


# [pr_diff] fail_to_pass
def test_safe_conflicts_access():
    """The conflicts map access must use safe Option handling (if let, match,
    .map, .and_then) — not .unwrap(). Combines PR fix pattern with CLAUDE.md:7-8."""
    section = _fix_region()
    assert re.search(
        r"(if let .* conflicts|match\s+conflicts|conflicts\.\s*(as_mut|as_ref|map|and_then))",
        section,
    ), "Missing safe Option handling for conflicts access in fix region"
    # Also verify the insert is real code, not just pattern noise
    assert re.search(r"insert.*ConflictItem", section), (
        "Safe access found but no actual ConflictItem insert"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_extras_conflict_tracking_preserved():
    """Existing conflict tracking for extras must still work —
    the extras loop already had conflicts.insert before the fix."""
    src = _read_stripped()
    # Find the extras loop and check it still has conflict tracking
    assert re.search(
        r"for extra in.*extra_names[\s\S]{0,2000}?conflicts.*insert.*ConflictItem",
        src,
    ), "Extras conflict tracking (conflicts.insert in extras loop) was removed"


# [pr_diff] pass_to_pass
def test_graph_traversal_intact():
    """from_lock must still add graph edges and queue dependencies for traversal."""
    body = _from_lock_body()
    assert "add_edge" in body, "graph.add_edge missing from from_lock"
    assert "push_back" in body, "queue.push_back missing from from_lock"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 3d4cb95c
def test_no_panic_unwrap_in_from_lock():
    """CLAUDE.md:7 — AVOID panic!, unreachable!, .unwrap() in from_lock."""
    body = _from_lock_body()
    assert not re.search(r"\.unwrap\(\)", body), ".unwrap() found in from_lock body"
    assert not re.search(r"panic!\(", body), "panic!() found in from_lock body"
    assert not re.search(r"unreachable!\(", body), "unreachable!() found in from_lock body"


# [static] pass_to_pass
def test_no_stub_macros():
    """Modified file must not contain todo!/unimplemented! stubs."""
    src = _read_stripped()
    assert not re.search(r"todo!\(", src), "todo!() macro found in source file"
    assert not re.search(r"unimplemented!\(", src), "unimplemented!() macro found"
