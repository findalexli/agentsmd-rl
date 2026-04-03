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


def _strip_comments(text: str) -> str:
    """Remove single-line // comments from Rust source."""
    return re.sub(r"//[^\n]*", "", text)


def _read_stripped(path: Path) -> str:
    """Read file and strip // comments."""
    return _strip_comments(path.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_compact_span_removed_from_db():
    """compact() in db.rs must no longer create its own tracing span."""
    src = _read_stripped(DB_FILE)
    # Look for any tracing span macro with "compact" in its string argument.
    # We search line-by-line in the compact() function region to avoid
    # regex issues with nested parentheses across multiple lines.
    in_compact_fn = False
    brace_depth = 0
    for line in src.splitlines():
        stripped = line.strip()
        # Detect the compact function definition
        if re.search(r"fn\s+compact\b", stripped):
            in_compact_fn = True
            brace_depth = 0
        if in_compact_fn:
            brace_depth += stripped.count("{") - stripped.count("}")
            # Check for any span macro with "compact" on this line
            if re.search(
                r"(?:info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)",
                stripped,
            ) and re.search(r'"[^"]*compact[^"]*"', stripped, re.IGNORECASE):
                assert False, f"Found compact-related span still in db.rs: {stripped[:80]}"
            # Also check if span macro + compact string are on separate lines
            # by looking for span macro assignment with compact in the string arg
            if brace_depth <= 0 and in_compact_fn and "{" in src[:src.find(stripped) + 1]:
                # We've exited the function
                pass
    # Also do a broad multiline search as a safety net
    # Match span macros where "compact" appears in the same macro invocation
    for m in re.finditer(
        r"(?:info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)\s*\(",
        src,
    ):
        # Find the matching close paren (handle nesting)
        start = m.end()
        depth = 1
        i = start
        while i < len(src) and depth > 0:
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
            i += 1
        macro_body = src[start : i - 1] if depth == 0 else src[start : start + 200]
        if re.search(r'"[^"]*compact[^"]*"', macro_body, re.IGNORECASE):
            # This span macro references "compact" — it shouldn't be in db.rs
            assert False, f"Found compact-related span in db.rs: {macro_body[:80]}"


# [pr_diff] fail_to_pass
def test_compact_span_added_to_mod():
    """A compact-related tracing span must exist in mod.rs (the call site)."""
    src = _read_stripped(MOD_FILE)
    # Search for span macros and check if any reference "compact"
    for m in re.finditer(
        r"(?:info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)\s*\(",
        src,
    ):
        start = m.end()
        depth = 1
        i = start
        while i < len(src) and depth > 0:
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
            i += 1
        macro_body = src[start : i - 1] if depth == 0 else src[start : start + 300]
        if re.search(r'"[^"]*compact[^"]*"', macro_body, re.IGNORECASE):
            return  # Found a compact span in mod.rs

    # Fallback: check if there's a span macro within 15 lines of .compact() call
    lines = src.splitlines()
    for idx, line in enumerate(lines):
        if ".compact()" in line:
            window = "\n".join(lines[max(0, idx - 15) : idx + 5])
            if re.search(
                r"(?:info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)\s*\(",
                window,
            ):
                return
    assert False, "No compact-related tracing span found in mod.rs"


# [pr_diff] fail_to_pass
def test_root_span_in_mod():
    """A root span (parent: None) must exist in mod.rs for background work."""
    src = _read_stripped(MOD_FILE)
    patterns = [
        r"(?:info_span!|trace_span!|debug_span!|span!)\s*\(\s*parent\s*:\s*None",
        r"parent\s*:\s*None\s*,\s*\"",
        r"Span::none\(\)",
    ]
    for pat in patterns:
        if re.search(pat, src):
            return
    assert False, "No root span (parent: None) found in mod.rs"


# [pr_diff] fail_to_pass
def test_sync_span_not_info_level():
    """'sync new files' span in db.rs must not be at info level."""
    src = DB_FILE.read_text()

    # Removed entirely is acceptable
    if '"sync new files"' not in src:
        return

    # Find lines with the span string and check the macro level
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if '"sync new files"' not in line:
            continue
        # Check this line and a few lines before for the macro
        context = "\n".join(lines[max(0, i - 3) : i + 1])
        context_no_comments = _strip_comments(context)
        assert not re.search(r"info_span!|warn_span!", context_no_comments), (
            "'sync new files' still at info level or higher"
        )
        if re.search(r"trace_span!|debug_span!|Level::TRACE|Level::DEBUG", context_no_comments):
            return

    assert False, "Could not determine 'sync new files' span level"


# [pr_diff] fail_to_pass
def test_snapshot_and_persist_not_called_with_none():
    """snapshot_and_persist must not be called with None as first arg."""
    src = _read_stripped(MOD_FILE)
    # Find all calls and extract the first argument
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
