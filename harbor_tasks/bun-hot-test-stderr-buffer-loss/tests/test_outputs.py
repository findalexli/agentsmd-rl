"""
Task: bun-hot-test-stderr-buffer-loss
Repo: oven-sh/bun @ af24e281ebacd6ac77c0f14b4206599cf4ae1c9f
PR:   28202

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/test/cli/hot/hot.test.ts"


def _extract_sourcemap_blocks(code: str) -> str:
    """Extract only the three sourcemap test blocks from the file."""
    blocks = re.split(r'(?=it\s*\()', code)
    relevant = [b for b in blocks if any(name in b for name in [
        "sourcemap generation", "sourcemap loading", "large files",
    ])]
    return "\n".join(relevant)


def _read_code() -> str:
    """Read the target file, stripping single-line comments to prevent gaming."""
    lines = Path(TARGET).read_text().splitlines()
    result = []
    in_block = False
    for line in lines:
        s = line.strip()
        if in_block:
            if "*/" in s:
                in_block = False
            continue
        if s.startswith("/*") and "*/" not in s:
            in_block = True
            continue
        if s.startswith("/*") and "*/" in s:
            continue
        if s.startswith("//"):
            continue
        result.append(line)
    return "\n".join(result)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_target_file_exists():
    """Target test file must exist and be non-empty."""
    p = Path(TARGET)
    assert p.exists(), f"{TARGET} does not exist"
    assert p.stat().st_size > 0, f"{TARGET} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_data_loss_pattern_fixed():
    """The buggy str='' + continue outer pattern must be removed and remaining lines preserved.

    The base code sets str="" inside the inner loop then does 'continue outer',
    discarding unprocessed lines from the current chunk. The fix must:
    (a) Remove this discard pattern
    (b) Preserve remaining lines via any valid mechanism
    """
    code = _read_code()

    # (a) The buggy pattern: str="" followed by continue outer
    has_buggy = bool(re.search(
        r'str\s*=\s*["\']["\'].*?continue\s+outer',
        code, re.DOTALL,
    ))
    assert not has_buggy, "Buggy str='' + continue outer pattern still present"

    # (b) Remaining lines preserved via slice/splice/join/break or restructured away
    preserves = bool(re.search(
        r'(?:'
        r'lines?\.\s*slice\s*\(|'
        r'lines?\.\s*splice\s*\(|'
        r'remaining\s*[=,]|'
        r'\.join\s*\(\s*["\']\\n|'
        r'str\s*=\s*[^"\';\n]*lines?|'
        r'buf\w*\s*=\s*[^"\';\n]*lines'
        r')',
        code,
    ))
    no_continue_outer = "continue outer" not in code

    assert preserves or no_continue_outer, (
        "No mechanism found to preserve remaining lines from split chunks"
    )


# [pr_diff] fail_to_pass
def test_trailing_partial_lines_preserved():
    """When splitting stderr by newline, the trailing partial line must be saved.

    The base code clears str="" inside the processing loop, discarding
    incomplete trailing lines. The fix must pop/save the last element.
    """
    code = _read_code()

    # Must save the trailing element from the split
    saves_last = bool(re.search(
        r'(?:'
        r'lines?\.\s*pop\s*\(\s*\)|'
        r'lines?\s*\[\s*lines?\s*\.\s*length\s*-\s*1|'
        r'lines?\.\s*at\s*\(\s*-\s*1\s*\)|'
        r'str\s*=\s*lines?\.\s*pop|'
        r'str\s*=\s*lines?\s*\[\s*lines?\s*\.\s*length'
        r')',
        code,
    ))
    # Also accept: restructured via helper function processing stderr
    uses_helper = bool(re.search(r'(?:async\s+)?function\s+\w+.*?stderr', code, re.DOTALL))

    # In the sourcemap test blocks, str="" must not appear as a bare reassignment.
    # (Other non-sourcemap tests in the file legitimately use str="" — ignore those.)
    sourcemap_blocks = _extract_sourcemap_blocks(code)
    inner_clear = False
    for line in sourcemap_blocks.splitlines():
        stripped = line.strip()
        if re.match(r'str\s*=\s*["\']["\']\s*;', stripped):
            inner_clear = True
            break

    assert (saves_last or uses_helper) and not inner_clear, (
        "Trailing partial lines may be discarded (no pop/save or inner str='' found)"
    )


# [pr_diff] fail_to_pass
def test_bundler_no_inherit_pipes():
    """Bundler subprocesses must not use stdout/stderr:'inherit'.

    The base code uses stdout:"inherit" and stderr:"inherit" on bundler spawns,
    which causes pipe buffer backpressure that blocks the bundler.
    """
    code = _read_code()

    # Find test blocks for sourcemap loading tests (they spawn bundlers)
    test_blocks = re.split(r'(?=it\s*\()', code)
    for block in test_blocks:
        if "sourcemap loading" not in block and "large files" not in block:
            continue
        # Look for spawn calls with --watch (bundler spawns)
        spawn_sections = re.findall(r'spawn\s*\(\s*\{[\s\S]*?\}\s*\)', block)
        for section in spawn_sections:
            if "--watch" in section or '"watch"' in section:
                assert not re.search(
                    r'std(?:out|err)\s*:\s*["\']inherit["\']', section
                ), f"Bundler spawn still uses 'inherit': {section[:100]}..."


# [pr_diff] fail_to_pass
def test_early_bundler_exit_detection():
    """Bundler-based tests must detect early bundler exit instead of hanging.

    Accept: Promise.race, Promise.any, bundler.exited, .on('exit'),
    AbortController, or any concurrent monitoring pattern — but only in the
    sourcemap loading test blocks that spawn a bundler subprocess.
    """
    code = _read_code()

    # Only check in test blocks that spawn bundler subprocesses
    test_blocks = re.split(r'(?=it\s*\()', code)
    bundler_blocks = [
        b for b in test_blocks
        if "sourcemap loading" in b or "large files" in b
    ]
    assert len(bundler_blocks) >= 2, "Expected at least 2 bundler-based test blocks"

    for block in bundler_blocks:
        has_exit_detect = bool(re.search(
            r'(?:'
            r'Promise\.\s*(?:race|any|allSettled)\s*\(|'
            r'bundler\.\s*exited|'
            r'\.on\s*\(\s*["\'](?:exit|close)["\']|'
            r'AbortController|'
            r'exited\s*\.\s*then\s*\('
            r')',
            block,
        ))
        assert has_exit_detect, (
            f"No early bundler exit detection in test block: {block[:80]}..."
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_sourcemap_tests_preserved():
    """All three sourcemap hot-reload tests must exist and verify 50 reload cycles."""
    code = _read_code()

    tests = [
        "should work with sourcemap generation",
        "should work with sourcemap loading",
        "should work with sourcemap loading with large files",
    ]
    for t in tests:
        assert t in code, f"Test '{t}' missing from file"

    # Each test must still verify 50 reloads
    reload_checks = len(re.findall(r'(?:toBe|toEqual|===)\s*\(\s*50\s*\)', code))
    assert reload_checks >= 3, (
        f"Expected >= 3 reload-count assertions (toBe/toEqual 50), found {reload_checks}"
    )


# [static] fail_to_pass
def test_not_stub():
    """Modified file must have meaningful code changes, not just comments or trivial edits."""
    diff = subprocess.run(
        ["git", "diff", "HEAD", "--", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, cwd=REPO,
    ).stdout

    added = removed = 0
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:].strip()
            if content and not content.startswith("//") and not content.startswith("/*"):
                added += 1
        elif line.startswith("-") and not line.startswith("---"):
            content = line[1:].strip()
            if content and not content.startswith("//") and not content.startswith("/*"):
                removed += 1

    total_changes = added + removed
    assert total_changes >= 10, (
        f"Only {total_changes} non-comment lines changed — fix should touch ~50+ lines"
    )

    code = Path(TARGET).read_text()
    assert len(code.splitlines()) > 300, "File appears gutted (< 300 lines)"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — repo format check
def test_repo_format():
    """Repo's Prettier formatting check passes on the modified file (pass_to_pass)."""
    # Install tools first since the container is stateless
    install = subprocess.run(
        ["npm", "install", "-g", "prettier"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["npx", "prettier", "--check", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — TypeScript syntax validation
def test_target_typescript_syntax():
    """Target file must have valid TypeScript syntax (pass_to_pass)."""
    code = _read_code()
    # Basic TypeScript syntax validation - check for balanced braces and valid structure
    open_braces = code.count("{")
    close_braces = code.count("}")
    open_parens = code.count("(")
    close_parens = code.count(")")
    open_brackets = code.count("[")
    close_brackets = code.count("]")

    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"
    assert open_parens == close_parens, f"Unbalanced parens: {open_parens} open, {close_parens} close"
    assert open_brackets == close_brackets, f"Unbalanced brackets: {open_brackets} open, {close_brackets} close"

    # Check for required test structure elements
    assert "import { spawn } from \"bun\"" in code or 'import { spawn } from "bun"' in code, "Missing spawn import"
    assert "it(" in code, "Missing test cases (it() calls)"
    assert "expect(" in code, "Missing expect() assertions"


# [repo_tests] pass_to_pass — oxlint check (no errors, warnings ok)
def test_repo_oxlint():
    """Repo's oxlint passes on the target file with 0 errors (pass_to_pass).

    The bun repo uses oxlint in CI. Warnings are acceptable (existing code
    has intentional patterns), but errors must be 0.
    """
    install = subprocess.run(
        ["npm", "install", "-g", "oxlint"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["npx", "oxlint", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # oxlint returns exit code 0 for warnings only, non-zero for errors
    # We allow warnings (existing code style) but not errors
    assert r.returncode == 0, f"oxlint found errors:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — TypeScript project check (excluding regression fixtures)
def test_repo_typescript_project():
    """Repo's TypeScript project compiles without errors (pass_to_pass).

    Excludes test/regression/issue/14477 which contains intentional JSX
    syntax errors for regression testing.
    """
    install = subprocess.run(
        ["npm", "install", "-g", "typescript"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "test", "--skipLibCheck"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Filter out known intentional errors from regression fixtures
    errors = [line for line in r.stderr.splitlines() if "error TS" in line]
    real_errors = [e for e in errors if "test/regression/issue/14477" not in e]
    assert len(real_errors) == 0, f"TypeScript errors found:\n" + "\n".join(real_errors[:10])


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — test/CLAUDE.md:147 @ af24e281
def test_buffer_alloc_convention():
    """Large repetitive strings (>=100 chars) must use Buffer.alloc, not .repeat().

    Rule: 'Use Buffer.alloc(count, fill).toString() instead of "A".repeat(count).
    "".repeat is very slow in debug JavaScriptCore builds.'
    Source: test/CLAUDE.md:147 @ af24e281
    """
    code = _read_code()

    # Find large .repeat() calls (number >= 100)
    large_repeats = re.findall(
        r'["\'][^"\']*["\']\s*\.\s*repeat\s*\(\s*(\d+)\s*\)', code
    )
    has_large_repeat = any(int(n) >= 100 for n in large_repeats)
    assert not has_large_repeat, (
        f"Found .repeat() with large count: {[n for n in large_repeats if int(n) >= 100]}"
    )

    # Must use Buffer.alloc (or Uint8Array) for large string creation
    has_buffer = bool(re.search(r'Buffer\.\s*alloc\s*\(', code))
    has_uint8 = bool(re.search(r'new\s+Uint8Array\s*\(', code))
    assert has_buffer or has_uint8, (
        "No Buffer.alloc or Uint8Array found for large repetitive strings"
    )
