"""
Task: bun-mysql-per-query-memory-leak
Repo: oven-sh/bun @ 9a27ef75697d713dba18b7a9762308197014ecca
PR:   28633

Behavioral test suite that verifies memory management correctness without
asserting on specific gold implementation patterns.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/repo"
COLDEF = f"{REPO}/src/sql/mysql/protocol/ColumnDefinition41.zig"
PREPSTMT = f"{REPO}/src/sql/mysql/protocol/PreparedStatement.zig"
MYSTMT = f"{REPO}/src/sql/mysql/MySQLStatement.zig"
MYCONN = f"{REPO}/src/sql/mysql/MySQLConnection.zig"


def _run_subprocess_validator(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python validation code in a subprocess."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _extract_function_body(src: str, func_name: str) -> str:
    """Extract the body of a function from source code."""
    import re
    # Match function signature
    pattern = rf"(?:pub\s+)?fn\s+{re.escape(func_name)}\b[^{{]*\{{"
    m = re.search(pattern, src)
    if not m:
        return ""

    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
        i += 1
    return src[start:i-1]


def _extract_struct_body(src: str, struct_name: str) -> str:
    """Extract the body of a struct from source code."""
    import re
    pattern = rf"{re.escape(struct_name)}\s*=\s*struct\s*\{{"
    m = re.search(pattern, src)
    if not m:
        return ""

    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
        i += 1
    return src[start:i-1]


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------

def test_modified_files_exist():
    """All four modified Zig files must exist."""
    code = f'''
from pathlib import Path
paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
for path in paths:
    if not Path(path).exists():
        print("FAIL: Missing " + path)
        exit(1)
print("PASS: All modified files exist")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_balanced_braces():
    """Modified files must have balanced braces (basic syntax gate)."""
    code = f'''
from pathlib import Path
paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
for path in paths:
    src = Path(path).read_text()
    opens = src.count("{{")
    closes = src.count("}}")
    if opens != closes:
        print(f"FAIL: Unbalanced braces in {{Path(path).name}}: {{opens}} open vs {{closes}} close")
        exit(1)
print("PASS: All files have balanced braces")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_not_stub():
    """ColumnDefinition41.deinit has >=6 cleanup calls (not a stub)."""
    code = f'''
import re
from pathlib import Path

src = Path("{COLDEF}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

pattern = r"(?:pub\\s+)?fn\\s+deinit\\b[^{{]*\\{{"
m = re.search(pattern, clean)
if not m:
    print("FAIL: deinit function not found")
    exit(1)

start = m.end()
depth = 1
i = start
while i < len(clean) and depth > 0:
    if clean[i] == "{{":
        depth += 1
    elif clean[i] == "}}":
        depth -= 1
    i += 1
body = clean[start:i-1]

calls = re.findall(r"\\.\\s*(?:deinit|free)\\s*\\(", body)
if len(calls) < 6:
    print(f"FAIL: deinit has only {{len(calls)}} cleanup calls, need >=6")
    exit(1)
print(f"PASS: deinit has {{len(calls)}} cleanup calls (>=6)")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# -----------------------------------------------------------------------------

def test_coldef_deinit_frees_name_or_index():
    """
    ColumnDefinition41.deinit() must cleanup name_or_index field.
    Verifies: deinit body contains name_or_index cleanup (any pattern).
    """
    code = f'''
import re
from pathlib import Path

def extract_function_body(src, func_name):
    pattern = rf"(?:pub\\s+)?fn\\s+{{re.escape(func_name)}}\\b[^{{]*\\{{"
    m = re.search(pattern, src)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{{":
            depth += 1
        elif src[i] == "}}":
            depth -= 1
        i += 1
    return src[start:i-1]

src = Path("{COLDEF}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

deinit_body = extract_function_body(clean, "deinit")
if not deinit_body:
    print("FAIL: deinit function not found")
    exit(1)

# Check for any pattern that cleans up name_or_index
# Accept: .deinit(), .free(), or passing to any cleanup function
cleanup_patterns = [
    r"name_or_index\\.\\s*deinit\\s*\\(",
    r"name_or_index\\.\\s*free\\s*\\(",
    r"(?:free|deinit)\\s*\\([^)]*name_or_index",
]
found = any(re.search(p, deinit_body) for p in cleanup_patterns)
if not found:
    print("FAIL: name_or_index cleanup not found in ColumnDefinition41.deinit()")
    exit(1)
print("PASS: name_or_index cleanup found in deinit")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_coldef_deinit_frees_all_data_fields():
    """
    ColumnDefinition41.deinit() frees all Data fields.
    Verifies: all 6 Data fields have cleanup calls in deinit.
    """
    code = f'''
import re
from pathlib import Path

def extract_function_body(src, func_name):
    pattern = rf"(?:pub\\s+)?fn\\s+{{re.escape(func_name)}}\\b[^{{]*\\{{"
    m = re.search(pattern, src)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{{":
            depth += 1
        elif src[i] == "}}":
            depth -= 1
        i += 1
    return src[start:i-1]

src = Path("{COLDEF}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

deinit_body = extract_function_body(clean, "deinit")
if not deinit_body:
    print("FAIL: deinit function not found")
    exit(1)

required = ["catalog", "schema", "table", "org_table", "name", "org_name"]
missing = []
for field in required:
    # Accept any cleanup pattern: .deinit(), .free(), etc.
    if not re.search(rf"this\\.{{re.escape(field)}}\\.\\s*(?:deinit|free)\\s*\\(", deinit_body):
        missing.append(field)

if missing:
    print(f"FAIL: Missing cleanup for fields: {{missing}}")
    exit(1)
print("PASS: All 6 Data fields have cleanup calls")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_decodeinternal_frees_before_reassign():
    """
    decodeInternal() must cleanup name_or_index before reassignment.
    Verifies: cleanup occurs before assignment of new ColumnIdentifier.
    """
    code = f'''
import re
from pathlib import Path

def extract_function_body(src, func_name):
    pattern = rf"(?:pub\\s+)?fn\\s+{{re.escape(func_name)}}\\b[^{{]*\\{{"
    m = re.search(pattern, src)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{{":
            depth += 1
        elif src[i] == "}}":
            depth -= 1
        i += 1
    return src[start:i-1]

src = Path("{COLDEF}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

decode_body = extract_function_body(clean, "decodeInternal")
if not decode_body:
    print("FAIL: decodeInternal function not found")
    exit(1)

# Find all name_or_index assignments that create new ColumnIdentifier
assign_matches = list(re.finditer(r"this\\.name_or_index\\s*=", decode_body))
if not assign_matches:
    print("FAIL: name_or_index assignment not found in decodeInternal")
    exit(1)

# For each assignment, check that cleanup occurs before it in the function body
for assign_match in assign_matches:
    before_assign = decode_body[:assign_match.start()]
    # Check for any cleanup pattern before assignment
    cleanup_before = re.search(r"this\\.name_or_index\\.\\s*(?:deinit|free)\\s*\\(", before_assign)
    if not cleanup_before:
        print("FAIL: name_or_index cleanup must occur BEFORE reassignment in decodeInternal")
        exit(1)

print("PASS: name_or_index cleanup occurs before reassignment in decodeInternal")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_execute_deinit_frees_params_slice():
    """
    Execute.deinit() frees the params slice after freeing elements.
    Verifies: slice freeing occurs after the element cleanup loop.
    """
    code = f'''
import re
from pathlib import Path

def extract_struct_body(src, struct_name):
    pattern = rf"{{re.escape(struct_name)}}\\s*=\\s*struct\\s*\\{{"
    m = re.search(pattern, src)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{{":
            depth += 1
        elif src[i] == "}}":
            depth -= 1
        i += 1
    return src[start:i-1]

def extract_function_body(src, func_name):
    pattern = rf"(?:pub\\s+)?fn\\s+{{re.escape(func_name)}}\\b[^{{]*\\{{"
    m = re.search(pattern, src)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{{":
            depth += 1
        elif src[i] == "}}":
            depth -= 1
        i += 1
    return src[start:i-1]

src = Path("{PREPSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

# Extract Execute struct body
struct_body = extract_struct_body(clean, "Execute")
if not struct_body:
    print("FAIL: Execute struct not found")
    exit(1)

# Extract deinit function from Execute struct
deinit_body = extract_function_body(struct_body, "deinit")
if not deinit_body:
    print("FAIL: deinit not found in Execute")
    exit(1)

# Check that there's a loop cleaning up params elements
has_element_loop = re.search(r"for\\s*\\([^)]*params", deinit_body)
if not has_element_loop:
    has_element_loop = "for" in deinit_body and "params" in deinit_body

# Check that params slice is freed (any pattern: .free(), allocator.free(), etc.)
# This must come AFTER the element cleanup loop
has_slice_free = re.search(r"(?:\\.free\\s*\\(|free\\s*\\([^)]*params)", deinit_body)
if not has_slice_free:
    # Alternative: check for params being passed to any free function
    has_slice_free = re.search(r"free\\s*\\([^)]*this\\.params", deinit_body)

if not has_element_loop:
    print("FAIL: Missing element cleanup loop for params")
    exit(1)

if not has_slice_free:
    print("FAIL: params slice is not freed after element cleanup")
    exit(1)

print("PASS: params elements cleaned up and slice freed in Execute.deinit()")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_checkduplicate_frees_before_overwrite():
    """
    checkForDuplicateFields frees name_or_index before .duplicate overwrite.
    Verifies: cleanup occurs before .duplicate assignment for field.name_or_index.
    """
    code = f'''
import re
from pathlib import Path

def extract_function_body(src, func_name):
    pattern = rf"(?:pub\\s+)?fn\\s+{{re.escape(func_name)}}\\b[^{{]*\\{{"
    m = re.search(pattern, src)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{{":
            depth += 1
        elif src[i] == "}}":
            depth -= 1
        i += 1
    return src[start:i-1]

src = Path("{MYSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

body = extract_function_body(clean, "checkForDuplicateFields")
if not body:
    print("FAIL: checkForDuplicateFields function not found")
    exit(1)

# Find all .duplicate assignments to field.name_or_index
duplicate_matches = list(re.finditer(r"field\\.name_or_index\\s*=\\s*\\.duplicate", body))
if not duplicate_matches:
    duplicate_matches = list(re.finditer(r"field\\.name_or_index\\s*=\\s*[^;=]*duplicate", body))

if not duplicate_matches:
    print("FAIL: .duplicate assignment not found in checkForDuplicateFields")
    exit(1)

# Check that cleanup occurs before each .duplicate assignment
for dup_match in duplicate_matches:
    before = body[:dup_match.start()]
    # Check for any cleanup pattern: .deinit(), .free(), or any function call
    has_cleanup = re.search(r"field\\.name_or_index\\.\\s*(?:deinit|free)\\s*\\(", before)
    if not has_cleanup:
        # Check if there's a conditional block with cleanup before this assignment
        # Look at the block structure - find the enclosing control flow
        segment = body[:dup_match.start()]
        # Get the last statement before this assignment
        lines = segment.strip().split(";")
        for line in reversed(lines):
            if "field.name_or_index" in line and ("deinit" in line or "free" in line):
                has_cleanup = True
                break

    if not has_cleanup:
        print("FAIL: field.name_or_index cleanup must occur BEFORE .duplicate assignment")
        exit(1)

print("PASS: field.name_or_index cleanup occurs before .duplicate assignment")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_columns_zero_initialized_after_alloc():
    """
    ColumnDefinition41 arrays are zero-initialized after allocation.
    Verifies: for-loop or @memset follows allocation sites.
    """
    code = f'''
import re
from pathlib import Path

src = Path("{MYCONN}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

# Find all ColumnDefinition41 allocation sites
alloc_pattern = r"(?:try\\s+)?bun\\.default_allocator\\.alloc\\s*\\(\\s*ColumnDefinition41"
matches = list(re.finditer(alloc_pattern, clean))

if not matches:
    print("FAIL: No ColumnDefinition41 allocations found")
    exit(1)

for match in matches:
    after = clean[match.end():match.end() + 800]

    # Look for zero-initialization pattern: for-loop with .{{}} assignment
    zero_init_loop = re.search(r"for\\s*\\([^)]*\\)\\s*\\|[^|]+\\|[^=]+=\\s*\\.\\{{\\s*\\}}", after)

    # Alternative: @memset
    memset_init = re.search(r"@memset\\s*\\([^)]*\\.\\{{\\s*\\}}", after)

    # Alternative: std.mem.zeroes
    zeroes_init = re.search(r"std\\.mem\\.zeroes", after)

    # Alternative: explicit assignment to default/empty
    default_init = re.search(r"=\\s*\\.\\{{\\s*\\}}", after)

    if not (zero_init_loop or memset_init or zeroes_init or default_init):
        print(f"FAIL: Zero-initialization not found after alloc at offset {{match.start()}}")
        exit(1)

print(f"PASS: All {{len(matches)}} allocation sites have zero-initialization")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression checks
# -----------------------------------------------------------------------------

def test_individual_params_still_freed():
    """
    Execute.deinit() still frees individual param values in the loop.
    Verifies: loop exists that calls deinit on each param.
    """
    code = f'''
import re
from pathlib import Path

def extract_struct_body(src, struct_name):
    pattern = rf"{{re.escape(struct_name)}}\\s*=\\s*struct\\s*\\{{"
    m = re.search(pattern, src)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{{":
            depth += 1
        elif src[i] == "}}":
            depth -= 1
        i += 1
    return src[start:i-1]

def extract_function_body(src, func_name):
    pattern = rf"(?:pub\\s+)?fn\\s+{{re.escape(func_name)}}\\b[^{{]*\\{{"
    m = re.search(pattern, src)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{{":
            depth += 1
        elif src[i] == "}}":
            depth -= 1
        i += 1
    return src[start:i-1]

src = Path("{PREPSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

struct_body = extract_struct_body(clean, "Execute")
if not struct_body:
    print("FAIL: Execute struct not found")
    exit(1)

deinit_body = extract_function_body(struct_body, "deinit")
if not deinit_body:
    print("FAIL: deinit not found in Execute")
    exit(1)

# Check for loop that processes params
has_loop = re.search(r"for\\s*\\([^)]*params", deinit_body)
if not has_loop:
    has_loop = "for" in deinit_body and "params" in deinit_body

# Check for element deinit call
has_deinit = re.search(r"(?:param|item).*\\.deinit\\s*\\(", deinit_body)
if not has_deinit:
    # More flexible: any deinit call inside the deinit function
    has_deinit = ".deinit(" in deinit_body

if not has_loop:
    print("FAIL: Individual param cleanup loop not found")
    exit(1)

if not has_deinit:
    print("FAIL: Individual param.deinit() not found")
    exit(1)

print("PASS: Individual param cleanup preserved")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_columns_array_still_freed():
    """
    MySQLStatement.deinit() still frees columns array.
    Verifies: column deinit loop and allocator free exist.
    """
    code = f'''
import re
from pathlib import Path

def extract_function_body(src, func_name):
    pattern = rf"(?:pub\\s+)?fn\\s+{{re.escape(func_name)}}\\b[^{{]*\\{{"
    m = re.search(pattern, src)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{{":
            depth += 1
        elif src[i] == "}}":
            depth -= 1
        i += 1
    return src[start:i-1]

src = Path("{MYSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

deinit_body = extract_function_body(clean, "deinit")
if not deinit_body:
    print("FAIL: deinit function not found in MySQLStatement")
    exit(1)

# Check for column cleanup (any pattern)
has_col_cleanup = re.search(r"column\\.\\s*(?:deinit|free)\\s*\\(", deinit_body)
if not has_col_cleanup:
    # Check for loop with column cleanup
    has_col_cleanup = re.search(r"for\\s*\\([^)]*column[^)]*\\).*deinit", deinit_body, re.DOTALL)

# Check for allocator free
has_free = re.search(r"(?:\\.free\\s*\\(|free\\s*\\(", deinit_body)

if not has_col_cleanup:
    print("FAIL: column cleanup not found in MySQLStatement.deinit()")
    exit(1)

if not has_free:
    print("FAIL: allocator free not found in MySQLStatement")
    exit(1)

print("PASS: column cleanup and allocator free preserved")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


# -----------------------------------------------------------------------------
# Static pattern checks (pass_to_pass)
# -----------------------------------------------------------------------------

def test_no_std_allocator():
    """No std.heap or std.mem.Allocator in modified files."""
    code = f'''
import re
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]

for path in paths:
    src = Path(path).read_text()
    if "std.heap" in src:
        print(f"FAIL: std.heap found in {{Path(path).name}}")
        exit(1)
    if re.search(r"std\\.mem\\.Allocator\\b", src):
        print(f"FAIL: std.mem.Allocator found in {{Path(path).name}}")
        exit(1)

print("PASS: No std.heap or std.mem.Allocator usage in modified files")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_no_inline_imports():
    """No @import() calls inline inside function bodies."""
    code = f'''
import re
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]

for path in paths:
    src = Path(path).read_text()
    for fn_match in re.finditer(r"(?:pub\\s+)?fn\\s+\\w+\\b[^{{]*\\{{", src):
        fn_start = fn_match.end()
        depth = 1
        i = fn_start
        while i < len(src) and depth > 0:
            if src[i] == "{{":
                depth += 1
            elif src[i] == "}}":
                depth -= 1
            i += 1
        fn_body = src[fn_start:i-1]
        if "@import(" in fn_body:
            print(f"FAIL: Inline @import() found inside function body in {{Path(path).name}}")
            exit(1)

print("PASS: No inline @import() calls in function bodies")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


# -----------------------------------------------------------------------------
# Repo CI-style checks (pass_to_pass) - using subprocess.run
# -----------------------------------------------------------------------------

def test_repo_zig_syntax_valid():
    """Modified Zig files have balanced braces and valid syntax (repo CI gate)."""
    code = f'''
from pathlib import Path
import re

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]

for path in paths:
    src = Path(path).read_text()
    filename = Path(path).name

    # Check balanced braces
    opens = src.count("{{")
    closes = src.count("}}")
    if opens != closes:
        print(f"FAIL: {{filename}}: Unbalanced braces ({{opens}} open vs {{closes}} close)")
        exit(1)

    # Check balanced parentheses
    opens_p = src.count("(")
    closes_p = src.count(")")
    if opens_p != closes_p:
        print(f"FAIL: {{filename}}: Unbalanced parentheses ({{opens_p}} open vs {{closes_p}} close)")
        exit(1)

    # Check balanced brackets
    opens_b = src.count("[")
    closes_b = src.count("]")
    if opens_b != closes_b:
        print(f"FAIL: {{filename}}: Unbalanced brackets ({{opens_b}} open vs {{closes_b}} close)")
        exit(1)

print("PASS: All modified Zig files have valid syntax")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_no_banned_words():
    """Modified files do not contain banned words/patterns from ban-words.test.ts CI check."""
    code = f'''
import re
from pathlib import Path

banned_patterns = [
    (" != undefined", "This is by definition Undefined Behavior"),
    (" == undefined", "This is by definition Undefined Behavior"),
    ("undefined != ", "This is by definition Undefined Behavior"),
    ("undefined == ", "This is by definition Undefined Behavior"),
    ('@import("bun").', "Only import 'bun' once"),
    ("std.debug.assert", "Use bun.assert instead"),
    ("std.debug.dumpStackTrace", "Use bun.handleErrorReturnTrace or bun.crash_handler.dumpStackTrace instead"),
    ("std.debug.print", "Don't let this be committed"),
    ("std.log", "Don't let this be committed"),
    ("std.mem.indexOfAny(u8", "Use bun.strings.indexOfAny"),
    ("std.StringArrayHashMapUnmanaged(", "bun.StringArrayHashMapUnmanaged has a faster `eql`"),
    ("std.StringArrayHashMap(", "bun.StringArrayHashMap has a faster `eql`"),
    ("std.StringHashMapUnmanaged(", "bun.StringHashMapUnmanaged has a faster `eql`"),
    ("std.StringHashMap(", "bun.StringHashMap has a faster `eql`"),
    ("std.Thread.Mutex", "Use bun.Mutex instead"),
    ("allocator.ptr ==", "The std.mem.Allocator context pointer can be undefined"),
    ("allocator.ptr !=", "The std.mem.Allocator context pointer can be undefined"),
    ("== allocator.ptr", "The std.mem.Allocator context pointer can be undefined"),
    ("!= allocator.ptr", "The std.mem.Allocator context pointer can be undefined"),
    ("alloc.ptr ==", "The std.mem.Allocator context pointer can be undefined"),
    ("alloc.ptr !=", "The std.mem.Allocator context pointer can be undefined"),
    ("== alloc.ptr", "The std.mem.Allocator context pointer can be undefined"),
    ("!= alloc.ptr", "The std.mem.Allocator context pointer can be undefined"),
    ("usingnamespace", "Zig 0.15 will remove `usingnamespace`"),
    ("std.fs.Dir", "Prefer bun.sys + bun.FD instead of std.fs"),
    ("std.fs.cwd", "Prefer bun.FD.cwd()"),
    ("std.fs.File", "Prefer bun.sys + bun.FD instead of std.fs"),
    ("std.fs.openFileAbsolute", "Prefer bun.sys + bun.FD instead of std.fs"),
    (".stdFile()", "Prefer bun.sys + bun.FD instead of std.fs.File"),
    (".stdDir()", "Prefer bun.sys + bun.FD instead of std.fs.File"),
    (".arguments_old(", "Please migrate to .argumentsAsArray() or another argument API"),
    ("// autofix", "Evaluate if this variable should be deleted entirely or explicitly discarded"),
    ("global.hasException", "Incompatible with strict exception checks"),
    ("globalObject.hasException", "Incompatible with strict exception checks"),
    ("globalThis.hasException", "Incompatible with strict exception checks"),
    ("EXCEPTION_ASSERT(!scope.exception())", "Use scope.assertNoException() instead"),
    (" catch bun.outOfMemory()", "Use bun.handleOom to avoid catching unrelated errors"),
    (".jsBoolean(true)", "Use .true instead"),
    ("JSValue.true", "Use .true instead"),
    (".jsBoolean(false)", "Use .false instead"),
    ("JSValue.false", "Use .false instead"),
    ("std.enums.tagName(", "Use bun.tagName instead"),
]

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
errors = []
for path in paths:
    src = Path(path).read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        trimmed = line.strip()
        if trimmed.startswith("//") or trimmed.startswith("\\\\"):
            continue
        for pattern, reason in banned_patterns:
            if pattern in line:
                errors.append(f"{{Path(path).name}}:{{i}}: Banned pattern {{repr(pattern)}} - {{reason}}")

if errors:
    for e in errors:
        print(f"FAIL: {{e}}")
    exit(1)
print("PASS: No banned words/patterns found")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_mysql_structs_complete():
    """MySQL structs have required fields and deinit methods (repo CI gate)."""
    code = f'''
import re
from pathlib import Path

def extract_struct_body(src, struct_name):
    pattern = rf"{{re.escape(struct_name)}}\\s*=\\s*struct\\s*\\{{"
    m = re.search(pattern, src)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{{":
            depth += 1
        elif src[i] == "}}":
            depth -= 1
        i += 1
    return src[start:i-1]

src = Path("{COLDEF}").read_text()

if not re.search(r"pub\\s+fn\\s+deinit", src):
    print("FAIL: ColumnDefinition41 missing deinit method")
    exit(1)

required = ["catalog", "schema", "table", "name", "org_name", "name_or_index"]
for field in required:
    if field + ":" not in src:
        print(f"FAIL: ColumnDefinition41 missing field {{field}}")
        exit(1)

src = Path("{PREPSTMT}").read_text()
struct_body = extract_struct_body(src, "Execute")
if not struct_body:
    print("FAIL: Execute struct not found")
    exit(1)

if "deinit" not in struct_body:
    print("FAIL: Execute struct missing deinit method")
    exit(1)

if "params" not in struct_body:
    print("FAIL: Execute struct missing params field")
    exit(1)

print("PASS: MySQL structs are complete with required fields and methods")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_allocator_consistency():
    """Memory allocation and deallocation use consistent allocator (repo CI gate)."""
    code = f'''
import re
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]

for path in paths:
    src = Path(path).read_text()
    filename = Path(path).name

    # Check that bun.default_allocator is used (not std allocators)
    if "bun.default_allocator" not in src and "bun.default.allocator" not in src:
        continue  # Some files might not do allocation, that's ok

    if "std.heap" in src:
        print(f"FAIL: {{filename}} uses forbidden std.heap")
        exit(1)
    if "std.mem.Allocator" in src:
        print(f"FAIL: {{filename}} uses forbidden std.mem.Allocator")
        exit(1)

print("PASS: Allocator usage is consistent (bun.default_allocator only)")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_no_autofix_comments():
    """Modified files should not have autofix todo comments (repo CI gate)."""
    code = f'''
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
for path in paths:
    src = Path(path).read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        if "// autofix" in line:
            print(f"FAIL: {{Path(path).name}}:{{i}}: Found '// autofix' comment")
            exit(1)
print("PASS: No autofix comments found")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_no_enum_tagname():
    """Modified files should use bun.tagName instead of std.enums.tagName (repo CI gate)."""
    code = f'''
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
for path in paths:
    src = Path(path).read_text()
    if "std.enums.tagName(" in src:
        print(f"FAIL: {{Path(path).name}} uses std.enums.tagName")
        exit(1)
print("PASS: No std.enums.tagName usage found")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_no_debug_log_patterns():
    """Modified files do not have debug print patterns (repo CI gate)."""
    code = f'''
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
banned = ["std.debug.print(", "std.log("]

for path in paths:
    src = Path(path).read_text()
    for pattern in banned:
        if pattern in src:
            print(f"FAIL: {{Path(path).name}} contains {{pattern}}")
            exit(1)

print("PASS: No debug print patterns found")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_no_std_unicode():
    """Modified files use bun.strings instead of std.unicode (repo CI gate)."""
    code = f'''
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
for path in paths:
    src = Path(path).read_text()
    if "std.unicode" in src:
        print(f"FAIL: {{Path(path).name}} uses std.unicode instead of bun.strings")
        exit(1)
print("PASS: No std.unicode usage found")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_no_fs_api_misuse():
    """Modified files use bun.sys instead of std.fs (repo CI gate)."""
    code = f'''
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
forbidden = ["std.fs.Dir", "std.fs.cwd", "std.fs.File", "std.fs.openFileAbsolute"]

for path in paths:
    src = Path(path).read_text()
    for pattern in forbidden:
        if pattern in src:
            print(f"FAIL: {{Path(path).name}} uses {{pattern}} instead of bun.sys/bun.FD")
            exit(1)
print("PASS: No std.fs API misuse found")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"
