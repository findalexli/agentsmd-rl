"""
Task: nextjs-turbopack-compact-span-hierarchy
Repo: vercel/next.js @ df886d4a2d36b63717f8aa5eae1147811ad025f8
PR:   91693

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

DB_FILE = Path("/workspace/next.js/turbopack/crates/turbo-persistence/src/db.rs")
MOD_FILE = Path("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs")

# Matches any tracing span macro whose string arg contains "compact"
COMPACT_SPAN_RE = re.compile(
    r"(?:info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)"
    r'\s*\([^)]*"[^"]*compact[^"]*"',
    re.IGNORECASE,
)

SPAN_MACRO_RE = re.compile(
    r"(?:info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)\s*\("
)


def _read_code_lines(path: Path) -> list[str]:
    """Read file, return non-comment lines."""
    lines = path.read_text().splitlines(keepends=True)
    return [l for l in lines if not l.lstrip().startswith("//")]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_compact_span_removed_from_db():
    """compact() in db.rs must no longer create its own tracing span."""
    code = "".join(_read_code_lines(DB_FILE))
    matches = COMPACT_SPAN_RE.findall(code)
    assert not matches, (
        f"Found compact-related span(s) still in db.rs: {[m.strip()[:80] for m in matches[:3]]}"
    )


# [pr_diff] fail_to_pass
def test_compact_span_added_to_mod():
    """A compact-related tracing span must exist in mod.rs (the call site)."""
    lines = MOD_FILE.read_text().splitlines(keepends=True)
    code_lines = [l for l in lines if not l.lstrip().startswith("//")]
    code = "".join(code_lines)

    # Strategy A: span macro with "compact" in its name
    if COMPACT_SPAN_RE.search(code):
        return

    # Strategy B: a tracing span macro within 15 lines of a .compact() call
    compact_call_indices = [
        i for i, l in enumerate(lines)
        if ".compact()" in l and not l.lstrip().startswith("//")
    ]
    for idx in compact_call_indices:
        window = "".join(
            l for l in lines[max(0, idx - 15) : idx + 5]
            if not l.lstrip().startswith("//")
        )
        if SPAN_MACRO_RE.search(window):
            return

    raise AssertionError("No compact-related tracing span found in mod.rs")


# [pr_diff] fail_to_pass
def test_root_span_in_mod():
    """A root span (parent: None) must exist in mod.rs for background work."""
    code = "".join(_read_code_lines(MOD_FILE))
    patterns = [
        r"(?:info_span!|trace_span!|debug_span!|span!)\s*\(\s*parent\s*:\s*None",
        r'parent\s*:\s*None\s*,\s*"',
        r"Span::none\(\)",
    ]
    for pat in patterns:
        if re.search(pat, code):
            return
    raise AssertionError("No root span (parent: None) found in mod.rs")


# [pr_diff] fail_to_pass
def test_sync_span_not_info_level():
    """'sync new files' span in db.rs must not be at info level."""
    src = DB_FILE.read_text()

    # Removed entirely is fine
    if '"sync new files"' not in src:
        return

    for line in src.splitlines():
        if '"sync new files"' not in line:
            continue
        assert not re.search(r"info_span!|warn_span!", line), (
            "'sync new files' still at info level or higher"
        )
        if re.search(r"trace_span!|debug_span!|Level::TRACE|Level::DEBUG", line):
            return

    # Check context around the span
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if '"sync new files"' in line:
            context = "\n".join(lines[max(0, i - 3) : i + 1])
            assert not re.search(r"info_span!|warn_span!", context), (
                "'sync new files' still at info level"
            )
            return

    raise AssertionError("Could not determine 'sync new files' span level")


# [pr_diff] fail_to_pass
def test_snapshot_and_persist_not_called_with_none():
    """snapshot_and_persist must not be called with None as first arg."""
    src = MOD_FILE.read_text()
    calls = re.findall(r"snapshot_and_persist\(\s*([^,)]+)", src)
    if not calls:
        # Function restructured / renamed — acceptable if "None" isn't passed
        assert "snapshot_and_persist" not in src, (
            "snapshot_and_persist exists but no calls found"
        )
        return
    for arg in calls:
        assert arg.strip() != "None", "snapshot_and_persist still called with None"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_compact_call_still_present():
    """The compaction logic must still invoke compact() on backing storage."""
    src = MOD_FILE.read_text()
    assert re.search(r"\.compact\(\)", src), "compact() call missing from mod.rs"


# [static] pass_to_pass
def test_mod_rs_not_stub():
    """mod.rs must have substantial content (not a stub replacement)."""
    line_count = len(MOD_FILE.read_text().splitlines())
    assert line_count > 2000, f"mod.rs has only {line_count} lines (possible stub)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:414 @ df886d4a
def test_no_formatting_issues():
    """No tabs or trailing whitespace in modified files (cargo fmt, CLAUDE.md:414)."""
    issues = []
    for path in [DB_FILE, MOD_FILE]:
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if "\t" in line and not line.lstrip().startswith("//"):
                issues.append(f"{path.name}:{i}: tab character")
            stripped = line.rstrip()
            if stripped != line and stripped:
                issues.append(f"{path.name}:{i}: trailing whitespace")
    assert not issues, f"Formatting issues: {issues[:5]}"
