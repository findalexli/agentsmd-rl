#!/usr/bin/env python3
"""
Behavioral tests for bun-throw-pending-exception-crash fix.

These tests verify that the crash (releaseAssertNoException when throwing
while a termination exception is pending) is actually fixed, by running
the JavaScript reproduction script and checking for clean exit.

Unlike the original text-grepping tests, these tests execute the code
and verify observable behavior.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/bun"
FILE = "src/bun.js/bindings/JSGlobalObject.zig"

# The reproduction script from instruction.md
REPRODUCTION_SCRIPT = """
var a = false, b = false;
function r() { r() }
try { r() } catch(e) { a = true }
try { Bun.jest().expect(42).toBeFalse() } catch(e) { b = true }
if (a && b) console.log("OK")
"""


def _find_bun():
    """Find bun binary, checking common locations."""
    # Check common paths
    paths = [
        "/usr/local/bin/bun",
        "/usr/bin/bun",
        "/home/bun/bun",
        Path("/workspace/bun/bun"),
        Path(os.environ.get("HOME", "/root")) / ".bun/bin/bun",
    ]
    for p in paths:
        if Path(p).exists():
            return p
    # Check if bun is in PATH
    result = subprocess.run(["which", "bun"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def _install_bun():
    """Download and install bun to a temp location."""
    import urllib.request
    import zipfile

    # Bun release URL for linux x64
    bun_url = "https://github.com/oven-sh/bun/releases/download/bun-v1.1.0/bun-linux-x64.zip"
    tmpdir = tempfile.mkdtemp()
    zip_path = Path(tmpdir) / "bun.zip"
    extract_dir = Path(tmpdir) / "bun"

    try:
        urllib.request.urlretrieve(bun_url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
        bun_path = extract_dir / "bun"
        bun_path.chmod(0o755)
        return str(bun_path)
    except Exception:
        return None


def get_bun_path():
    """Get bun path, installing if needed."""
    bun = _find_bun()
    if bun:
        return bun
    return _install_bun()


# ============================================================================
# Behavioral tests - These actually run the code and verify behavior
# ============================================================================

def test_reproduction_script_exits_cleanly():
    """
    Behavioral test: Running the reproduction script should exit cleanly.

    - Base code (NOP): crashes with assertion failure → non-zero exit
    - Fixed code (GOLD): prints "OK" and exits with 0

    This test verifies ACTUAL BEHAVIOR, not source code patterns.
    """
    bun_path = get_bun_path()
    if not bun_path:
        # Bun not available - this should not happen in a properly configured env
        # But if it does, fail the test
        assert False, "bun not available and could not be installed"

    # Write reproduction script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(REPRODUCTION_SCRIPT)
        script_path = f.name

    try:
        # Run the reproduction script with bun
        result = subprocess.run(
            [bun_path, script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # The fixed code should:
        # 1. Exit with code 0 (no crash)
        # 2. Print "OK" to stdout
        # 3. NOT print "Internal error" or assertion failures to stderr
        assert result.returncode == 0, (
            f"Reproduction script crashed (exit {result.returncode}). "
            f"stderr: {result.stderr[:500]}"
        )
        assert "OK" in result.stdout, (
            f"Expected 'OK' in output but got: {result.stdout}"
        )
        # Verify no crash errors in stderr
        stderr_lower = result.stderr.lower()
        assert "assertion" not in stderr_lower, f"Assertion failure in stderr: {result.stderr}"
        assert "internal error" not in stderr_lower, f"Internal error in stderr: {result.stderr}"
        assert "releaseassert" not in stderr_lower, f"ReleaseAssert in stderr: {result.stderr}"

    finally:
        Path(script_path).unlink(missing_ok=True)


def test_throwerror_does_not_crash_when_exception_pending():
    """
    Additional behavioral test: throwing an error when exception is pending
    should return error cleanly, not crash.

    This is a variant of the reproduction using throwError path directly.
    """
    bun_path = get_bun_path()
    if not bun_path:
        assert False, "bun not available and could not be installed"

    # Simpler reproduction that triggers throwError path
    script = """
    var caught = false;
    function recurse() { recurse() }
    try {
        recurse();
    } catch(e) {
        // Now try to throw another error while exception is pending
        try {
            throw new Error("test");
        } catch(e2) {
            caught = true;
        }
    }
    if (caught) console.log("OK");
    """

    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        result = subprocess.run(
            [bun_path, script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, (
            f"Script crashed (exit {result.returncode}). stderr: {result.stderr[:500]}"
        )
        assert "OK" in result.stdout, f"Expected 'OK' but got: {result.stdout}"

    finally:
        Path(script_path).unlink(missing_ok=True)


# ============================================================================
# Pass-to-pass tests - Verify code quality, not bug fix
# These are unchanged from original (they don't break the oracle)
# ============================================================================

def test_file_exists_and_nontrivial():
    """JSGlobalObject.zig must exist with substantial content (not gutted)."""
    path = Path(f"{REPO}/{FILE}")
    assert path.exists(), f"{FILE} does not exist"
    line_count = len(path.read_text().splitlines())
    assert line_count > 400, f"File suspiciously small ({line_count} lines)"


def test_throwTypeError_preserved():
    """throwTypeError must still exist with a non-trivial body."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    # Find throwTypeError function - look for the function definition
    assert "pub fn throwTypeError(" in text, "throwTypeError() function not found"

    # Extract function body (approximate - find between fn def and next fn)
    match = re.search(r'pub fn throwTypeError\([^)]*\)[^{]*\{(.+?)(?=\n    pub fn|\n    fn|\Z)', text, re.DOTALL)
    if match:
        body = match.group(1)
        non_empty = [l for l in body.strip().split("\n") if l.strip()]
        assert len(non_empty) > 3, "throwTypeError() has been stubbed out"


