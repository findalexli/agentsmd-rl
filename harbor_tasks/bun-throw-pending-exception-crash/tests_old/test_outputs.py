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
            if re.search(signature_pattern, stripped):
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
    script = """
import re, sys
code = open("/workspace/bun/src/bun.js/bindings/JSGlobalObject.zig").read()
clean_lines = []
for line in code.split("\n"):
    in_str, cln = False, line
    for i in range(len(line) - 1):
        if line[i] == '"' and (i == 0 or line[i-1] != "\\\\"):
            in_str = not in_str
        elif not in_str and line[i:i+2] == "//":
            cln = line[:i]
            break
    clean_lines.append(cln)
clean = "\n".join(clean_lines)
if "bun.assert(instance != .zero)" in clean:
    print("bun.assert(instance != .zero) still present", file=sys.stderr)
    sys.exit(1)
for fn_sig in ["pub fn throw(this", "pub fn throwPretty("]:
    found = False
    all_lines = clean.split("\n")
    for i, ln in enumerate(all_lines):
        if fn_sig in ln:
            depth, started, body_lines = 0, False, []
            for j in range(i, len(all_lines)):
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
            if "createErrorInstance" not in body:
                print("Missing createErrorInstance", file=sys.stderr)
                sys.exit(1)
            if not re.search(r"if\s*\(.*==\s*\.zero\)", body):
                print("Does not handle .zero", file=sys.stderr)
                sys.exit(1)
            if "error.JSError" not in body:
                print("Missing error.JSError", file=sys.stderr)
                sys.exit(1)
            found = True
            break
    if not found:
        print(f"Function with {fn_sig} not found", file=sys.stderr)
        sys.exit(1)
print("PASS")
"""
    r = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"Crash assert check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_throwvalue_guarded():
    """throwValue() must guard against calling vm().throwError() when exception pending."""
    script = """
import sys
code = open("/workspace/bun/src/bun.js/bindings/JSGlobalObject.zig").read()
clean_lines = []
for line in code.split("\n"):
    in_str, cln = False, line
    for i in range(len(line) - 1):
        if line[i] == '"' and (i == 0 or line[i-1] != "\\\\"):
            in_str = not in_str
        elif not in_str and line[i:i+2] == "//":
            cln = line[:i]
            break
    clean_lines.append(cln)
clean = "\n".join(clean_lines)
all_lines = clean.split("\n")
fn_start = None
for i, ln in enumerate(all_lines):
    if "pub fn throwValue(" in ln:
        fn_start = i
        break
if fn_start is None:
    print("throwValue() not found", file=sys.stderr)
    sys.exit(1)
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
if "vm().throwError" not in body:
    print("No vm().throwError", file=sys.stderr)
    sys.exit(1)
if "hasException" not in body:
    print("No hasException", file=sys.stderr)
    sys.exit(1)
guard_pos = body.index("hasException")
vm_pos = body.index("vm().throwError")
if guard_pos >= vm_pos:
    print("hasException after vm().throwError", file=sys.stderr)
    sys.exit(1)
after_guard = body[guard_pos:guard_pos + 120]
if "error.JSError" not in after_guard:
    print("No error.JSError after guard", file=sys.stderr)
    sys.exit(1)
print("PASS")
"""
    r = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"throwValue guard check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_throw_and_throwpretty_handle_zero():
    """throw() and throwPretty() must handle createErrorInstance returning .zero."""
    code = _read_file()
    for fn_name, sig in [
        ("throw", "pub fn throw(this.*comptime fmt"),
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
    body = _extract_function(code, "throwError", "pub fn throwError(this.*err:\s*anyerror")
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


# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
def test_repo_no_tabs_indentation():
    """Zig file must use spaces for indentation, not tabs."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if "\t" in line:
            if not re.search(r'"[^"]*\t[^"]*"', line):
                assert False, f"Line {i} contains tab character (use spaces for indentation)"


# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
def test_repo_no_usingnamespace():
    """Must not use usingnamespace (deprecated, will be removed in Zig 0.15)."""
    path = Path(f"{REPO}/{FILE}")
    text = path.read_text()
    matches = list(re.finditer(r"\busingnamespace\b", text))
    for match in matches:
        line_num = text[:match.start()].count("\n") + 1
        assert False, f"Line {line_num}: usingnamespace is deprecated and will be removed in Zig 0.15"


# [repo_tests] pass_to_pass
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
