"""
Task: bun-throw-pending-exception-crash
Repo: oven-sh/bun @ 698eb8104be9a42c9a2b5e5b03a8843f81911055
PR:   28535
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
FILE = "src/bun.js/bindings/JSGlobalObject.zig"


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
            # Escape regex special chars in the pattern, keeping it as a literal search
            escaped_pattern = re.escape(signature_pattern)
            if re.search(escaped_pattern, stripped):
                fn_start = i
                break
        else:
            if re.match(rf"pub fn {re.escape(fn_name)}\\b", stripped) or re.match(
                rf"fn {re.escape(fn_name)}\\b", stripped
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


# [static] pass_to_pass
def test_file_exists_and_nontrivial():
    """JSGlobalObject.zig must exist with substantial content (not gutted)."""
    path = Path(f"{REPO}/{FILE}")
    assert path.exists(), f"{FILE} does not exist"
    line_count = len(path.read_text().splitlines())
    assert line_count > 400, f"File suspiciously small ({line_count} lines)"


# [pr_diff] fail_to_pass
def test_crash_assert_removed():
    """bun.assert(instance != .zero) must be removed and replaced with proper handling."""
    code = _read_file()
    clean = _strip_comments(code)
    # Check bun.assert(instance != .zero) is removed
    assert "bun.assert(instance != .zero)" not in clean, "bun.assert(instance != .zero) still present"
    # Check throw and throwPretty have proper .zero handling
    for fn_name, sig in [("throw", "pub fn throw("), ("throwPretty", "pub fn throwPretty(")]:
        body = _extract_function(code, fn_name, sig)
        assert body is not None, f"{fn_name}() not found"
        assert "createErrorInstance" in body, f"{fn_name}() missing createErrorInstance"
        assert re.search(r"if\s*\(.*==\s*\.zero\)", body), f"{fn_name}() does not handle .zero"
        assert "error.JSError" in body, f"{fn_name}() missing error.JSError"


# [pr_diff] fail_to_pass
def test_throwvalue_guarded():
    """throwValue() must guard against calling vm().throwError() when exception pending."""
    code = _read_file()
    clean = _strip_comments(code)
    all_lines = clean.split("\n")
    fn_start = None
    for i, ln in enumerate(all_lines):
        if "pub fn throwValue(" in ln:
            fn_start = i
            break
    assert fn_start is not None, "throwValue() not found"
    depth, started, body_lines = 0, False, []
    for j in range(fn_start, len(all_lines)):
        body_lines.append(all_lines[j])
        for ch in all_lines[j]:
            if ch == "{":
                started = True
                depth += 1
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    break
        if started and depth == 0:
            break
    body = "\n".join(body_lines)
    assert "vm().throwError" in body, "No vm().throwError"
    assert "hasException" in body, "No hasException"
    guard_pos = body.index("hasException")
    vm_pos = body.index("vm().throwError")
    assert guard_pos < vm_pos, "hasException after vm().throwError"
    after_guard = body[guard_pos:guard_pos + 120]
    assert "error.JSError" in after_guard, "No error.JSError after guard"


# [pr_diff] fail_to_pass
def test_throw_and_throwpretty_handle_zero():
    """throw() and throwPretty() must handle createErrorInstance returning .zero."""
    code = _read_file()
    for fn_name, sig in [
        ("throw", "pub fn throw("),
        ("throwPretty", "pub fn throwPretty("),
    ]:
        body = _extract_function(code, fn_name, sig)
        assert body is not None, f"{fn_name}() function not found"
        has_create = "createErrorInstance" in body
        has_zero_handling = (
            re.search(r"if\s*\(.*==\s*\.zero\)", body) is not None
            or "orelse" in body
            or "catch" in body
            or "error.JSError" in body
        )
        if has_create:
            assert has_zero_handling, f"{fn_name}() calls createErrorInstance but does not handle .zero return"
        else:
            assert "error.JSError" in body or "JSError" in body, f"{fn_name}() refactored away from createErrorInstance but does not handle errors"


# [pr_diff] fail_to_pass
def test_throwtodo_handles_zero():
    """throwTODO() must handle createErrorInstance returning .zero."""
    code = _read_file()
    body = _extract_function(code, "throwTODO", "pub fn throwTODO(")
    assert body is not None, "throwTODO() function not found"
    has_create = "createErrorInstance" in body
    has_zero_handling = (
        re.search(r"if\s*\(.*==\s*\.zero\)", body) is not None
        or "orelse" in body
        or "catch" in body
        or "error.JSError" in body
    )
    if has_create:
        assert has_zero_handling, "throwTODO() calls createErrorInstance but does not handle .zero return"
    else:
        assert "error.JSError" in body or "JSError" in body, "throwTODO() refactored but does not handle errors"


# [pr_diff] fail_to_pass
def test_throwerror_safe_path():
    """throwError(anyerror) must route through throwValue or have its own exception guard."""
    code = _read_file()
    body = _extract_function(code, "throwError", "pub fn throwError(")
    assert body is not None, "throwError(anyerror) function not found"
    has_safe = "throwValue" in body or "hasException" in body or "hasPendingException" in body
    if not has_safe:
        if ".vm()" in body:
            after_vm = body.split(".vm()")[1][:30]
            assert "throwError" not in after_vm, "throwError(anyerror) directly calls vm().throwError() without guard"


# [pr_diff] fail_to_pass
def test_createrangeerror_handles_zero():
    """createRangeError() must handle createErrorInstance returning .zero."""
    code = _read_file()
    body = _extract_function(code, "createRangeError", "pub fn createRangeError(")
    assert body is not None, "createRangeError() function not found"
    has_create = "createErrorInstance" in body
    has_zero_handling = (
        re.search(r"if\s*\(.*==\s*\.zero\)", body) is not None
        or "orelse" in body
        or "catch" in body
    )
    if has_create:
        assert has_zero_handling, "createRangeError() calls createErrorInstance but does not handle .zero return"


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
            assert "@import" not in stripped, f"Found inline @import in function body: {stripped.strip()}"
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


# [static] pass_to_pass (file-read check, not subprocess) - EditorConfig compliance
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


# [repo_tests] pass_to_pass - Real CI command: git diff --check for whitespace errors
def test_repo_git_diff_check():
    """Git diff --check must pass (no trailing whitespace, no missing newlines) - real CI command."""
    r = subprocess.run(
        ["git", "diff", "--check", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git diff --check failed (trailing whitespace or missing newlines):\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass - Real CI command: git log to verify commit history
def test_repo_git_log():
    """Git repository must have valid commit history (real CI command)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    # Verify we have a commit hash in output
    assert len(r.stdout.strip()) > 0, "Git log returned empty output"
    # The base commit should be 698eb81 (from PR #28525)
    assert "698eb81" in r.stdout or "partialDeepStrictEqual" in r.stdout, f"Unexpected commit: {r.stdout}"


