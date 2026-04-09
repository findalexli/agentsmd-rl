"""
Tests for sglang hisparse LRU eviction policy fix.

The hisparse kernel manages a hot buffer cache with LRU eviction.
The bug: the LRU write-back ordering was computed before total_misses
was known, so newly loaded entries (misses) were lumped together with
truly stale entries. This meant newly loaded cache lines could be
immediately evicted on the next access.

The fix moves the write-back after total_misses computation and adds
3-way categorization: misses (protected), stale evictables (evict first),
hits (MRU).

Since this is a CUDA kernel, tests use text analysis (permitted last
resort for GPU kernels / CUDA C++).
"""

import os
import re

REPO = "/workspace/sglang"
HISPARSE = os.path.join(REPO, "python/sglang/jit_kernel/csrc/hisparse.cuh")


def _read_file():
    with open(HISPARSE) as f:
        return f.read()


def _find_total_misses_line(lines):
    """Find the line index where total_misses is computed."""
    for i, line in enumerate(lines):
        if re.search(
            r"total_misses\s*=\s*NUM_TOP_K\s*-\s*s_total_hits\s*-\s*s_newest_hit",
            line,
        ):
            return i
    return None


def _find_first_req_lru_slots(lines):
    """Find the first line that assigns to req_lru_slots[]."""
    for i, line in enumerate(lines):
        if re.search(r"req_lru_slots\[", line) and "=" in line:
            return i
    return None


def _find_all_req_lru_slots(lines):
    """Find all lines that assign to req_lru_slots[]."""
    result = []
    for i, line in enumerate(lines):
        if re.search(r"req_lru_slots\[", line) and "=" in line:
            result.append(i)
    return result


# ---- Fail-to-pass tests ----


def test_lru_writeback_after_miss_count():
    """
    The LRU write-back (req_lru_slots assignments) must appear AFTER
    total_misses is computed. Before the fix, write-back happened too
    early, before misses were counted.
    """
    lines = _read_file().splitlines()

    miss_line = _find_total_misses_line(lines)
    assert miss_line is not None, "total_misses assignment not found"

    first_writeback = _find_first_req_lru_slots(lines)
    assert first_writeback is not None, "No req_lru_slots assignments found"

    assert first_writeback > miss_line, (
        f"LRU write-back at line {first_writeback + 1} must come after "
        f"total_misses computation at line {miss_line + 1}"
    )


def test_lru_writeback_distinguishes_misses():
    """
    The write-back block must reference total_misses to separate
    newly-loaded entries from truly stale ones. Before the fix,
    both categories were treated identically as 'evictables'.
    """
    lines = _read_file().splitlines()

    miss_line = _find_total_misses_line(lines)
    assert miss_line is not None

    # Collect the scoped block after total_misses that writes req_lru_slots
    block_text = []
    in_scope = False
    brace_depth = 0
    for i in range(miss_line, len(lines)):
        line = lines[i]
        if "req_lru_slots[" in line and not in_scope:
            in_scope = True
        if in_scope:
            block_text.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and "}" in line:
                break

    block = "\n".join(block_text)
    assert "total_misses" in block, (
        "LRU write-back must reference total_misses to distinguish "
        "misses from stale entries. Before the fix, both were lumped "
        "together as 'evictables'."
    )


def test_no_early_lru_writeback():
    """
    The buggy code had an LRU write-back block BEFORE total_misses
    was computed. After the fix, there must be no req_lru_slots
    assignments before the total_misses line.
    """
    lines = _read_file().splitlines()

    miss_line = _find_total_misses_line(lines)
    assert miss_line is not None

    early_assignments = []
    for i in range(miss_line):
        if re.search(r"req_lru_slots\[", lines[i]) and "=" in lines[i]:
            early_assignments.append(i)

    assert len(early_assignments) == 0, (
        f"Found req_lru_slots assignments at lines "
        f"{[i + 1 for i in early_assignments]}, before total_misses at "
        f"line {miss_line + 1}. The old write-back block should have been removed."
    )


def test_three_way_eviction_categories():
    """
    The fixed code must use 3-way branching in the LRU write-back:
    1. Misses (just loaded from host, placed near MRU end)
    2. Remaining evictables (truly stale, at LRU front)
    3. Hits (at MRU back)

    The buggy code only had 2-way branching (evictables, hits).
    """
    lines = _read_file().splitlines()

    miss_line = _find_total_misses_line(lines)
    assert miss_line is not None

    # Collect lines from total_misses to the end of the write-back block
    block_lines = []
    in_block = False
    brace_depth = 0
    for i in range(miss_line, len(lines)):
        line = lines[i]
        if "Write back LRU order" in line or "req_lru_slots[" in line:
            in_block = True
        if in_block:
            block_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0 and "}" in line:
                break

    block = "\n".join(block_lines)

    # Must have 3-way branching (if / else if / else)
    assert "else if" in block or "else\n" in block or "} else if" in block, (
        "LRU write-back must use 3-way branching (if/else if/else) "
        "to separate misses, stale entries, and hits. The buggy code "
        "only had 2-way (if/else)."
    )

    # Must reference both total_misses and total_evictable
    assert "total_misses" in block, "Write-back must reference total_misses"
    assert "total_evictable" in block, "Write-back must reference total_evictable"


# ---- Pass-to-pass tests ----


def test_file_exists():
    """The hisparse kernel source file must exist."""
    assert os.path.isfile(HISPARSE), f"File not found: {HISPARSE}"


def test_kernel_function_present():
    """The main kernel function must still be present."""
    content = _read_file()
    assert "load_cache_to_device_buffer_kernel" in content, (
        "load_cache_to_device_buffer_kernel function must exist"
    )
    assert "__global__" in content, "CUDA kernel declaration must exist"