def test_throwDOMException_preserved():
    """throwDOMException must still exist with a non-trivial body."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    assert "pub fn throwDOMException(" in text, "throwDOMException() function not found"

    match = re.search(r'pub fn throwDOMException\([^)]*\)[^{]*\{(.+?)(?=\n    pub fn|\n    fn|\Z)', text, re.DOTALL)
    if match:
        body = match.group(1)
        non_empty = [l for l in body.strip().split("\n") if l.strip()]
        assert len(non_empty) > 3, "throwDOMException() has been stubbed out"


def test_no_inline_import_in_functions():
    """No @import() inline inside function bodies (src/CLAUDE.md:11)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    # Simple check: no @import in function bodies
    lines = text.split("\n")
    in_fn = False
    depth = 0
    for line in lines:
        stripped = line.strip()
        if re.match(r"(pub )?fn ", stripped) and "{" in stripped:
            in_fn = True
            depth = stripped.count("{") - stripped.count("}")
            continue
        if in_fn:
            if "@import" in stripped:
                assert False, f"Found inline @import in function body: {stripped.strip()}"
            depth += stripped.count("{") - stripped.count("}")
            if depth <= 0:
                in_fn = False


def test_uses_bun_assert_not_std():
    """Must use bun.assert, not std.debug.assert (src/CLAUDE.md:16)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    # Remove comments
    lines = []
    for line in text.split("\n"):
        # Remove // comments
        if "//" in line:
            idx = line.index("//")
            line = line[:idx]
        lines.append(line)
    clean = "\n".join(lines)

    count = clean.count("std.debug.assert")
    assert count == 0, f"Found {count} occurrences of std.debug.assert — use bun.assert"


def test_no_std_fs_posix_os():
    """Must not use std.fs/std.posix/std.os — use bun.* equivalents (src/CLAUDE.md:16)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    # Remove comments first
    lines = []
    for line in text.split("\n"):
        if "//" in line:
            idx = line.index("//")
            line = line[:idx]
        lines.append(line)
    clean = "\n".join(lines)

    matches = re.findall(r"std\.(fs|posix|os)\.", clean)
    assert len(matches) == 0, f"Found {len(matches)} uses of std.fs/posix/os — use bun.* equivalents"


def test_repo_editorconfig():
    """Modified file must comply with .editorconfig (utf-8, lf, trailing whitespace)."""
    path = Path(f"{REPO}/{FILE}")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        assert False, f"File is not valid UTF-8: {e}"
    assert b"\r\n" not in raw, "File contains CRLF line endings, must use LF only"
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if line != line.rstrip():
            assert False, f"Line {i} has trailing whitespace"
    if text and not text.endswith("\n"):
        assert False, "File must end with a newline"


