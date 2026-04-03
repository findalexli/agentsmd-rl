"""
Task: nextjs-turbo-persistence-block-heuristics
Repo: vercel/next.js @ d7e06519cb98b1685830bcbb1dd4955cb159061d
PR:   89497

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
CRATE = f"{REPO}/turbopack/crates/turbo-persistence"
SRC = f"{CRATE}/src"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — basic file integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_constants_file_valid():
    """constants.rs must exist and contain core constant definitions."""
    src = Path(f"{SRC}/constants.rs").read_text()
    # These constants existed before the PR and must still be present
    assert "MAX_MEDIUM_VALUE_SIZE" in src, "Missing MAX_MEDIUM_VALUE_SIZE constant"
    assert "MAX_SMALL_VALUE_SIZE" in src, "Missing MAX_SMALL_VALUE_SIZE constant"
    assert "MAX_INLINE_VALUE_SIZE" in src, "Missing MAX_INLINE_VALUE_SIZE constant"
    assert "KEY_BLOCK_CACHE_SIZE" in src, "Missing KEY_BLOCK_CACHE_SIZE constant"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (constant values)
# ---------------------------------------------------------------------------

def _parse_const(src: str, name: str) -> int:
    """Extract the integer value of a Rust const from source text."""
    # Match patterns like: pub const NAME: usize = 4096;
    # Also handles expressions like: u16::MAX as usize / 2
    pattern = rf'(?:pub\s+)?const\s+{re.escape(name)}\s*:\s*\w+\s*=\s*(.+?)\s*;'
    m = re.search(pattern, src)
    assert m, f"Could not find const {name} in source"
    expr = m.group(1).strip()
    # Handle simple numeric: 4096, 8 * 1024, 64 * 1024 * 1024
    # Handle u16::MAX as usize / 2
    expr = re.sub(r'u16::MAX\s+as\s+\w+', '65535', expr)
    expr = re.sub(r'u16::MAX', '65535', expr)
    return int(eval(expr))


# [pr_diff] fail_to_pass
def test_small_value_threshold_reduced():
    """MAX_SMALL_VALUE_SIZE must be reduced to 4096 (was 64KB-1)."""
    src = Path(f"{SRC}/constants.rs").read_text()
    val = _parse_const(src, "MAX_SMALL_VALUE_SIZE")
    assert val == 4096, (
        f"MAX_SMALL_VALUE_SIZE should be 4096, got {val}. "
        "Values up to 4 KiB are small; larger ones become medium values."
    )


# [pr_diff] fail_to_pass
def test_min_small_value_block_size():
    """MIN_SMALL_VALUE_BLOCK_SIZE must exist and equal 8192 (8 KiB)."""
    src = Path(f"{SRC}/constants.rs").read_text()
    assert "MIN_SMALL_VALUE_BLOCK_SIZE" in src, (
        "Missing MIN_SMALL_VALUE_BLOCK_SIZE constant — small value blocks should "
        "be emitted once they accumulate at least this many bytes."
    )
    val = _parse_const(src, "MIN_SMALL_VALUE_BLOCK_SIZE")
    assert val == 8192, f"MIN_SMALL_VALUE_BLOCK_SIZE should be 8192, got {val}"


# [pr_diff] fail_to_pass
def test_max_value_block_count():
    """MAX_VALUE_BLOCK_COUNT must exist to prevent u16 block index overflow."""
    src = Path(f"{SRC}/constants.rs").read_text()
    assert "MAX_VALUE_BLOCK_COUNT" in src, (
        "Missing MAX_VALUE_BLOCK_COUNT constant — needed to prevent exceeding "
        "the u16 block index limit in SST files."
    )
    val = _parse_const(src, "MAX_VALUE_BLOCK_COUNT")
    # u16::MAX / 2 = 32767, to account for 50/50 merge-and-split during compaction
    assert 30000 <= val <= 33000, (
        f"MAX_VALUE_BLOCK_COUNT should be approximately u16::MAX/2 (~32767), got {val}"
    )


# [pr_diff] fail_to_pass
def test_key_block_entry_meta_overhead():
    """KEY_BLOCK_ENTRY_META_OVERHEAD must be updated to 20 (was 8)."""
    src = Path(f"{SRC}/static_sorted_file_builder.rs").read_text()
    pattern = r'const\s+KEY_BLOCK_ENTRY_META_OVERHEAD\s*:\s*\w+\s*=\s*(\d+)\s*;'
    m = re.search(pattern, src)
    assert m, "Could not find KEY_BLOCK_ENTRY_META_OVERHEAD constant"
    val = int(m.group(1))
    assert val == 20, (
        f"KEY_BLOCK_ENTRY_META_OVERHEAD should be 20 (actual worst-case overhead), got {val}"
    )


# [pr_diff] fail_to_pass
def test_value_block_count_tracker_module():
    """A ValueBlockCountTracker module must exist with track/is_full/reset methods."""
    # Check the module file exists
    tracker_path = Path(f"{SRC}/value_block_count_tracker.rs")
    assert tracker_path.exists(), (
        "Missing value_block_count_tracker.rs — needed to track block count "
        "and prevent exceeding the u16 block index limit."
    )
    src = tracker_path.read_text()
    # Must have the core methods
    assert "fn track" in src, "ValueBlockCountTracker must have a track() method"
    assert "fn is_full" in src, "ValueBlockCountTracker must have an is_full() method"
    assert "fn reset" in src, "ValueBlockCountTracker must have a reset() method"
    # Must reference the max block count constant
    assert "MAX_VALUE_BLOCK_COUNT" in src, (
        "ValueBlockCountTracker should check against MAX_VALUE_BLOCK_COUNT"
    )


# [pr_diff] fail_to_pass
def test_collector_overflow_protection():
    """Collector must use ValueBlockCountTracker for block count overflow protection."""
    src = Path(f"{SRC}/collector.rs").read_text()
    # The collector must import/use the tracker
    assert "ValueBlockCountTracker" in src or "value_block_count_tracker" in src, (
        "Collector must use ValueBlockCountTracker to prevent block index overflow"
    )
    # The should_write / is_full check must be present
    assert "is_full" in src, (
        "Collector must check is_full() to stop accumulating entries before "
        "exceeding the block index limit"
    )


# [pr_diff] fail_to_pass
def test_builder_uses_min_threshold():
    """Static sorted file builder must use MIN threshold for small value block emission."""
    src = Path(f"{SRC}/static_sorted_file_builder.rs").read_text()
    assert "MIN_SMALL_VALUE_BLOCK_SIZE" in src, (
        "Builder should use MIN_SMALL_VALUE_BLOCK_SIZE for small value block emission "
        "(blocks are emitted once they reach the minimum, not capped at a maximum)."
    )
    # The old MAX_SMALL_VALUE_BLOCK_SIZE should no longer be used
    assert "MAX_SMALL_VALUE_BLOCK_SIZE" not in src, (
        "Builder should no longer use MAX_SMALL_VALUE_BLOCK_SIZE — "
        "replaced by MIN_SMALL_VALUE_BLOCK_SIZE (emit at minimum, not cap at maximum)."
    )


# ---------------------------------------------------------------------------
# Config/documentation update tests (config_edit) — README changes
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must mention all four value types (not just INLINE and BLOB)
    assert "small" in readme_lower and "medium" in readme_lower, (
        "README should document SMALL and MEDIUM value types in addition to INLINE and BLOB"
    )

    # Check size boundaries are documented
    # INLINE: ≤ 8 bytes
    assert re.search(r'inline.*?8\s*b', readme_lower) or re.search(r'≤\s*8', readme), (
        "README should document INLINE values as ≤ 8 bytes"
    )
    # SMALL: up to 4096 / 4 kB
    assert re.search(r'4096|4\s*k[bB]|4,?096', readme), (
        "README should document SMALL value upper bound as 4 KiB (4096 bytes)"
    )
    # MEDIUM: up to 64 MB
    assert re.search(r'64\s*MB', readme, re.IGNORECASE), (
        "README should document MEDIUM value upper bound as 64 MB"
    )
    # BLOB: > 64 MB
    assert re.search(r'blob.*?>.*?64\s*MB|>\s*64\s*MB.*?blob', readme, re.IGNORECASE | re.DOTALL), (
        "README should document BLOB values as > 64 MB"
    )


# [config_edit] fail_to_pass

    # The trade-off table should compare compression, compaction, access cost
    assert "trade-off" in readme.lower() or "tradeoff" in readme.lower(), (
        "README should have a section about value type trade-offs"
    )
    # Table should have key comparison dimensions
    assert "compaction" in readme.lower(), (
        "Trade-off table should compare compaction behavior across value types"
    )
    assert "access cost" in readme.lower() or "access" in readme.lower(), (
        "Trade-off table should compare access cost across value types"
    )
    assert "compression" in readme.lower(), (
        "Trade-off table should compare compression behavior across value types"
    )
    # Should be a markdown table (contains pipe characters in table rows)
    table_rows = [line for line in readme.split('\n') if '|' in line and ('inline' in line.lower() or 'small' in line.lower() or 'blob' in line.lower())]
    assert len(table_rows) >= 2, (
        "Trade-off section should contain a markdown table comparing value types"
    )
