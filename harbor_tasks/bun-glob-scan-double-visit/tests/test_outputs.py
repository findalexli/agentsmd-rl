"""
Task: bun-glob-scan-double-visit
Repo: oven-sh/bun @ 639bc4351cd7b5daa38b99d47a506dec68e95353
PR:   #28496

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Bun requires full Zig compiler + WebKit/JSC + CMake toolchain to build.
All tests inspect source structure because we cannot compile and call the code.
# AST-only because: Zig code requires Zig compiler + WebKit/JSC; not available in container
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
WALKER = Path(f"{REPO}/src/glob/GlobWalker.zig")
BITSET = Path(f"{REPO}/src/collections/bit_set.zig")


def _read(path: Path) -> str:
    return path.read_text()


def _added_lines() -> list[str]:
    """Return lines added to GlobWalker.zig (git diff vs HEAD)."""
    r = subprocess.run(
        ["git", "diff", "--numstat", "HEAD", "--", "src/glob/GlobWalker.zig"],
        capture_output=True, text=True, cwd=REPO,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return []
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "src/glob/GlobWalker.zig"],
        capture_output=True, text=True, cwd=REPO,
    )
    return [
        l[1:] for l in r.stdout.split("\n")
        if l.startswith("+") and not l.startswith("+++")
    ]


def _extract_struct(code: str, name: str) -> str:
    """Extract struct body by balanced-brace matching."""
    m = re.search(rf"const {name} = struct\s*\{{", code)
    assert m, f"{name} struct not found"
    depth, pos = 1, m.end()
    while pos < len(code) and depth > 0:
        if code[pos] == "{":
            depth += 1
        elif code[pos] == "}":
            depth -= 1
        pos += 1
    return code[m.start() : pos]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_zig_files_balanced_braces():
    """Modified Zig files must have balanced braces (basic syntax sanity)."""
    for path in [WALKER, BITSET]:
        code = _read(path)
        opens = code.count("{")
        closes = code.count("}")
        assert abs(opens - closes) <= 2, (
            f"{path.name}: unbalanced braces ({opens} open, {closes} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_workitem_tracks_multiple_indices():
    """WorkItem must no longer use a single u32 index field.

    The bug is caused by WorkItem having `idx: u32`, so two WorkItems are
    pushed for the same dir at **/X boundaries. Any correct fix must allow
    WorkItem to carry multiple active indices (bitset, array, set, etc.).
    """
    code = _read(WALKER)
    body = _extract_struct(code, "WorkItem")

    # Old buggy code has `idx: u32` -- must be gone
    assert not re.search(r"\bidx\s*:\s*u32\s*[,\n]", body), (
        "WorkItem still has idx: u32 (single index = double-visit bug)"
    )

    # Must have SOME field that can hold multiple values
    multi_patterns = [
        r"BitSet", r"AutoBitSet", r"bit_set",
        r"ArrayList", r"BoundedArray", r"ArrayListUnmanaged",
        r"HashMap", r"AutoHashMap",
        r"\[\d+\]u\d+", r"\[\]u\d+",  # fixed/slice arrays
        r"idx2\s*:", r"indices\s*:", r"active\s*:",
        r"component.*set", r"ComponentSet",
    ]
    found = any(re.search(p, body, re.IGNORECASE) for p in multi_patterns)

    if not found:
        # Accept: WorkItem.new() takes a non-u32 second parameter
        new_fn = re.search(r"fn\s+new\s*\(([^)]*)\)", body)
        if new_fn:
            params = [p.strip() for p in new_fn.group(1).split(",")]
            if len(params) >= 2 and not re.search(r":\s*u32\s*$", params[1]):
                found = True

    assert found, "WorkItem has no field capable of holding multiple indices"


# [pr_diff] fail_to_pass
def test_double_push_eliminated():
    """Paired workbuf.append calls for the same dir must be consolidated.

    The base code pushes two WorkItems for the same directory at **/X
    boundaries (11 append calls total with paired if/else blocks).
    A correct fix consolidates into fewer appends (one per directory).
    """
    code = _read(WALKER)
    append_count = len(re.findall(r"workbuf\.append", code))
    assert 0 < append_count < 11, (
        f"workbuf.append count is {append_count} (base has 11, fix should consolidate; 0 means removed)"
    )


# [pr_diff] fail_to_pass
def test_pattern_matching_iterates_active_indices():
    """Pattern matching must iterate over a collection of active indices.

    The fix evaluates matchPatternDir/matchPatternFile for EACH active index,
    not just a single one. Accepts any iteration mechanism (while/for loop
    over iterator, bitset, array, etc.).
    """
    code = _read(WALKER)

    iteration_patterns = [
        r"\.iterator\s*\(",
        r"while\s*\([^)]*\.next\(\)",
        r"for\s*\([^)]*\.items",
        r"while\s*\([^)]*findFirstSet",
        r"for\s*\([^)]*\.\.",
        r"while\s*\([^)]*mask",
    ]

    match_calls = list(
        re.finditer(r"match(?:Pattern(?:Dir|File)|PatternImpl)\s*\(", code)
    )
    assert match_calls, "No pattern matching calls found"

    found_iteration = False
    for call in match_calls:
        region_start = max(0, call.start() - 1500)
        region_end = min(len(code), call.end() + 300)
        region = code[region_start:region_end]
        if any(re.search(p, region) for p in iteration_patterns):
            found_iteration = True
            break

    assert found_iteration, (
        "Pattern matching not called inside iteration over active indices"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) -- regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_both_match_functions_present():
    """matchPatternDir and matchPatternFile must be defined and called."""
    code = _read(WALKER)
    for fn in ["matchPatternDir", "matchPatternFile"]:
        assert f"fn {fn}" in code, f"{fn} not defined"
        calls = re.findall(fn + r"\s*\(", code)
        assert len(calls) >= 2, f"{fn} defined but not called (need def + >=1 call)"


# [pr_diff] pass_to_pass
def test_core_api_preserved():
    """Core GlobWalker identifiers must still exist."""
    code = _read(WALKER)
    for name in ["matchPatternDir", "matchPatternFile", "matchPatternImpl",
                  "WorkItem", "workbuf"]:
        assert name in code, f"Missing from GlobWalker: {name}"


# [pr_diff] pass_to_pass
def test_workitem_retains_path_and_kind():
    """WorkItem must still have path and kind fields."""
    code = _read(WALKER)
    body = _extract_struct(code, "WorkItem")
    assert "path" in body, "WorkItem missing path field"
    assert "Kind" in body or "kind" in body, "WorkItem missing kind field/type"


# [static] fail_to_pass
def test_substantial_modification():
    """GlobWalker.zig must have substantial changes (>= 20 lines added)."""
    r = subprocess.run(
        ["git", "diff", "--numstat", "HEAD", "--", "src/glob/GlobWalker.zig"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0 and r.stdout.strip(), "No changes to GlobWalker.zig"
    parts = r.stdout.strip().split()
    added = int(parts[0])
    assert added >= 20, f"Only {added} lines added (need >= 20 for a real fix)"


# [static] fail_to_pass
def test_coherent_zig_code():
    """Added lines must contain real Zig constructs (not keyword injection)."""
    added = _added_lines()
    code_lines = [l for l in added if l.strip() and not l.strip().startswith("//")]
    assert len(code_lines) >= 15, f"Only {len(code_lines)} non-comment added lines"

    zig_constructs = sum(
        1 for l in code_lines
        if re.search(r"\b(fn |if |while |for |const |var |return |switch |\.\w+\()", l)
    )
    assert zig_constructs >= 8, (
        f"Only {zig_constructs} lines with Zig constructs (need >= 8)"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass -- CLAUDE.md:232 @ 639bc435
def test_allocator_usage():
    """New code must reference an allocator (Zig memory management rule).

    From CLAUDE.md:232: 'Memory management -- In Zig code, be careful with
    allocators and use defer for cleanup.'
    """
    added = _added_lines()
    code_lines = [l for l in added if l.strip() and not l.strip().startswith("//")]
    text = "\n".join(code_lines)
    assert "allocator" in text.lower() or "alloc" in text.lower(), (
        "New code does not reference any allocator"
    )


# [agent_config] pass_to_pass -- src/CLAUDE.md:11 @ 639bc435
def test_no_inline_imports():
    """No @import() inside functions -- imports must be at file/struct bottom.

    From src/CLAUDE.md:11: 'Never use @import() inline inside of functions.
    Always put them at the bottom of the file or containing struct.'
    """
    added = _added_lines()
    for line in added:
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        if "@import" in stripped:
            # Top-level/struct-level is <= 8 spaces indent
            indent = len(line) - len(line.lstrip())
            assert indent <= 8, (
                f"@import used inline (indent={indent}): {stripped}"
            )


# [agent_config] pass_to_pass -- src/CLAUDE.md:16 @ 639bc435
def test_no_std_namespace_in_new_code():
    """New code must not introduce std.fs, std.posix, or std.os usage.

    From src/CLAUDE.md:16: 'Always use bun.* APIs instead of std.*.
    The bun namespace provides cross-platform wrappers that preserve
    OS error info and never use unreachable.'
    """
    added = _added_lines()
    forbidden = ["std.fs.", "std.posix.", "std.os."]
    for line in added:
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        for pat in forbidden:
            assert pat not in stripped, (
                f"New code uses {pat} (should use bun.* equivalent): {stripped}"
            )


# [agent_config] pass_to_pass -- src/CLAUDE.md:234 @ 639bc435
def test_no_catch_out_of_memory():
    """New code must use bun.handleOom() not 'catch bun.outOfMemory()'.

    From src/CLAUDE.md:234: 'bun.handleOom(expr) converts error.OutOfMemory
    into a crash without swallowing other errors.'
    """
    added = _added_lines()
    for line in added:
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "catch bun.outOfMemory()" not in stripped, (
            f"Uses catch bun.outOfMemory() instead of bun.handleOom(): {stripped}"
        )
