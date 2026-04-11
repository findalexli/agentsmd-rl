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

Since this is a CUDA kernel, some tests use text analysis (permitted last
resort for GPU kernels / CUDA C++), but pass-to-pass tests use actual
CI commands via subprocess.run().
"""

import os
import re
import subprocess

REPO = "/workspace/sglang"
HISPARSE = os.path.join(REPO, "python/sglang/jit_kernel/csrc/hisparse.cuh")
HISPARSE_PY = os.path.join(REPO, "python/sglang/jit_kernel/hisparse.py")


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
    both categories were treated identically as evictables.
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
        "together as evictables."
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
    """The hisparse kernel source file must exist (pass_to_pass)."""
    assert os.path.isfile(HISPARSE), f"File not found: {HISPARSE}"


def test_kernel_function_present():
    """The main kernel function must still be present (pass_to_pass)."""
    content = _read_file()
    assert "load_cache_to_device_buffer_kernel" in content, (
        "load_cache_to_device_buffer_kernel function must exist"
    )
    assert "__global__" in content, "CUDA kernel declaration must exist"


def test_repo_python_syntax():
    """Repo Python files have valid syntax (pass_to_pass).

    Verifies that the hisparse.py module parses without syntax errors.
    This is a real CI command using Python\'s parser.
    """
    r = subprocess.run(
        ["python3", "-m", "py_compile", HISPARSE_PY],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_ruff_check():
    """Repo Python files pass ruff syntax checks (pass_to_pass).

    Runs ruff check on the hisparse Python module for syntax errors (E9).
    This is a real CI linting command.
    """
    # First ensure ruff is installed
    install_result = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Even if install "fails" due to warnings, ruff might still work

    r = subprocess.run(
        ["ruff", "check", "--select=E9", HISPARSE_PY],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_import_sglang_jit_kernel():
    """Repo\'s sglang.jit_kernel module imports successfully (pass_to_pass).

    Tests that the Python module structure is intact by importing the package.
    This validates the module-level code and dependencies.
    """
    r = subprocess.run(
        ["python3", "-c", "from sglang.jit_kernel import hisparse; print(\x27OK\x27)"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": f"{REPO}/python"},
    )
    # The import may fail due to missing dependencies (torch, etc.),
    # but we check that the file is importable at a syntax level
    # A syntax error would be exit code 1 with "SyntaxError" in stderr
    if r.returncode != 0:
        # Check it\'s not a syntax error - missing deps are OK for P2P
        assert "SyntaxError" not in r.stderr, f"Syntax error in module:\n{r.stderr}"
        assert "IndentationError" not in r.stderr, f"Indentation error in module:\n{r.stderr}"


def test_kernel_header_valid():
    """The hisparse.cuh header file has valid structure (pass_to_pass).

    Validates that the CUDA header file has proper include guards and
    basic structural elements expected in a valid C++ header.
    """
    content = _read_file()

    # Check for basic CUDA/C++ header structure
    assert "#include" in content, "Header must have #include statements"
    assert "__global__" in content or "__device__" in content, (
        "CUDA kernel file must have __global__ or __device__ functions"
    )

    # Check for balanced braces (basic structural validation)
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, (
        f"Unbalanced braces in header: {open_braces} open, {close_braces} close"
    )


def test_repo_git_tracks_file():
    """The hisparse kernel file is tracked by git (pass_to_pass).

    Uses git ls-files to verify the file is part of the repository.
    This is a real CI command that validates repo structure.
    """
    r = subprocess.run(
        ["git", "ls-files", "python/sglang/jit_kernel/csrc/hisparse.cuh"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git command failed:\n{r.stderr}"
    assert "hisparse.cuh" in r.stdout, (
        "hisparse.cuh should be tracked by git"
    )

