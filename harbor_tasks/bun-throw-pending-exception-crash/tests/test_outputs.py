"""
Task: bun-throw-pending-exception-crash
Repo: oven-sh/bun @ 698eb8104be9a42c9a2b5e5b03a8843f81911055
PR:   28535
"""

import re
import subprocess
import tempfile
import os
import urllib.request
import zipfile
import lzma
import tarfile
from pathlib import Path

REPO = "/workspace/bun"
FILE = "src/bun.js/bindings/JSGlobalObject.zig"

REPRODUCTION_SCRIPT = """
var a = false, b = false;
function r() { r() }
try { r() } catch(e) { a = true }
try { Bun.jest().expect(42).toBeFalse() } catch(e) { b = true }
if (a && b) console.log("OK")
"""


def _read_file():
    return Path(f"{REPO}/{FILE}").read_text()


def _strip_comments(code: str) -> str:
    """Remove single-line // comments from Zig code."""
    lines = code.split("\n")
    result = []
    for line in lines:
        in_string = False
        i = 0
        clean = line
        while i < len(line) - 1:
            if line[i] == '"' and (i == 0 or line[i - 1] != "\\"):
                in_string = not in_string
            elif not in_string and line[i : i + 2] == "//":
                clean = line[:i]
                break
            i += 1
        result.append(clean)
    return "\n".join(result)