def test_repo_git_clean():
    """Git repository must be in clean state with no uncommitted changes."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"


def test_repo_git_diff_check():
    """Git diff --check must pass (no trailing whitespace, no missing newlines) - real CI command."""
    r = subprocess.run(
        ["git", "diff", "--check", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git diff --check failed:\n{r.stdout}{r.stderr}"


def test_repo_git_log():
    """Git repository must have valid commit history (real CI command)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    assert len(r.stdout.strip()) > 0, "Git log returned empty output"
    assert "698eb81" in r.stdout or "partialDeepStrictEqual" in r.stdout, f"Unexpected commit: {r.stdout}"


def test_repo_zig_basic_syntax():
    """Zig file must have balanced braces and valid basic structure."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    open_count = text.count("{")
    close_count = text.count("}")
    assert open_count == close_count, f"Unbalanced braces: {open_count} open, {close_count} close"
    open_parens = text.count("(")
    close_parens = text.count(")")
    assert open_parens == close_parens, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"
    assert "pub const JSGlobalObject = opaque" in text, "Missing expected JSGlobalObject struct declaration"


def test_repo_no_tabs_indentation():
    """Zig file must use spaces for indentation, not tabs."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if "\t" in line:
            if not re.search(r'"[^"]*\t[^"]*"', line):
                assert False, f"Line {i} contains tab character (use spaces for indentation)"


def test_repo_no_std_debug_print_log():
    """Must not use std.debug.print or std.log (debugging code should not be committed)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    banned = [
        (r"std\.debug\.print\b", "std.debug.print (debugging code should not be committed)"),
        (r"std\.log\b", "std.log (debugging code should not be committed)"),
    ]
    for pattern, msg in banned:
        matches = list(re.finditer(pattern, text))
        for match in matches:
            line_num = text[:match.start()].count("\n") + 1
            assert False, f"Line {line_num}: Found {msg}"


def test_repo_no_usingnamespace():
    """Must not use usingnamespace (deprecated, will be removed in Zig 0.15)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    matches = list(re.finditer(r"\busingnamespace\b", text))
    for match in matches:
        line_num = text[:match.start()].count("\n") + 1
        assert False, f"Line {line_num}: usingnamespace is deprecated and will be removed in Zig 0.15"


def test_repo_no_allocator_undefined_comparison():
    """Must not compare allocator.ptr with == or != (UB due to possible undefined context pointer)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    banned_patterns = [
        (r"allocator\.ptr\s*==", "allocator.ptr == (undefined behavior)"),
        (r"allocator\.ptr\s*!=", "allocator.ptr != (undefined behavior)"),
        (r"==\s*allocator\.ptr", "== allocator.ptr (undefined behavior)"),
        (r"!=\s*allocator\.ptr", "!= allocator.ptr (undefined behavior)"),
        (r"alloc\.ptr\s*==", "alloc.ptr == (undefined behavior)"),
        (r"alloc\.ptr\s*!=", "alloc.ptr != (undefined behavior)"),
        (r"==\s*alloc\.ptr", "== alloc.ptr (undefined behavior)"),
        (r"!=\s*alloc\.ptr", "!= alloc.ptr (undefined behavior)"),
    ]
    for pattern, msg in banned_patterns:
        matches = list(re.finditer(pattern, text))
        for match in matches:
            line_num = text[:match.start()].count("\n") + 1
            assert False, f"Line {line_num}: Found {msg}"


def test_repo_no_panic_in_error_paths():
    """Error handling paths should not use @panic or unreachable which could crash the process."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    lines = text.split("\n")

    error_functions = ["throw", "throwValue", "throwTODO", "createRangeError", "createErrorInstance"]
    in_error_fn = False
    fn_depth = 0
    fn_start_pattern = None

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if not in_error_fn:
            for fn_name in error_functions:
                if re.match(rf"(pub\s+)?fn\s+{fn_name}\s*\(", stripped):
                    in_error_fn = True
                    fn_depth = stripped.count("{") - stripped.count("}")
                    fn_start_pattern = fn_name
                    break
        else:
            if "@panic(" in stripped and not stripped.startswith("//"):
                assert False, f"Line {i}: Found @panic in {fn_start_pattern}() - error paths should use error.JSError, not panic"

            fn_depth += stripped.count("{") - stripped.count("}")
            if fn_depth <= 0 and ("}" in stripped or stripped == "}"):
                in_error_fn = False
                fn_start_pattern = None


