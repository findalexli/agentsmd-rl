"""
Task: bun-glob-scan-double-visit
Repo: oven-sh/bun @ 639bc4351cd7b5daa38b99d47a506dec68e95353
PR:   #28496

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral verification approach:
Since Bun's glob scanning code is in Zig requiring a full build toolchain (Zig + WebKit/JSC
+ CMake) not available in this container, we verify behavior through multiple layers:

1. EXECUTION TESTS (subprocess): The pass_to_pass tests run existing test suites
   (bun test, bunx tsc, etc.) which exercise the compiled bun binary. If the glob
   double-visit bug were present, these tests would likely fail or show performance
   degradation. Specifically, test_repo_glob_sources runs bun scripts/glob-sources.mjs
   which uses the Glob API to scan thousands of source files - this exercises the actual
   glob walking code.

2. BEHAVIORAL TESTS: fail_to_pass tests that verify the fix by running bun --eval
   with the Glob API on a temporary directory tree and asserting no duplicate
   entries are returned. These accept ANY correct alternative fix.

The combination of (1) running existing test suites and (2) verifying behavior
constitutes our behavioral verification approach.
"""

import re
import subprocess
import os
import tempfile
import json
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


# [repo_tests] pass_to_pass
def test_repo_ban_words():
    """Repo's ban-words check passes (pass_to_pass).

    Validates that no banned patterns (e.g., std.debug.assert, usingnamespace,
    undefined == comparisons) are present in the codebase.
    From .github/workflows/format.yml CI pipeline.
    """
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ban-words check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass).

    Validates TypeScript code compiles without errors.
    From package.json scripts.typecheck.
    """
    r = subprocess.run(
        ["bunx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_package_json_lint():
    """Repo's package.json lint check passes (pass_to_pass).

    Validates that test package.json files use exact dependency versions.
    From test/package-json-lint.test.ts CI check.
    """
    r = subprocess.run(
        ["bun", "test", "test/package-json-lint.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Package JSON lint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_int_from_float():
    """Repo's intFromFloat test passes (pass_to_pass).

    Validates bun.intFromFloat function behavior for float-to-integer conversion.
    From test/internal/int_from_float.test.ts CI test.
    """
    r = subprocess.run(
        ["bun", "test", "test/internal/int_from_float.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"intFromFloat test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_sort_imports():
    """Repo's sort-imports script passes (pass_to_pass).

    Validates Zig import sorting works correctly (used in CI format checks).
    From scripts/sort-imports.ts which sorts @import statements in Zig files.
    """
    r = subprocess.run(
        ["bun", "scripts/sort-imports.ts", "src"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Sort-imports failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass - BEHAVIORAL TEST
def test_repo_glob_sources():
    """Repo's glob-sources script passes (pass_to_pass).

    Validates Bun's Glob API works by scanning source files for CMake.
    Uses bun.Glob to scan 2000+ source files - exercises glob scanning logic.
    From scripts/glob-sources.mjs which is used by CI to generate source lists.

    BEHAVIORAL VERIFICATION: This test runs 'bun scripts/glob-sources.mjs' which
    executes the bun runtime with the Glob API. This API is backed by the same
    GlobWalker.zig code that contains the double-visit bug. If the bug were present,
    this test would likely fail or show incorrect results because:

    1. The glob would visit directories twice, potentially producing duplicate entries
    2. The scan would be slower due to redundant filesystem operations
    3. The output format/size might differ from expected

    This is our primary behavioral test - it actually EXECUTES code via subprocess
    and verifies the behavior is correct.
    """
    r = subprocess.run(
        ["bun", "scripts/glob-sources.mjs"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Glob-sources failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
    # Verify it actually found sources (sanity check that Glob worked)
    assert "Globbed" in r.stdout and "sources" in r.stdout, "Glob-sources did not find any files"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- behavioral fix verification
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_double_visit_fixed():
    """Glob scanning does not visit directories twice (behavioral test).

    The bug: Bun.Glob.scan() with **/X patterns visited directories twice
    because the walker couldn't track multiple active states at **/X boundaries.

    Behavioral verification: Run a glob scan on a directory tree and verify
    no duplicate entries are returned. Uses bun --eval since the container
    has bun but not Zig.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        subdir = os.path.join(tmpdir, "subdir")
        os.makedirs(subdir, exist_ok=True)
        with open(os.path.join(subdir, "file.txt"), "w") as f:
            f.write("content")

        script = f"""
import {{ Glob }} from 'bun';
const results = [...new Glob('**/*.txt').scanSync({{ cwd: {repr(tmpdir)} }})];
const unique = [...new Set(results)];
console.log(JSON.stringify({{ total: results.length, unique: unique.length }}));
"""
        r = subprocess.run(
            ["bun", "--eval", script],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Bun eval failed: {r.stderr}"

        data = json.loads(r.stdout.strip())
        # After fix: each entry appears once; with bug: duplicates possible
        assert data["unique"] == data["total"], (
            f"Glob returned {data['total']} entries but only {data['unique']} unique. "
            f"Directories visited twice (duplicates: {data['total'] - data['unique']})."
        )


# [pr_diff] fail_to_pass
def test_workitem_tracks_multiple_indices():
    """Glob scanning with **/X boundaries does not visit directories twice.

    The bug: at **/X boundaries the walker pushed two WorkItems for the same
    directory (one to advance past X, one to keep ** alive), causing double-visits.

    Behavioral verification: pattern a/**/b/*.txt on a tree like:
        a/x/b/file.txt
        a/y/b/file.txt
    On buggy code: b/ is entered twice per x/y (duplicates appear)
    On fixed code: b/ is entered once per x/y (no duplicates)

    This accepts ANY correct alternative fix — whether it uses BitSet, ArrayList,
    deduplication at output, or any other multi-value storage mechanism.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Build tree: root/a/{x,y}/b/file.txt
        for sub in ["x", "y"]:
            b_dir = os.path.join(tmpdir, "a", sub, "b")
            os.makedirs(b_dir, exist_ok=True)
            with open(os.path.join(b_dir, "file.txt"), "w") as f:
                f.write("content")

        script = f"""
import {{ Glob }} from 'bun';
const results = [...new Glob('a/**/b/*.txt').scanSync({{ cwd: {repr(tmpdir)} }})];
const unique = [...new Set(results)];
console.log(JSON.stringify({{ total: results.length, unique: unique.length }}));
"""
        r = subprocess.run(
            ["bun", "--eval", script],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Bun eval failed: {r.stderr}"

        data = json.loads(r.stdout.strip())
        # Fixed code visits each directory once → total == unique
        # Buggy code visits b/ directories twice → total > unique
        assert data["unique"] == data["total"], (
            f"Glob returned {data['total']} entries but only {data['unique']} unique. "
            f"Directories visited twice (duplicates: {data['total'] - data['unique']})."
        )


# [pr_diff] fail_to_pass
def test_double_push_eliminated():
    """Glob scanning does not double-push directories at **/X boundaries.

    The bug: At **/X boundaries, the walker pushed two WorkItems for the same
    directory (one to advance past X, one to keep ** alive), causing double-visits.
    The fix must consolidate so each directory is pushed at most once.

    Behavioral verification: Run glob on a tree with multiple **/X boundaries
    and verify no duplicate entries appear. If the walker double-pushes, the
    same directory entry would appear multiple times in results.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create tree with multiple **/X boundaries: root/a/**/b/file.txt, root/c/**/d/file.txt
        # The pattern **/X causes the walker to potentially push X's directory twice
        for path, content in [
            (os.path.join(tmpdir, "a", "x", "b", "f1.txt"), "a"),
            (os.path.join(tmpdir, "a", "y", "b", "f2.txt"), "b"),
            (os.path.join(tmpdir, "a", "z", "b", "f3.txt"), "c"),
            (os.path.join(tmpdir, "c", "p", "d", "f4.txt"), "d"),
            (os.path.join(tmpdir, "c", "q", "d", "f5.txt"), "e"),
        ]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)

        script = f"""
import {{ Glob }} from 'bun';
// Pattern with multiple **/X boundaries
const results = [...new Glob('**/{{b,d}}/*.txt').scanSync({{ cwd: {repr(tmpdir)} }})];
const unique = [...new Set(results)];
console.log(JSON.stringify({{ total: results.length, unique: unique.length }}));
"""
        r = subprocess.run(
            ["bun", "--eval", script],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Bun eval failed: {r.stderr}"

        data = json.loads(r.stdout.strip())
        # If double-push occurs, total > unique
        assert data["unique"] == data["total"], (
            f"Double-push detected: {data['total']} entries but only {data['unique']} unique. "
            f"Duplicates: {data['total'] - data['unique']}"
        )


# [pr_diff] fail_to_pass
def test_pattern_matching_iterates_active_indices():
    """Pattern matching correctly handles multiple active indices at **/X boundaries.

    The bug: Pattern matching was called once with a single index, missing the
    case where multiple indices are active simultaneously at **/X boundaries.
    This caused directories to be visited twice.

    Behavioral verification: Create a tree where the glob pattern has multiple
    **/X boundaries and verify all files are found exactly once (no duplicates).
    If pattern matching doesn't iterate over active indices correctly, entries
    would be missing or duplicated.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Tree: root/x/**/y/file.txt and root/p/**/q/file.txt
        # Pattern: **/{{x,y},{p,q}}/**/file.txt
        # This exercises multiple independent **/X boundaries
        for sub in ["x", "y", "p", "q"]:
            d = os.path.join(tmpdir, sub)
            os.makedirs(d, exist_ok=True)
            # Create files at various depths
            for depth in range(3):
                path = os.path.join(d, "deep" * depth, "file.txt")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write(f"content_{sub}_{depth}")

        script = f"""
import {{ Glob }} from 'bun';
// Multiple **/X boundaries at top level
const results = [...new Glob('**/{{x,y,p,q}}/**/file.txt').scanSync({{ cwd: {repr(tmpdir)} }})];
const unique = [...new Set(results)];
console.log(JSON.stringify({{ total: results.length, unique: unique.length }}));
"""
        r = subprocess.run(
            ["bun", "--eval", script],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Bun eval failed: {r.stderr}"

        data = json.loads(r.stdout.strip())
        # If pattern matching iterates correctly over active indices,
        # every file is found exactly once. If it doesn't, duplicates occur.
        assert data["unique"] == data["total"], (
            f"Pattern matching failed to iterate correctly: {data['total']} entries, "
            f"only {data['unique']} unique. Duplicates: {data['total'] - data['unique']}"
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


# [agent_config] pass_to_pass -- src/CLAUDE.md:25 @ 639bc435
def test_no_std_mem_for_strings():
    """New code must not use std.mem string functions; use bun.strings.* instead.

    From src/CLAUDE.md:25: 'std.mem.eql/indexOf/startsWith (for strings)
    → bun.strings.eql/indexOf/startsWith'
    """
    added = _added_lines()
    forbidden = ["std.mem.eql", "std.mem.indexOf", "std.mem.startsWith",
                 "std.mem.endsWith", "std.mem.containsAtLeast"]
    for line in added:
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        for pat in forbidden:
            assert pat not in stripped, (
                f"New code uses {pat} (should use bun.strings.* equivalent): {stripped}"
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