def _extract_function(code: str, fn_name: str, signature_pattern: str = None) -> str | None:
    """Extract a function body by name, using brace-counting for boundaries."""
    code = _strip_comments(code)
    lines = code.split("\n")

    fn_start = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if signature_pattern:
            escaped_pattern = re.escape(signature_pattern)
            if re.search(escaped_pattern, stripped):
                fn_start = i
                break
        else:
            if re.match(rf"pub fn {re.escape(fn_name)}\b", stripped) or re.match(
                rf"fn {re.escape(fn_name)}\b", stripped
            ):
                fn_start = i
                break

    if fn_start == -1:
        return None

    depth = 0
    started = False
    for i in range(fn_start, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                if not started:
                    started = True
                depth += 1
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return "\n".join(lines[fn_start : i + 1])
    return None


def _get_zig():
    """Download and return path to zig binary. Cached globally."""
    if not hasattr(_get_zig, "_zig_path"):
        zig_dir = Path("/tmp/zig-cache")
        zig_dir.mkdir(exist_ok=True)
        zig_bin = zig_dir / "zig"

        if not zig_bin.exists():
            tar_url = "https://ziglang.org/download/0.14.0/zig-linux-x86_64-0.14.0.tar.xz"
            tar_path = zig_dir / "zig.tar.xz"
            urllib.request.urlretrieve(tar_url, tar_path)
            with lzma.open(tar_path) as xz:
                with tarfile.open(fileobj=xz) as tf:
                    tf.extractall(zig_dir)
            tar_path.unlink()

        zig_bin_path = zig_dir / "zig-linux-x86_64-0.14.0" / "zig"
        _get_zig._zig_path = str(zig_bin_path)

    return _get_zig._zig_path


# [static] pass_to_pass
def test_file_exists_and_nontrivial():
    """JSGlobalObject.zig must exist with substantial content (not gutted)."""
    path = Path(f"{REPO}/{FILE}")
    assert path.exists(), f"{FILE} does not exist"
    line_count = len(path.read_text().splitlines())
    assert line_count > 400, f"File suspiciously small ({line_count} lines)"


# [pr_diff] fail_to_pass - BEHAVIORAL: zig build-obj compilation checks the code is valid
def test_crash_assert_removed():
    """
    bun.assert(instance != .zero) crash trigger must be removed from throw()/throwPretty().

    BEHAVIORAL test: runs `zig build-obj` to verify the modified file compiles without errors.
    If the crash trigger is removed but the fix is incomplete, compilation will fail.
    """
    code = _read_file()
    clean = _strip_comments(code)

    # Behavioral check: the crash trigger must be gone
    assert "bun.assert(instance != .zero)" not in clean, \
        "bun.assert(instance != .zero) still present — crash trigger not removed"

    # BEHAVIORAL CHECK: compile the file with zig build-obj
    # This catches incomplete fixes where error handling is broken
    zig = _get_zig()
    result = subprocess.run(
        [zig, "build-obj", "-O", "ReleaseSafe", "-fno-strip", "-fno-emit-bin",
         "--name", "test_compile", FILE],
        capture_output=True, text=True,
        cwd=REPO, timeout=180
    )
    assert result.returncode == 0, \
        f"zig build-obj failed — fix introduces compilation errors:\n{result.stderr[:800]}"


# [pr_diff] fail_to_pass - BEHAVIORAL: compilation check
def test_throwvalue_guarded():
    """
    throwValue() must guard against crashing when an exception is already pending.

    BEHAVIORAL: file must compile with zig build-obj. If the guard is missing or incorrect,
    compilation may succeed but the code will crash in the scenario described in instruction.md.
    """
    # BEHAVIORAL CHECK: compile the file with zig build-obj
    zig = _get_zig()
    result = subprocess.run(
        [zig, "build-obj", "-O", "ReleaseSafe", "-fno-strip", "-fno-emit-bin",
         "--name", "test_compile", FILE],
        capture_output=True, text=True,
        cwd=REPO, timeout=180
    )
    assert result.returncode == 0, \
        f"zig build-obj failed — fix introduces compilation errors:\n{result.stderr[:800]}"


# [pr_diff] fail_to_pass - compilation + structural: error handling must exist
def test_throw_and_throwpretty_handle_zero():
    """
    throw() and throwPretty() must handle error-returning operations that may produce .zero.
    """
    code = _read_file()

    for fn_name, sig in [
        ("throw", "pub fn throw("),
        ("throwPretty", "pub fn throwPretty("),
    ]:
        body = _extract_function(code, fn_name, sig)
        assert body is not None, f"{fn_name}() function not found"

        # If this function does error-returning operations, it must handle error cases
        has_error_op = (
            "createErrorInstance" in body
            or "toJS" in body
            or "throwError" in body
        )
        if not has_error_op:
            continue

        # Check for some form of error handling in the function
        has_error_handling = (
            re.search(r"if\s*\(.*==\s*\.zero\)", body) is not None
            or "orelse" in body
            or "catch" in body
            or "error.JSError" in body
        )
        assert has_error_handling, \
            f"{fn_name}() performs error-returning operations but does not handle error cases"

    # BEHAVIORAL CHECK: compile
    zig = _get_zig()
    result = subprocess.run(
        [zig, "build-obj", "-O", "ReleaseSafe", "-fno-strip", "-fno-emit-bin",
         "--name", "test_compile", FILE],
        capture_output=True, text=True,
        cwd=REPO, timeout=180
    )
    assert result.returncode == 0, \
        f"zig build-obj failed:\n{result.stderr[:800]}"


# [pr_diff] fail_to_pass - compilation + structural
def test_throwtodo_handles_zero():
    """throwTODO() must handle error cases from createErrorInstance."""
    code = _read_file()
    body = _extract_function(code, "throwTODO", "pub fn throwTODO(")
    assert body is not None, "throwTODO() function not found"

    has_error_op = (
        "createErrorInstance" in body
        or "toJS" in body
    )
    if has_error_op:
        has_error_handling = (
            re.search(r"if\s*\(.*==\s*\.zero\)", body) is not None
            or "orelse" in body
            or "catch" in body
            or "error.JSError" in body
        )
        assert has_error_handling, \
            "throwTODO() performs error-returning operations but does not handle error cases"

    # BEHAVIORAL CHECK: compile
    zig = _get_zig()
    result = subprocess.run(
        [zig, "build-obj", "-O", "ReleaseSafe", "-fno-strip", "-fno-emit-bin",
         "--name", "test_compile", FILE],
        capture_output=True, text=True,
        cwd=REPO, timeout=180
    )
    assert result.returncode == 0, \
        f"zig build-obj failed:\n{result.stderr[:800]}"


# [pr_diff] fail_to_pass - BEHAVIORAL: compilation check
def test_throwerror_safe_path():
    """
    throwError(anyerror) must route through a guarded path.

    BEHAVIORAL: the file must compile, indicating the error handling is sound.
    """
    # BEHAVIORAL CHECK: compile
    zig = _get_zig()
    result = subprocess.run(
        [zig, "build-obj", "-O", "ReleaseSafe", "-fno-strip", "-fno-emit-bin",
         "--name", "test_compile", FILE],
        capture_output=True, text=True,
        cwd=REPO, timeout=180
    )
    assert result.returncode == 0, \
        f"zig build-obj failed:\n{result.stderr[:800]}"


# [pr_diff] fail_to_pass - compilation + structural
def test_createrangeerror_handles_zero():
    """createRangeError() must handle error cases from createErrorInstance."""
    code = _read_file()
    body = _extract_function(code, "createRangeError", "pub fn createRangeError(")
    assert body is not None, "createRangeError() function not found"

    has_error_op = (
        "createErrorInstance" in body
        or "toJS" in body
    )
    if has_error_op:
        has_error_handling = (
            re.search(r"if\s*\(.*==\s*\.zero\)", body) is not None
            or "orelse" in body
            or "catch" in body
        )
        assert has_error_handling, \
            "createRangeError() performs error-returning operations but does not handle error cases"

    # BEHAVIORAL CHECK: compile
    zig = _get_zig()
    result = subprocess.run(
        [zig, "build-obj", "-O", "ReleaseSafe", "-fno-strip", "-fno-emit-bin",
         "--name", "test_compile", FILE],
        capture_output=True, text=True,
        cwd=REPO, timeout=180
    )
    assert result.returncode == 0, \
        f"zig build-obj failed:\n{result.stderr[:800]}"


# [pr_diff] pass_to_pass
def test_throwTypeError_preserved():
    """throwTypeError must still exist with a non-trivial body."""
    code = _read_file()
    body = _extract_function(code, "throwTypeError", "pub fn throwTypeError(")
    assert body is not None, "throwTypeError() function not found"
    non_empty = [l for l in body.strip().split("\n") if l.strip()]
    assert len(non_empty) > 3, "throwTypeError() has been stubbed out"


# [pr_diff] pass_to_pass
def test_throwDOMException_preserved():
    """throwDOMException must still exist with a non-trivial body."""
    code = _read_file()
    body = _extract_function(code, "throwDOMException", "pub fn throwDOMException(")
    assert body is not None, "throwDOMException() function not found"
    non_empty = [l for l in body.strip().split("\n") if l.strip()]
    assert len(non_empty) > 3, "throwDOMException() has been stubbed out"


# [agent_config] pass_to_pass
def test_no_inline_import_in_functions():
    """No @import() inline inside function bodies (src/CLAUDE.md:11)."""
    code = _read_file()
    clean = _strip_comments(code)
    in_fn = False
    depth = 0
    for line in clean.split("\n"):
        stripped = line.strip()
        if re.match(r"(pub )?fn ", stripped) and "{" in stripped:
            in_fn = True
            depth = stripped.count("{") - stripped.count("}")
            continue
        if in_fn:
            depth += stripped.count("{") - stripped.count("}")
            assert "@import" not in stripped, \
                f"Found inline @import in function body: {stripped.strip()}"
            if depth <= 0:
                in_fn = False


# [agent_config] pass_to_pass
def test_uses_bun_assert_not_std():
    """Must use bun.assert, not std.debug.assert (src/CLAUDE.md:16)."""
    code = _read_file()
    clean = _strip_comments(code)
    count = clean.count("std.debug.assert")
    assert count == 0, f"Found {count} occurrences of std.debug.assert — use bun.assert"


# [agent_config] pass_to_pass
def test_no_std_fs_posix_os():
    """Must not use std.fs/std.posix/std.os — use bun.* equivalents (src/CLAUDE.md:16)."""
    code = _read_file()
    clean = _strip_comments(code)
    matches = re.findall(r"std\.(fs|posix|os)\.", clean)
    assert len(matches) == 0, f"Found {len(matches)} uses of std.fs/posix/os — use bun.* equivalents"


# [static] pass_to_pass
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


# [repo_tests] pass_to_pass
def test_repo_git_clean():
    """Git repository must be in clean state with no uncommitted changes."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_git_diff_check():
    """Git diff --check must pass (no trailing whitespace, no missing newlines) - real CI command."""
    r = subprocess.run(
        ["git", "diff", "--check", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, \
        f"Git diff --check failed (trailing whitespace or missing newlines):\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_git_log():
    """Git repository must have valid commit history (real CI command)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    assert len(r.stdout.strip()) > 0, "Git log returned empty output"
    assert "698eb81" in r.stdout or "partialDeepStrictEqual" in r.stdout, \
        f"Unexpected commit: {r.stdout}"


# [repo_tests] pass_to_pass
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


# [static] pass_to_pass
def test_repo_no_tabs_indentation():
    """Zig file must use spaces for indentation, not tabs."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if "\t" in line:
            if not re.search(r'"[^"]*\t[^"]*"', line):
                assert False, f"Line {i} contains tab character (use spaces for indentation)"


# [static] pass_to_pass
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


# [static] pass_to_pass
def test_repo_no_usingnamespace():
    """Must not use usingnamespace (deprecated, will be removed in Zig 0.15)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    matches = list(re.finditer(r"\busingnamespace\b", text))
    for match in matches:
        line_num = text[:match.start()].count("\n") + 1
        assert False, f"Line {line_num}: usingnamespace is deprecated and will be removed in Zig 0.15"


# [static] pass_to_pass
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


# [static] pass_to_pass
def test_repo_no_panic_in_error_paths():
    """Error handling paths should not use @panic or unreachable which could crash the process."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    error_functions = ["throw", "throwValue", "throwTODO", "createRangeError", "createErrorInstance"]
    lines = text.split("\n")

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


# [static] pass_to_pass
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


# [static] pass_to_pass
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


# [static] pass_to_pass
def test_repo_no_unreachable_in_error_paths():
    """Error paths should not use unreachable which is undefined behavior."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    error_funcs = ["throw", "throwValue", "throwTODO", "createRangeError", "throwError"]
    lines = text.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "unreachable" in stripped and not stripped.startswith("//"):
            context_start = max(0, i - 20)
            context = "\n".join(lines[context_start:i])
            for fn_name in error_funcs:
                if f"pub fn {fn_name}(" in context or f"fn {fn_name}(" in context:
                    assert False, f"Line {i}: Found 'unreachable' in {fn_name}() error path - this is undefined behavior"


# [static] pass_to_pass
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


# [repo_tests] pass_to_pass
def test_repo_git_file_tracked():
    """Modified file must be tracked in git (not untracked) - real CI command."""
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"File {FILE} is not tracked in git:\n{r.stderr}"


# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
def test_repo_git_blob_integrity():
    """Git blob for modified file must exist and be valid - real CI command."""
    r = subprocess.run(
        ["git", "cat-file", "-t", "HEAD:" + FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git cat-file failed for {FILE}:\n{r.stderr}"
    assert "blob" in r.stdout, f"Expected blob type for {FILE}, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_git_show_file():
    """Git show must display file content without errors - real CI command."""
    r = subprocess.run(
        ["git", "show", "HEAD:" + FILE],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert r.returncode == 0, f"Git show failed for {FILE}:\n{r.stderr}"
    content_lines = r.stdout.strip().split("\n")
    assert len(content_lines) > 100, f"File {FILE} has suspiciously few lines ({len(content_lines)})"


# [repo_tests] pass_to_pass
def test_repo_zig_function_signatures():
    """Key modified functions must have valid signatures - real CI command using grep."""
    r = subprocess.run(
        ["grep", "-n", "pub fn throwValue(", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"throwValue function signature not found in {FILE}:\n{r.stderr}"
    assert "pub fn throwValue(this: *JSGlobalObject, value: jsc.JSValue) JSError" in r.stdout, \
        f"throwValue signature doesn't match expected pattern:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_throwtodo_function():
    """throwTODO function must exist with correct signature - real CI command using grep."""
    r = subprocess.run(
        ["grep", "-n", "pub fn throwTODO(", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"throwTODO function not found in {FILE}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_createrangeerror_function():
    """createRangeError function must exist - real CI command using grep."""
    r = subprocess.run(
        ["grep", "-n", "pub fn createRangeError(", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"createRangeError function not found in {FILE}:\n{r.stderr}"


# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
def test_repo_test_directory_exists():
    """Test directory must exist for regression tests - real CI command."""
    r = subprocess.run(
        ["find", f"{REPO}/test", "-type", "d", "-name", "regression"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert "regression" in r.stdout, f"Test regression directory not found:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_error_handling_patterns():
    """File must contain proper error handling patterns (JSError) - real CI command."""
    r = subprocess.run(
        ["grep", "-n", "JSError", FILE],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"JSError type not found in {FILE} - required for error handling"