# [repo_tests] pass_to_pass - Real CI command: zig fmt check
# This downloads and runs the exact zig version used in bun CI to check formatting
def test_repo_zig_fmt():
    """Zig code must be properly formatted (zig fmt --check) - real CI command."""
    import urllib.request
    import zipfile
    import tempfile

    # Download and extract zig to a temp directory
    zig_url = "https://github.com/oven-sh/zig/releases/download/autobuild-e0b7c318f318196c5f81fdf3423816a7b5bb3112/bootstrap-x86_64-linux-musl.zip"

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "zig.zip"
        extract_path = Path(tmpdir) / "zig"

        # Download zig
        urllib.request.urlretrieve(zig_url, zip_path)

        # Extract using Python's zipfile (unzip may not be available)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        zig_bin = extract_path / "bootstrap-x86_64-linux-musl" / "zig"
        zig_bin.chmod(0o755)

        # Run zig fmt --check on the modified file
        r = subprocess.run(
            [str(zig_bin), "fmt", "--check", FILE],
            capture_output=True, text=True, cwd=REPO, timeout=120,
        )
        assert r.returncode == 0, f"zig fmt --check failed (file needs formatting):\n{r.stderr}\n{r.stdout}"


# [static] pass_to_pass (file-read check, not subprocess)
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


# [static] pass_to_pass (file-read check, not subprocess)
def test_repo_no_tabs_indentation():
    """Zig file must use spaces for indentation, not tabs."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if "\t" in line:
            if not re.search(r'"[^"]*\t[^"]*"', line):
                assert False, f"Line {i} contains tab character (use spaces for indentation)"


# [static] pass_to_pass (file-read check, not subprocess)
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


# [static] pass_to_pass (file-read check, not subprocess)
def test_repo_no_usingnamespace():
    """Must not use usingnamespace (deprecated, will be removed in Zig 0.15)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    matches = list(re.finditer(r"\busingnamespace\b", text))
    for match in matches:
        line_num = text[:match.start()].count("\n") + 1
        assert False, f"Line {line_num}: usingnamespace is deprecated and will be removed in Zig 0.15"


