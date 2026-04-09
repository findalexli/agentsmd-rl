"""
Task: sglang-hisparse-lru-policy-fix
Repo: sglang @ 93109cc89be31809e45886377c55099983effa22
PR:   22170

Fix for LRU (Least Recently Used) ordering in hisparse cache kernel.
The bug was in how the LRU slots were ordered after cache misses were loaded.

The fix:
1. Moves the LRU write-back block to AFTER total_misses is computed
2. Adds proper handling for miss slots: misses are placed right before hits in the LRU order
3. The remaining truly stale evictables stay at the LRU front

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/sglang"
TARGET_FILE = f"{REPO}/python/sglang/jit_kernel/csrc/hisparse.cuh"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET_FILE).exists(), f"Target file not found: {TARGET_FILE}"


# [static] pass_to_pass
def test_file_is_not_empty():
    """Target file must have content."""
    content = Path(TARGET_FILE).read_text()
    assert len(content) > 1000, "Target file seems truncated"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_lru_writeback_after_miss_calculation():
    """
    The LRU write-back block must come AFTER total_misses is computed.
    In the buggy version, the write-back happened before miss counting and didn't
    account for misses in the LRU ordering.
    """
    content = Path(TARGET_FILE).read_text()

    # Find the two key patterns:
    # 1. "total_misses = NUM_TOP_K - s_total_hits - s_newest_hit;"
    # 2. The start of the LRU write-back block: "// Write back LRU order"

    miss_calc_pattern = r'total_misses\s*=\s*NUM_TOP_K\s+-\s+s_total_hits\s+-\s+s_newest_hit;'
    lru_writeback_pattern = r'// Write back LRU order: evictables at front \(LRU\), hits at back \(MRU\)\.'

    # Find all occurrences
    miss_calc_matches = list(re.finditer(miss_calc_pattern, content))
    lru_writeback_matches = list(re.finditer(lru_writeback_pattern, content))

    assert len(miss_calc_matches) > 0, "Missing total_misses calculation"
    assert len(lru_writeback_matches) > 0, "Missing LRU write-back block"

    # The LRU write-back must come AFTER the miss calculation
    miss_calc_pos = miss_calc_matches[-1].start()  # Use the last occurrence (the real one)
    lru_writeback_pos = lru_writeback_matches[0].start()  # Use the first occurrence

    assert lru_writeback_pos > miss_calc_pos, (
        "LRU write-back must come AFTER total_misses is calculated. "
        "In the buggy version, write-back happened before misses were counted."
    )


# [pr_diff] fail_to_pass
def test_miss_slot_handling():
    """
    The LRU write-back must properly handle miss slots.
    Misses (just loaded from host) should be placed right before hits in the LRU order.
    This is the key fix in the PR.
    """
    content = Path(TARGET_FILE).read_text()

    # Check for the three-way conditional that handles misses
    # The fix adds: if (i < total_misses) { ... misses ... }
    #            else if (i < total_evictable) { ... evictables ... }
    #            else { ... hits ... }

    # Look for the pattern that indicates proper miss handling
    miss_handling_pattern = r'if\s*\(\s*i\s*<\s*total_misses\s*\)'

    matches = list(re.finditer(miss_handling_pattern, content))
    assert len(matches) > 0, (
        "Missing miss slot handling. The fix requires a conditional to handle "
        "misses separately from evictables: 'if (i < total_misses)'"
    )


# [pr_diff] fail_to_pass
def test_miss_slot_placement():
    """
    Misses should be placed right before hits in the LRU order.
    Check for: req_lru_slots[total_evictable - total_misses + i] = ...
    """
    content = Path(TARGET_FILE).read_text()

    # The fix places misses at: total_evictable - total_misses + i
    # This positions them right before the hits in the LRU order
    miss_placement_pattern = r'req_lru_slots\[\s*total_evictable\s+-\s+total_misses\s+\+\s+i\s*\]'

    matches = list(re.finditer(miss_placement_pattern, content))
    assert len(matches) > 0, (
        "Miss slots should be placed at 'total_evictable - total_misses + i'. "
        "This positions misses right before hits in the LRU order."
    )


# [pr_diff] fail_to_pass
def test_evictable_slot_placement():
    """
    Remaining evictables should be placed at the LRU front.
    Check for: req_lru_slots[i - total_misses] = ...
    """
    content = Path(TARGET_FILE).read_text()

    # The fix places remaining evictables at: i - total_misses
    # This shifts evictables to make room for misses
    evictable_placement_pattern = r'req_lru_slots\[\s*i\s+-\s+total_misses\s*\]'

    matches = list(re.finditer(evictable_placement_pattern, content))
    assert len(matches) > 0, (
        "Evictables should be placed at 'i - total_misses' to make room for miss slots."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub verification
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_kernel_has_substantial_content():
    """The kernel function should have substantial implementation."""
    content = Path(TARGET_FILE).read_text()

    # Count the load_cache_to_device_buffer_kernel function
    kernel_start = content.find('__global__ void load_cache_to_device_buffer_kernel')
    assert kernel_start > 0, "Missing kernel function"

    # Count lines in the kernel (approximate by finding the template declaration after it)
    template_pattern = r'template\s*<\s*int\s+BLOCK_SIZE[^>]+>\s*\nvoid\s+load_cache_to_device_buffer\s*\('
    template_match = re.search(template_pattern, content[kernel_start:])

    if template_match:
        kernel_end = kernel_start + template_match.start()
        kernel_content = content[kernel_start:kernel_end]
    else:
        kernel_content = content[kernel_start:kernel_start + 5000]

    # Kernel should be substantial
    kernel_lines = len(kernel_content.split('\n'))
    assert kernel_lines > 100, f"Kernel seems too short ({kernel_lines} lines), might be stubbed"


# [static] pass_to_pass
def test_not_stub():
    """The fix should not be a stub - it must contain the actual LRU logic."""
    content = Path(TARGET_FILE).read_text()

    # Check for key elements that indicate real implementation
    required_patterns = [
        r'__syncthreads\(\)',  # CUDA synchronization
        r's_total_hits',       # Shared memory hit counter
        r'req_lru_slots',     # LRU slot array
        r's_lru_slots_out',    # Shared memory output buffer
    ]

    for pattern in required_patterns:
        assert re.search(pattern, content), f"Missing required element: {pattern}"


# [static] pass_to_pass
def test_lru_writeback_block_exists():
    """The LRU write-back block must exist with proper comments."""
    content = Path(TARGET_FILE).read_text()

    # Look for the write-back comment
    writeback_comment = "// Write back LRU order: evictables at front (LRU), hits at back (MRU)."
    assert writeback_comment in content, "Missing LRU write-back comment"

    # Look for the three categories mentioned in comments
    miss_comment = "// Misses: just loaded from host, place right before hits"
    evictable_comment = "// Remaining evictables: truly stale, dest at LRU front"
    hits_comment = "// Hits: source at forward end, dest at MRU back"

    # At least the miss comment must exist (the key fix)
    assert miss_comment in content or "// Misses:" in content, (
        "Missing comment about miss handling - this is the key part of the fix"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base AND fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_hisparse_cuh_structure():
    """hisparse.cuh must have substantial structure (pass_to_pass)."""
    content = Path(TARGET_FILE).read_text()

    # Basic structure checks
    assert "__global__ void load_cache_to_device_buffer_kernel" in content, (
        "Missing kernel function declaration"
    )
    assert "__syncthreads()" in content, "Missing CUDA synchronization"
    assert "req_lru_slots" in content, "Missing req_lru_slots array"

    # Count lines - should be substantial (300+ lines for a real implementation)
    lines = content.split("\n")
    assert len(lines) > 300, f"hisparse.cuh seems truncated ({len(lines)} lines)"


# [repo_tests] pass_to_pass
def test_repo_ruff_syntax_check():
    """Python files in jit_kernel must have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Install may fail if already installed, that's okay

    r = subprocess.run(
        ["ruff", "check", "--select=E9,F63,F7,F82", f"{REPO}/python/sglang/jit_kernel/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff syntax check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_black_format_check():
    """hisparse.py must be properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    r = subprocess.run(
        ["black", "--check", f"{REPO}/python/sglang/jit_kernel/hisparse.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stderr}"