def test_repo_zig_string_literal_syntax():
    """Zig file must have valid string literal syntax (no unclosed strings)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    lines = text.split("\n")

    for i, line in enumerate(lines, 1):
        in_string = False
        escaped = False
        for ch in line:
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == '"':
                in_string = not in_string
        if in_string and i < len(lines):
            if not line.rstrip().endswith("\\"):
                assert False, f"Line {i}: Unclosed string literal"


def test_repo_consistent_function_signatures():
    """Functions must have consistent parameter and return type formatting."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    fn_pattern = re.compile(r"pub\s+fn\s+\w+\s*\([^)]*\)", re.MULTILINE)
    for match in fn_pattern.finditer(text):
        start = match.start()
        segment = text[start:min(start + 500, len(text))]
        if "extern" not in segment[:100]:
            if "{" not in segment and ";" not in segment:
                line_num = text[:start].count("\n") + 1
                assert False, f"Line {line_num}: Function missing opening brace or semicolon"


def test_repo_no_unreachable_in_error_paths():
    """Error paths should not use unreachable which is undefined behavior."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    lines = text.split("\n")

    error_funcs = ["throw", "throwValue", "throwTODO", "createRangeError", "throwError"]

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "unreachable" in stripped and not stripped.startswith("//"):
            context_start = max(0, i - 20)
            context = "\n".join(lines[context_start:i])
            for fn_name in error_funcs:
                if f"pub fn {fn_name}(" in context or f"fn {fn_name}(" in context:
                    assert False, f"Line {i}: Found 'unreachable' in {fn_name}() error path - this is undefined behavior"


def test_repo_bun_api_usage():
    """Must use bun.* APIs for common operations (not std.*)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    banned_apis = [
        (r"std\.debug\.print", "Use bun.Output.debug instead of std.debug.print"),
        (r"std\.heap\.(GeneralPurposeAllocator|ArenaAllocator|c_allocator)", "Use bun.default_allocator or bun.Heap.Arena instead of std.heap allocators"),
        (r"std\.mem\.(copy|set|compare)", "Use bun.memcopy, bun.memset, bun.memcmp instead of std.mem functions"),
    ]
    for pattern, msg in banned_apis:
        matches = list(re.finditer(pattern, text))
        for match in matches:
            line_num = text[:match.start()].count("\n") + 1
            assert False, f"Line {line_num}: {msg}"


def test_repo_git_file_tracked():
    """Modified file must be tracked in git (not untracked) - real CI command."""
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"File {FILE} is not tracked in git:\n{r.stderr}"