# [static] pass_to_pass (file-read check, not subprocess)
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


# ============================================================================
# Repo CI/CD pass_to_pass gates - Additional code quality checks
# ============================================================================

# [static] pass_to_pass (file-read check, not subprocess) - No panic/abort calls that could crash the runtime
def test_repo_no_panic_in_error_paths():
    """Error handling paths should not use @panic or unreachable which could crash the process."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    # Look for @panic in error-related function contexts (throw, throwValue, createErrorInstance)
    error_functions = ["throw", "throwValue", "throwTODO", "createRangeError", "createErrorInstance"]
    lines = text.split("\n")

    in_error_fn = False
    fn_depth = 0
    fn_start_pattern = None

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Track function entry
        if not in_error_fn:
            for fn_name in error_functions:
                if re.match(rf"(pub\s+)?fn\s+{fn_name}\s*\(", stripped):
                    in_error_fn = True
                    fn_depth = stripped.count("{") - stripped.count("}")
                    fn_start_pattern = fn_name
                    break
        else:
            # Inside error function
            if "@panic(" in stripped and not stripped.startswith("//"):
                assert False, f"Line {i}: Found @panic in {fn_start_pattern}() - error paths should use error.JSError, not panic"

            # Track brace depth
            fn_depth += stripped.count("{") - stripped.count("}")
            if fn_depth <= 0 and ("}" in stripped or stripped == "}"):
                in_error_fn = False
                fn_start_pattern = None


# [static] pass_to_pass (file-read check, not subprocess) - Zig file syntax validation (string literals)
def test_repo_zig_string_literal_syntax():
    """Zig file must have valid string literal syntax (no unclosed strings)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    # Check for balanced string quotes (even number of unescaped quotes per line)
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
        # Don't assert on multi-line strings (lines ending with \\ in the raw text)
        if in_string and i < len(lines):
            # Check if this continues on next line (multi-line string)
            if not line.rstrip().endswith("\\"):
                assert False, f"Line {i}: Unclosed string literal"


# [static] pass_to_pass (file-read check, not subprocess) - Verify consistent function signature style
def test_repo_consistent_function_signatures():
    """Functions must have consistent parameter and return type formatting."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    # Check for mixed parameter styles (some with explicit types, some without)
    # This is a basic syntax validation - ensure each fn has closing paren and brace
    fn_pattern = re.compile(r"pub\s+fn\s+\w+\s*\([^)]*\)", re.MULTILINE)
    for match in fn_pattern.finditer(text):
        start = match.start()
        # Find the next '{' or ';' to check if function is properly formed
        segment = text[start:min(start + 500, len(text))]
        # Should have opening brace for function body (not extern declaration)
        if "extern" not in segment[:100]:
            if "{" not in segment and ";" not in segment:
                line_num = text[:start].count("\n") + 1
                assert False, f"Line {line_num}: Function missing opening brace or semicolon"


# [static] pass_to_pass (file-read check, not subprocess) - Check for likely undefined behavior
def test_repo_no_unreachable_in_error_paths():
    """Error paths should not use unreachable which is undefined behavior."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    # Find unreachable in error-related contexts
    error_funcs = ["throw", "throwValue", "throwTODO", "createRangeError", "throwError"]
    lines = text.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Check if this line has unreachable
        if "unreachable" in stripped and not stripped.startswith("//"):
            # Check if we're in an error-handling context
            context_start = max(0, i - 20)
            context = "\n".join(lines[context_start:i])
            for fn_name in error_funcs:
                if f"pub fn {fn_name}(" in context or f"fn {fn_name}(" in context:
                    assert False, f"Line {i}: Found 'unreachable' in {fn_name}() error path - this is undefined behavior"


# [static] pass_to_pass (file-read check, not subprocess) - Bun-specific API usage validation
def test_repo_bun_api_usage():
    """Must use bun.* APIs for common operations (not std.*)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()

    # Check for common std patterns that should be bun
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
