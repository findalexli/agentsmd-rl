"""
Task: bun-error-format-pending-exception-crash
Repo: oven-sh/bun @ f6528b58ed67c8fb8c80046114829d9ad79a292f
PR:   28488

Behavioral verification: These tests verify the fix by analyzing source code
structure (not text grepping). The key behavioral requirement is that catch
blocks must clear pending exceptions before returning typed errors.

Tests import and CALL code where possible, execute subprocesses (repo CI tests),
and inspect behavior through structural analysis of the source code.

The bug: when error message formatting triggers a JS exception (via
Symbol.toPrimitive), the catch block returns a fallback string but leaves the
exception pending. The subsequent throwValue crashes with assertNoException.

The fix: add braces to the catch block, call an exception-clearing method,
and return the appropriate typed error.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = Path("/repo")
TARGET = REPO / "src/bun.js/bindings/JSGlobalObject.zig"


# -----------------------------------------------------------------------------
# Bun installer helper (for pass-to-pass CI tests)
# -----------------------------------------------------------------------------

def _ensure_bun_installed() -> Path:
    """Ensure Bun is installed and return path to the binary."""
    bun_dir = Path("/tmp/bun-install")
    bun_bin = bun_dir / "bun-linux-x64" / "bun"

    if bun_bin.exists():
        return bun_bin

    bun_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        timeout=60,
    )
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "unzip"],
        capture_output=True,
        timeout=60,
    )
    subprocess.run(
        [
            "curl", "-LO",
            "https://pub-5e11e972747a44bf9aaf9394f185a982.r2.dev/releases/bun-v1.2.10/bun-linux-x64.zip",
            "--retry", "5",
        ],
        capture_output=True,
        cwd=str(bun_dir),
        timeout=120,
    )
    subprocess.run(
        ["unzip", "-q", "bun-linux-x64.zip"],
        capture_output=True,
        cwd=str(bun_dir),
        timeout=30,
    )
    (bun_bin.parent / "bunx").symlink_to(bun_bin)
    return bun_bin


# -----------------------------------------------------------------------------
# Fail-to-pass (f2p) - Structural verification
#
# NOTE: These tests analyze the SOURCE CODE structure rather than executing
# compiled code, because building the Zig source requires a full build
# environment (Zig compiler, dependencies) not available in this test environment.
#
# The structural analysis verifies:
# 1. Catch blocks have the proper block structure (braces) added by the fix
# 2. An exception-clearing call appears before the return statement
# 3. The return statement uses the correct typed error conversion
#
# These structural checks accept alternative correct implementations:
# - Any method matching `this.*Clear*` or `vm.*Clear*` satisfies the clearing requirement
# - Any method matching `.to*ErrorInstance(` satisfies the typed error requirement
# -----------------------------------------------------------------------------

def _strip_zig_comments_and_strings(code: str) -> str:
    """Remove Zig comments and string literals for structural analysis."""
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
    return code


def _extract_function_body(code: str, fn_name: str) -> str | None:
    """Extract the complete body of a pub fn by parsing brace structure."""
    marker = f"pub fn {fn_name}("
    start = code.find(marker)
    if start < 0:
        marker = f"pub fn {fn_name} "
        start = code.find(marker)
    if start < 0:
        return None

    brace_start = code.find("{", start + len(marker))
    if brace_start < 0:
        return None

    depth = 1
    i = brace_start + 1
    while i < len(code) and depth > 0:
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
        i += 1

    if depth != 0:
        return None

    return code[brace_start:i]


def _find_catch_blocks_with_returns(body: str) -> list[dict]:
    """Find all catch blocks that have return statements."""
    clean = _strip_zig_comments_and_strings(body)
    catches = []

    # Match catch blocks that have braces (the fix adds braces to catch blocks)
    pattern = r'catch\s*(?:\|[^|]*\|)?\s*\{'
    for match in re.finditer(pattern, clean):
        start = match.end() - 1
        depth = 1
        i = start + 1
        while i < len(clean) and depth > 0:
            if clean[i] == "{":
                depth += 1
            elif clean[i] == "}":
                depth -= 1
            i += 1

        if depth == 0:
            catch_body = clean[start + 1:i - 1]
            returns = []
            for ret_match in re.finditer(r'\breturn\b', catch_body):
                returns.append({
                    'pos': ret_match.start(),
                    'context': catch_body[max(0, ret_match.start()-50):min(len(catch_body), ret_match.end()+50)]
                })
            if returns:
                catches.append({
                    'body': catch_body,
                    'returns': returns
                })

    return catches


def _has_exception_clear_call_in_scope(catch_body: str, return_pos: int) -> bool:
    """
    Check if there's an exception-clearing call before the return position.
    
    Accepts ANY method that clears/handles exceptions to allow alternative
    correct implementations (different method names). The fix must clear
    exceptions, but the specific method name is an implementation detail.
    """
    before_return = catch_body[:return_pos]

    # Flexible patterns - accept ANY method that clears/handles exceptions
    # This ensures alternative correct fixes (different method names) pass
    clear_patterns = [
        r'this\.[a-zA-Z_]*[Cc]lear[a-zA-Z_]*\s*\(',
        r'vm\.[a-zA-Z_]*[Cc]lear[a-zA-Z_]*\s*\(',
        r'vm\.[a-zA-Z_]*[Ee]xcept[a-zA-Z_]*[Tt]ermination[a-zA-Z_]*\s*\(',
        r'_\s*=\s*this\.[a-zA-Z_]*[Cc]lear',
        r'_\s*=\s*vm\.[a-zA-Z_]*[Cc]lear',
        r'this\.[a-zA-Z_]*[Ee]xcept[a-zA-Z_]*\s*\(',
        r'vm\.[a-zA-Z_]*[Ee]xcept[a-zA-Z_]*\s*\(',
    ]

    for pattern in clear_patterns:
        if re.search(pattern, before_return):
            return True

    return False


def _get_error_return_type(catch_body: str, return_pos: int) -> str:
    """
    Determine what type of error instance is being returned.
    Returns 'type_error', 'syntax_error', 'range_error', 'generic_error', or 'unknown'.
    
    Uses flexible pattern to accept any typed error conversion method.
    """
    after_return = catch_body[return_pos:]
    stmt_end = after_return.find(';')
    if stmt_end < 0:
        stmt_end = len(after_return)
    return_stmt = after_return[:stmt_end]

    # Flexible pattern - accept any method that produces a typed error
    # This allows alternative implementations that use different helper functions
    if re.search(r'\.to[A-Za-z]*ErrorInstance\(', return_stmt):
        m = re.search(r'\.to([A-Za-z]+)ErrorInstance\(', return_stmt)
        if m:
            type_name = m.group(1).lower()
            if type_name == 'type':
                return 'type_error'
            elif type_name == 'syntax':
                return 'syntax_error'
            elif type_name == 'range':
                return 'range_error'
            else:
                return 'generic_error'
    elif re.search(r'\.toErrorInstance\(', return_stmt):
        return 'generic_error'
    else:
        return 'unknown'


def _analyze_error_function_behavior(fn_name: str, expected_typed_return: str | None = None) -> dict:
    """
    Analyze an error creation function for the behavioral fix.
    
    Checks that catch blocks (with braces - the fix adds braces) have:
    1. An exception-clearing call before the return
    2. The correct typed error return
    """
    if not TARGET.exists():
        return {'exists': False, 'error': 'Target file not found'}

    raw = TARGET.read_text()
    body = _extract_function_body(raw, fn_name)

    if body is None:
        return {'exists': False, 'error': f"Function {fn_name} not found"}

    catches = _find_catch_blocks_with_returns(body)

    if not catches:
        return {
            'exists': True,
            'has_catch_blocks': False,
            'behavioral_fix_present': False
        }

    catch_analysis = []
    for catch in catches:
        catch_info = {
            'has_returns': len(catch['returns']) > 0,
            'clears_before_return': False,
            'correct_typed_return': True
        }

        if catch['returns']:
            catch_info['clears_before_return'] = _has_exception_clear_call_in_scope(
                catch['body'], catch['returns'][0]['pos']
            )

            if expected_typed_return:
                actual_type = _get_error_return_type(catch['body'], catch['returns'][0]['pos'])
                catch_info['actual_return_type'] = actual_type
                catch_info['expected_return_type'] = expected_typed_return
                catch_info['correct_typed_return'] = (actual_type == expected_typed_return)

        catch_analysis.append(catch_info)

    has_clearing = any(c['clears_before_return'] for c in catch_analysis)
    all_correct_types = all(c['correct_typed_return'] for c in catch_analysis)

    return {
        'exists': True,
        'has_catch_blocks': True,
        'catch_count': len(catches),
        'behavioral_fix_present': has_clearing and all_correct_types,
        'exception_cleared_before_return': has_clearing,
        'correct_error_types_returned': all_correct_types,
        'catch_details': catch_analysis
    }


def test_create_error_instance_handles_exception_gracefully():
    """
    [f2p] createErrorInstance catch block must clear pending exception before return.

    The bug: catch block returns error but leaves pending exception.
    The fix: clear exception before returning.

    This test analyzes the SOURCE CODE structure to verify the fix is applied.
    A stub implementation (without the fix) would not have catch blocks with
    the clearing pattern and would fail this test.
    """
    result = _analyze_error_function_behavior("createErrorInstance")

    assert result['exists'], result.get('error', 'Function not found')

    if not result['has_catch_blocks']:
        assert False, "createErrorInstance has no catch blocks with braces - fix not applied (original code uses inline catch return)"

    assert result['exception_cleared_before_return'], (
        "createErrorInstance catch does not clear pending exception before return. "
        "The fix requires calling an exception-clearing method before returning."
    )


def test_create_type_error_returns_typed_error_on_format_failure():
    """
    [f2p] createTypeErrorInstance catch block must clear exception AND return TypeError.
    """
    result = _analyze_error_function_behavior("createTypeErrorInstance", expected_typed_return='type_error')

    assert result['exists'], result.get('error', 'Function not found')

    if not result['has_catch_blocks']:
        assert False, "createTypeErrorInstance has no catch blocks with braces - fix not applied"

    assert result['exception_cleared_before_return'], (
        "createTypeErrorInstance catch does not clear pending exception before return"
    )

    assert result['correct_error_types_returned'], (
        f"createTypeErrorInstance catch returns wrong error type. "
        f"Expected type_error."
    )


def test_create_syntax_error_returns_typed_error_on_format_failure():
    """
    [f2p] createSyntaxErrorInstance catch block must clear exception AND return SyntaxError.
    """
    result = _analyze_error_function_behavior("createSyntaxErrorInstance", expected_typed_return='syntax_error')

    assert result['exists'], result.get('error', 'Function not found')

    if not result['has_catch_blocks']:
        assert False, "createSyntaxErrorInstance has no catch blocks with braces - fix not applied"

    assert result['exception_cleared_before_return'], (
        "createSyntaxErrorInstance catch does not clear pending exception before return"
    )

    assert result['correct_error_types_returned'], (
        f"createSyntaxErrorInstance catch returns wrong error type. "
        f"Expected syntax_error."
    )


def test_create_range_error_returns_typed_error_on_format_failure():
    """
    [f2p] createRangeErrorInstance catch block must clear exception AND return RangeError.
    """
    result = _analyze_error_function_behavior("createRangeErrorInstance", expected_typed_return='range_error')

    assert result['exists'], result.get('error', 'Function not found')

    if not result['has_catch_blocks']:
        assert False, "createRangeErrorInstance has no catch blocks with braces - fix not applied"

    assert result['exception_cleared_before_return'], (
        "createRangeErrorInstance catch does not clear pending exception before return"
    )

    assert result['correct_error_types_returned'], (
        f"createRangeErrorInstance catch returns wrong error type. "
        f"Expected range_error."
    )


# -----------------------------------------------------------------------------
# Pass-to-pass - regression + anti-stub
# -----------------------------------------------------------------------------

def test_dom_exception_not_modified():
    """
    [p2p] createDOMExceptionInstance must NOT have exception clearing added.
    Per the spec, it should NOT be modified.
    """
    result = _analyze_error_function_behavior("createDOMExceptionInstance")

    if not result['exists']:
        return

    if result['has_catch_blocks']:
        assert not result['exception_cleared_before_return'], (
            "createDOMExceptionInstance should NOT clear exceptions - "
            "it uses try pattern and should remain unmodified"
        )


def test_file_not_stubbed():
    """Target file must retain substantial content (not gutted)."""
    assert TARGET.exists(), "Target file does not exist"
    line_count = len(TARGET.read_text().splitlines())
    assert line_count > 200, f"File appears stubbed ({line_count} lines)"


def test_all_four_functions_exist():
    """All four create*ErrorInstance functions must still exist."""
    raw = TARGET.read_text()
    for fn in [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]:
        assert f"pub fn {fn}" in raw, f"{fn} not found in target file"


# -----------------------------------------------------------------------------
# Config-derived (agent_config) - rules from src/CLAUDE.md
# -----------------------------------------------------------------------------

def _strip_comments_and_strings(code: str) -> str:
    """Remove Zig // comments and string literals."""
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
    return code


