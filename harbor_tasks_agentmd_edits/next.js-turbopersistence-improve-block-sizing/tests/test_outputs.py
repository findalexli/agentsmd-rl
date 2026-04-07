"""
Task: next.js-turbopersistence-improve-block-sizing
Repo: vercel/next.js @ d7e06519cb98b1685830bcbb1dd4955cb159061d
PR:   89497

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
CRATE = Path(REPO) / "turbopack" / "crates" / "turbo-persistence"
SRC = CRATE / "src"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """turbo-persistence crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "turbo-persistence"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_max_small_value_size_reduced():
    """MAX_SMALL_VALUE_SIZE must be 4096 (reduced from 64KB)."""
    content = (SRC / "constants.rs").read_text()
    match = re.search(
        r"pub\s+const\s+MAX_SMALL_VALUE_SIZE\s*:\s*usize\s*=\s*(.+?);",
        content,
    )
    assert match, "constants.rs must define MAX_SMALL_VALUE_SIZE"
    expr = match.group(1).strip()
    # Evaluate the expression: could be 4096, 4 * 1024, etc.
    assert "64" not in expr, (
        f"MAX_SMALL_VALUE_SIZE should be ~4096, not 64KB. Got: {expr}"
    )
    # Parse the numeric value
    val = eval(expr.replace("usize", ""))
    assert val == 4096, f"MAX_SMALL_VALUE_SIZE should be 4096, got {val}"


# [pr_diff] fail_to_pass
def test_min_small_value_block_size_constant():
    """MIN_SMALL_VALUE_BLOCK_SIZE constant (8KB) must exist in constants.rs."""
    content = (SRC / "constants.rs").read_text()
    match = re.search(
        r"pub\s+const\s+MIN_SMALL_VALUE_BLOCK_SIZE\s*:\s*usize\s*=\s*(.+?);",
        content,
    )
    assert match, "constants.rs must define MIN_SMALL_VALUE_BLOCK_SIZE"
    expr = match.group(1).strip()
    val = eval(expr.replace("usize", ""))
    assert val == 8192, f"MIN_SMALL_VALUE_BLOCK_SIZE should be 8192, got {val}"


# [pr_diff] fail_to_pass
def test_max_value_block_count_constant():
    """MAX_VALUE_BLOCK_COUNT constant must exist for u16 overflow protection."""
    content = (SRC / "constants.rs").read_text()
    match = re.search(
        r"pub\s+const\s+MAX_VALUE_BLOCK_COUNT\s*:\s*usize\s*=",
        content,
    )
    assert match, "constants.rs must define MAX_VALUE_BLOCK_COUNT"
    # The value should be u16::MAX / 2 = 32767
    assert "u16::MAX" in content[match.start():match.start() + 200] or "32767" in content[match.start():match.start() + 200], (
        "MAX_VALUE_BLOCK_COUNT should be derived from u16::MAX"
    )


# [pr_diff] fail_to_pass
def test_key_block_entry_meta_overhead_updated():
    """KEY_BLOCK_ENTRY_META_OVERHEAD must be 20 (updated from 8)."""
    content = (SRC / "static_sorted_file_builder.rs").read_text()
    match = re.search(
        r"const\s+KEY_BLOCK_ENTRY_META_OVERHEAD\s*:\s*usize\s*=\s*(\d+)",
        content,
    )
    assert match, "static_sorted_file_builder.rs must define KEY_BLOCK_ENTRY_META_OVERHEAD"
    val = int(match.group(1))
    assert val == 20, f"KEY_BLOCK_ENTRY_META_OVERHEAD should be 20, got {val}"