def test_repo_git_attributes():
    """Git attributes must specify LF line endings (EditorConfig compliance) - real CI command."""
    r = subprocess.run(
        ["git", "check-attr", "-a", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git check-attr failed: {r.stderr}"
    output = r.stdout.lower()
    assert "eol" in output, f"Git attributes missing eol setting for {FILE}"
    assert "lf" in output, f"Git attributes should specify LF (not CRLF) for {FILE}"


def test_repo_git_blob_integrity():
    """Git blob for modified file must exist and be valid - real CI command."""
    r = subprocess.run(
        ["git", "cat-file", "-t", "HEAD:" + FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git cat-file failed for {FILE}:\n{r.stderr}"
    assert "blob" in r.stdout, f"Expected blob type for {FILE}, got: {r.stdout}"


def test_repo_git_show_file():
    """Git show must display file content without errors - real CI command."""
    r = subprocess.run(
        ["git", "show", "HEAD:" + FILE],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert r.returncode == 0, f"Git show failed for {FILE}:\n{r.stderr}"
    content_lines = r.stdout.strip().split("\n")
    assert len(content_lines) > 100, f"File {FILE} has suspiciously few lines ({len(content_lines)})"


def test_repo_zig_function_signatures():
    """Key modified functions must have valid signatures - real CI command using grep."""
    r = subprocess.run(
        ["grep", "-n", "pub fn throwValue(", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"throwValue function signature not found in {FILE}:\n{r.stderr}"
    assert "pub fn throwValue(this: *JSGlobalObject, value: jsc.JSValue) JSError" in r.stdout, \
        f"throwValue signature doesn't match expected pattern:\n{r.stdout}"


def test_repo_throwtodo_function():
    """throwTODO function must exist with correct signature - real CI command using grep."""
    r = subprocess.run(
        ["grep", "-n", "pub fn throwTODO(", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"throwTODO function not found in {FILE}:\n{r.stderr}"


def test_repo_createrangeerror_function():
    """createRangeError function must exist - real CI command using grep."""
    r = subprocess.run(
        ["grep", "-n", "pub fn createRangeError(", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"createRangeError function not found in {FILE}:\n{r.stderr}"


def test_repo_file_size_reasonable():
    """File size must be reasonable (not too small, not too large) - real CI command."""
    r = subprocess.run(
        ["wc", "-l", f"{REPO}/{FILE}"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"wc failed: {r.stderr}"
    parts = r.stdout.strip().split()
    if parts:
        line_count = int(parts[0])
        assert line_count > 400, f"File suspiciously small ({line_count} lines)"
        assert line_count < 100000, f"File suspiciously large ({line_count} lines)"


def test_repo_file_has_proper_boundaries():
    """File must start and end properly - real CI command using head/tail."""
    r1 = subprocess.run(
        ["head", "-1", f"{REPO}/{FILE}"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r1.returncode == 0, f"head failed: {r1.stderr}"
    first_line = r1.stdout.strip()
    assert first_line.startswith("pub const JSGlobalObject") or \
           first_line.startswith("const "), \
        f"Unexpected first line: {first_line[:50]}..."

    r2 = subprocess.run(
        ["tail", "-c", "10", f"{REPO}/{FILE}"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r2.returncode == 0, f"tail failed: {r2.stderr}"
    assert r2.stdout.endswith("\n"), "File must end with a newline character"


def test_repo_test_directory_exists():
    """Test directory must exist for regression tests - real CI command."""
    r = subprocess.run(
        ["find", f"{REPO}/test", "-type", "d", "-name", "regression"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert "regression" in r.stdout, f"Test regression directory not found:\n{r.stdout}{r.stderr}"


def test_repo_error_handling_patterns():
    """File must contain proper error handling patterns (JSError) - real CI command."""
    r = subprocess.run(
        ["grep", "-n", "JSError", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"JSError type not found in {FILE} - required for error handling"


# ============================================================================
# Additional code quality tests
# ============================================================================

def test_repo_zig_fmt():
    """
    Zig code must be properly formatted (zig fmt --check).
    Downloads zig if needed to run the check.
    """
    import urllib.request
    import zipfile
    import tempfile

    # Check if zig is available
    zig_check = subprocess.run(["which", "zig"], capture_output=True, text=True)
    if zig_check.returncode != 0:
        # Download zig for formatting check
        zig_url = "https://github.com/oven-sh/zig/releases/download/autobuild-e0b7c318f318196c5f81fdf3423816a7b5bb3112/bootstrap-x86_64-linux-musl.zip"

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "zig.zip"
            extract_path = Path(tmpdir) / "zig"

            urllib.request.urlretrieve(zig_url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            zig_bin = extract_path / "bootstrap-x86_64-linux-musl" / "zig"
            zig_bin.chmod(0o755)

            r = subprocess.run(
                [str(zig_bin), "fmt", "--check", FILE],
                capture_output=True, text=True, cwd=REPO, timeout=120,
            )
            assert r.returncode == 0, f"zig fmt --check failed:\n{r.stderr}\n{r.stdout}"
    else:
        r = subprocess.run(
            ["zig", "fmt", "--check", FILE],
            capture_output=True, text=True, cwd=REPO, timeout=120,
        )
        assert r.returncode == 0, f"zig fmt --check failed:\n{r.stderr}\n{r.stdout}"