def _find_fn_region(code: str, fn_name: str, size: int = 3000) -> str | None:
    """Extract the region for a pub fn, bounded by the next pub fn or size chars."""
    marker = f"pub fn {fn_name}"
    idx = code.find(marker)
    if idx < 0:
        return None
    next_fn = code.find("pub fn ", idx + len(marker))
    end = idx + size
    if next_fn > 0:
        end = min(end, next_fn)
    return code[idx:end]


def test_no_inline_imports_in_error_functions():
    """No @import() calls inside the four create*ErrorInstance function bodies."""
    raw = TARGET.read_text()
    fns = [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]
    for fn_name in fns:
        region = _find_fn_region(raw, fn_name)
        if region is None:
            continue
        body_start = region.find("{")
        if body_start < 0:
            continue
        body = region[body_start:]
        inline_imports = re.findall(r"@import\s*\(", body)
        assert not inline_imports, (
            f"{fn_name} has inline @import() - must be at bottom of file or containing struct"
        )


def test_no_forbidden_std_apis_in_error_functions():
    """No std.fs, std.posix, std.os, std.process usage in the four create*ErrorInstance functions."""
    clean = _strip_comments_and_strings(TARGET.read_text())
    forbidden = ["std.fs", "std.posix", "std.os", "std.process"]
    fns = [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]
    for fn_name in fns:
        region = _find_fn_region(clean, fn_name)
        if region is None:
            continue
        for api in forbidden:
            assert api not in region, (
                f"{fn_name} uses {api} - must use bun.* equivalent instead"
            )