# [pr_diff] fail_to_pass
def test_value_block_count_tracker_module():
    """A value_block_count_tracker module must exist with tracker struct."""
    tracker_path = SRC / "value_block_count_tracker.rs"
    assert tracker_path.exists(), (
        "src/value_block_count_tracker.rs must exist"
    )
    content = tracker_path.read_text()
    # Must define the struct
    assert "struct ValueBlockCountTracker" in content, (
        "value_block_count_tracker.rs must define ValueBlockCountTracker struct"
    )
    # Must have track method
    assert re.search(r"fn\s+track\b", content), (
        "ValueBlockCountTracker must have a track method"
    )
    # Must have is_full method
    assert re.search(r"fn\s+is_full\b", content), (
        "ValueBlockCountTracker must have an is_full method"
    )
    # Must reference MAX_VALUE_BLOCK_COUNT
    assert "MAX_VALUE_BLOCK_COUNT" in content, (
        "ValueBlockCountTracker must use MAX_VALUE_BLOCK_COUNT"
    )


# [pr_diff] fail_to_pass
def test_collector_uses_tracker():
    """Collector must integrate ValueBlockCountTracker for overflow protection."""
    content = (SRC / "collector.rs").read_text()
    assert "ValueBlockCountTracker" in content, (
        "collector.rs must import/use ValueBlockCountTracker"
    )
    assert "value_block_tracker" in content or "value_block_count_tracker" in content, (
        "Collector must have a ValueBlockCountTracker field"
    )
    # The is_ready method must check is_full
    assert "is_full" in content, (
        "Collector must check tracker.is_full() in its readiness check"
    )


# [pr_diff] fail_to_pass
def test_small_value_block_emit_logic():
    """write_value_blocks must use MIN_SMALL_VALUE_BLOCK_SIZE (not MAX)."""
    content = (SRC / "static_sorted_file_builder.rs").read_text()
    # Must import/use MIN_SMALL_VALUE_BLOCK_SIZE
    assert "MIN_SMALL_VALUE_BLOCK_SIZE" in content, (
        "static_sorted_file_builder.rs must use MIN_SMALL_VALUE_BLOCK_SIZE"
    )
    # The old MAX_SMALL_VALUE_BLOCK_SIZE should NOT be defined locally
    assert not re.search(
        r"const\s+MAX_SMALL_VALUE_BLOCK_SIZE\s*:\s*usize",
        content,
    ), "MAX_SMALL_VALUE_BLOCK_SIZE should be removed (renamed to MIN_SMALL_VALUE_BLOCK_SIZE)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — README documentation update
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_documents_value_types():
    """README must document INLINE, SMALL, MEDIUM, BLOB value types with size boundaries."""
    readme = CRATE / "README.md"
    content = readme.read_text()
    # Must mention all four value types with size info
    assert "INLINE" in content, "README must document INLINE value type"
    assert "SMALL" in content, "README must document SMALL value type"
    assert "MEDIUM" in content, "README must document MEDIUM value type"
    # Check size boundaries are documented
    assert "4096" in content or "4 kB" in content or "4 KB" in content or "4kB" in content, (
        "README must document the 4KB small/medium boundary"
    )
    assert "8 bytes" in content or "8 B" in content or "≤ 8" in content, (
        "README must document the 8-byte inline threshold"
    )


# [pr_diff] fail_to_pass
def test_readme_has_tradeoff_table():
    """README must have a value type trade-off table with compression/access/compaction info."""
    readme = CRATE / "README.md"
    content = readme.read_text()
    # Must have a table (markdown pipe syntax) with trade-off info
    assert "trade-off" in content.lower() or "tradeoff" in content.lower(), (
        "README must have a trade-offs section"
    )
    # Table must cover key dimensions
    assert "Compaction" in content or "compaction" in content, (
        "Trade-off table must discuss compaction behavior"
    )
    assert "Access cost" in content or "access cost" in content.lower(), (
        "Trade-off table must discuss access cost"
    )
    # Must be a markdown table (has pipe characters in table rows)
    table_lines = [l for l in content.split("\n") if l.strip().startswith("|")]
    assert len(table_lines) >= 4, (
        f"README must have a trade-off table with at least 4 rows, found {len(table_lines)} pipe-rows"
    )