def test_no_catch_out_of_memory_pattern():
    """No 'catch bun.outOfMemory()' in the four error functions - use bun.handleOom() instead."""
    clean = _strip_comments_and_strings(TARGET.read_text())
    fns = [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]
    for fn_name in fns:
        region = _find_fn_region(clean, fn_name)
        if region is None:
            continue
        assert "catch bun.outOfMemory()" not in region and "catch bun.oom()" not in region, (
            f"{fn_name} uses catch bun.outOfMemory() - should use bun.handleOom() instead"
        )


# -----------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates - subprocess-based real CI commands
# -----------------------------------------------------------------------------

def test_repo_banned_words():
    """Banned words check passes (pass_to_pass) - runs bun ./test/internal/ban-words.test.ts."""
    bun_bin = _ensure_bun_installed()
    env = os.environ.copy()
    env["PATH"] = f"{bun_bin.parent}:{env.get('PATH', '')}"

    subprocess.run(
        [str(bun_bin), "install"],
        capture_output=True,
        timeout=180,
        cwd=str(REPO),
        env=env,
    )

    r = subprocess.run(
        [str(bun_bin), "./test/internal/ban-words.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"Banned words test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_int_from_float():
    """int_from_float unit test passes (pass_to_pass) - runs bun test test/internal/int_from_float.test.ts."""
    bun_bin = _ensure_bun_installed()
    env = os.environ.copy()
    env["PATH"] = f"{bun_bin.parent}:{env.get('PATH', '')}"

    r = subprocess.run(
        [str(bun_bin), "test", "test/internal/int_from_float.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"int_from_float test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_glob_sources():
    """glob-sources script runs without errors (pass_to_pass) - runs bun scripts/glob-sources.mjs."""
    bun_bin = _ensure_bun_installed()
    env = os.environ.copy()
    env["PATH"] = f"{bun_bin.parent}:{env.get('PATH', '')}"

    r = subprocess.run(
        [str(bun_bin), "scripts/glob-sources.mjs"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"glob-sources script failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_package_json_lint():
    """Package.json lint test passes (pass_to_pass) - runs bun test test/package-json-lint.test.ts."""
    bun_bin = _ensure_bun_installed()
    env = os.environ.copy()
    env["PATH"] = f"{bun_bin.parent}:{env.get('PATH', '')}"

    subprocess.run(
        [str(bun_bin), "install"],
        capture_output=True,
        timeout=180,
        cwd=str(REPO),
        env=env,
    )

    r = subprocess.run(
        [str(bun_bin), "test", "test/package-json-lint.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"Package-json-lint test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_bun_cli():
    """Bun CLI tests pass (pass_to_pass) - runs bun test test/cli/bun.test.ts."""
    bun_bin = _ensure_bun_installed()
    env = os.environ.copy()
    env["PATH"] = f"{bun_bin.parent}:{env.get('PATH', '')}"

    subprocess.run(
        [str(bun_bin), "install"],
        capture_output=True,
        timeout=180,
        cwd=str(REPO),
        env=env,
    )

    r = subprocess.run(
        [str(bun_bin), "test", "test/cli/bun.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"Bun CLI test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_typecheck_root():
    """Root project TypeScript typecheck passes (pass_to_pass) - runs tsc --noEmit on root project."""
    bun_bin = _ensure_bun_installed()
    env = os.environ.copy()
    env["PATH"] = f"{bun_bin.parent}:{env.get('PATH', '')}"

    subprocess.run(
        [str(bun_bin), "install"],
        capture_output=True,
        timeout=180,
        cwd=str(REPO),
        env=env,
    )

    r = subprocess.run(
        [str(bun_bin), "run", "tsc", "--noEmit", "--project", "tsconfig.json"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# -----------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates - static analysis
# -----------------------------------------------------------------------------

def test_zig_file_balanced_braces():
    """JSGlobalObject.zig has balanced braces (basic syntax check)."""
    raw = TARGET.read_text()
    clean = _strip_zig_comments_and_strings(raw)
    open_count = clean.count("{")
    close_count = clean.count("}")
    assert open_count == close_count, (
        f"Zig file has unbalanced braces: {open_count} open, {close_count} close"
    )


def test_zig_file_balanced_parens():
    """JSGlobalObject.zig has balanced parentheses (basic syntax check)."""
    raw = TARGET.read_text()
    clean = _strip_zig_comments_and_strings(raw)
    open_count = clean.count("(")
    close_count = clean.count(")")
    assert open_count == close_count, (
        f"Zig file has unbalanced parentheses: {open_count} open, {close_count} close"
    )


def test_zig_file_no_double_semicolons():
    """JSGlobalObject.zig has no double semicolons (common syntax error)."""
    raw = TARGET.read_text()
    clean = _strip_zig_comments_and_strings(raw)
    assert ";;" not in clean, "Zig file contains double semicolons (;;) - likely syntax error"


def test_zig_file_pub_fn_syntax():
    """JSGlobalObject.zig pub fn declarations have valid syntax."""
    raw = TARGET.read_text()
    lines = raw.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        if re.match(r"^pub\s+fn\s+\w+", stripped) and stripped.endswith(";"):
            context = " ".join(lines[max(0, i-2):i+1])
            if "extern" not in context:
                assert False, f"Line {i+1}: pub fn with semicolon (not extern): {stripped[:60]}"


def test_zig_file_no_trailing_whitespace():
    """JSGlobalObject.zig has no lines with trailing whitespace (code style)."""
    raw = TARGET.read_text()
    lines = raw.split("\n")
    for i, line in enumerate(lines, 1):
        if line.endswith(" ") or line.endswith("\t"):
            if line.strip():
                assert False, f"Line {i} has trailing whitespace: {line[:40]!r}"


def test_no_banned_undefined_comparisons():
    """JSGlobalObject.zig has no undefined comparisons (UB per ban-words)."""
    clean = _strip_comments_and_strings(TARGET.read_text())
    fns = [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]
    banned_patterns = [
        " != undefined",
        " == undefined",
        "undefined != ",
        "undefined == ",
    ]
    for fn_name in fns:
        region = _find_fn_region(clean, fn_name)
        if region is None:
            continue
        for pattern in banned_patterns:
            assert pattern not in region, (
                f"{fn_name} contains banned pattern '{pattern}' - undefined comparison is UB"
            )


def test_no_usingnamespace_in_target():
    """JSGlobalObject.zig has no usingnamespace (deprecated in Zig 0.15)."""
    raw = TARGET.read_text()
    clean = _strip_comments_and_strings(raw)
    fns = [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]
    for fn_name in fns:
        region = _find_fn_region(clean, fn_name)
        if region is None:
            continue
        assert "usingnamespace" not in region, (
            f"{fn_name} contains 'usingnamespace' - deprecated in Zig 0.15"
        )


def test_no_banned_jsvalue_patterns():
    """JSGlobalObject.zig error functions do not use banned JSValue patterns."""
    clean = _strip_comments_and_strings(TARGET.read_text())
    fns = [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]
    banned_patterns = [
        ".jsBoolean(true)",
        ".jsBoolean(false)",
        "JSValue.true",
        "JSValue.false",
    ]
    for fn_name in fns:
        region = _find_fn_region(clean, fn_name)
        if region is None:
            continue
        for pattern in banned_patterns:
            assert pattern not in region, (
                f"{fn_name} contains banned pattern '{pattern}' - use .true/.false instead"
            )


def test_no_std_debug_in_error_functions():
    """JSGlobalObject.zig error functions do not use std.debug (per ban-words)."""
    clean = _strip_comments_and_strings(TARGET.read_text())
    fns = [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]
    banned_patterns = [
        "std.debug.assert",
        "std.debug.dumpStackTrace",
        "std.debug.print",
        "std.log",
    ]
    for fn_name in fns:
        region = _find_fn_region(clean, fn_name)
        if region is None:
            continue
        for pattern in banned_patterns:
            assert pattern not in region, (
                f"{fn_name} contains banned pattern '{pattern}' - use bun equivalent"
            )


def test_repo_prettier_check():
    """Prettier formatting check passes (pass_to_pass) - verifies JS/TS files are formatted."""
    r = subprocess.run(
        [
            "npx", "--yes", "prettier@latest", "--check",
            "--config", ".prettierrc",
            "scripts/*.ts", "scripts/*.mjs",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
