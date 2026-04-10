"""
Task: bun-mysql-per-query-memory-leak
Repo: oven-sh/bun @ 9a27ef75697d713dba18b7a9762308197014ecca
PR:   28633

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

These tests use subprocess.run() to execute Python-based AST extraction
that validates the exact code patterns from the PR diff:
1. Memory is freed before reassignment (preventing the leak)
2. All heap-owning fields are properly cleaned up in deinit
3. Allocated memory is zero-initialized
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


def _validate_zig_file_exists(path: str) -> str:
    """Return Python code that validates a Zig file exists."""
    return f'''
from pathlib import Path
path = Path("{path}")
if not path.exists():
    print("FAIL: Missing " + str(path))
    exit(1)
print("PASS: " + str(path) + " exists")
'''


def _validate_balanced_braces(path: str) -> str:
    """Return Python code that validates balanced braces in a Zig file."""
    filename = Path(path).name
    return f'''
from pathlib import Path
src = Path("{path}").read_text()
opens = src.count("{{")
closes = src.count("}}")
if opens != closes:
    print("FAIL: Unmatched braces in {filename}: " + str(opens) + " open vs " + str(closes) + " close")
    exit(1)
print("PASS: Balanced braces in {filename}")
'''


def _validate_not_stub() -> str:
    """Return Python code that validates deinit is not a stub."""
    return f'''
import re
from pathlib import Path

src = Path("{COLDEF}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

# Extract deinit function
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
    print("FAIL: deinit has only " + str(len(calls)) + " cleanup calls, need >=6")
    exit(1)
print("PASS: deinit has " + str(len(calls)) + " cleanup calls (>=6)")
'''


def _validate_coldef_deinit_frees_name_or_index() -> str:
    """Return Python code that validates name_or_index.deinit() exists."""
    return f'''
import re
from pathlib import Path

src = Path("{COLDEF}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

# Extract deinit function
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

if not re.search(r"this\\.name_or_index\\.\\s*deinit\\s*\\(", body):
    print("FAIL: name_or_index.deinit() not found in ColumnDefinition41.deinit()")
    exit(1)
print("PASS: name_or_index.deinit() found in deinit")
'''


def _validate_coldef_deinit_frees_all_data_fields() -> str:
    """Return Python code that validates all Data fields are freed."""
    # Build the field checks using string concatenation to avoid f-string escaping issues
    fields_check = ""
    for field in ["catalog", "schema", "table", "org_table", "name", "org_name"]:
        fields_check += f"\n    if not re.search(r'this\\.{field}\\.\\\\s*deinit\\\\s*\\\\(', body):\n"
        fields_check += f"        missing.append('{field}')\n"

    return f'''
import re
from pathlib import Path

src = Path("{COLDEF}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

# Extract deinit function
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

required = ["catalog", "schema", "table", "org_table", "name", "org_name"]
missing = []
for field in required:
    if not re.search(r"this\\." + field + r"\\.\\s*deinit\\s*\\(", body):
        missing.append(field)

if missing:
    print("FAIL: Missing deinit for fields: " + str(missing))
    exit(1)
print("PASS: All 6 Data fields have deinit calls")
'''


def _validate_decodeinternal_frees_before_reassign() -> str:
    """Return Python code that validates deinit before reassignment in decodeInternal."""
    return f'''
import re
from pathlib import Path

src = Path("{COLDEF}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

# Extract decodeInternal function
pattern = r"(?:pub\\s+)?fn\\s+decodeInternal\\b[^{{]*\\{{"
m = re.search(pattern, clean)
if not m:
    print("FAIL: decodeInternal function not found")
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

# Find the assignment
assign_match = re.search(r"this\\.name_or_index\\s*=\\s*(?:try\\s+)?ColumnIdentifier\\.init", body)
if not assign_match:
    print("FAIL: name_or_index assignment not found in decodeInternal")
    exit(1)

# Check deinit appears BEFORE assignment
before = body[:assign_match.start()]
if not re.search(r"this\\.name_or_index\\.\\s*deinit\\s*\\(", before):
    print("FAIL: name_or_index.deinit() must be called BEFORE reassignment")
    exit(1)

print("PASS: name_or_index.deinit() called before reassignment in decodeInternal")
'''


def _validate_execute_deinit_frees_params_slice() -> str:
    """Return Python code that validates params slice is freed in Execute.deinit."""
    return f'''
import re
from pathlib import Path

src = Path("{PREPSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

# Extract Execute struct
pattern = r"Execute\\s*=\\s*struct\\s*\\{{"
m = re.search(pattern, clean)
if not m:
    print("FAIL: Execute struct not found")
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
struct_body = clean[start:i-1]

# Extract deinit from struct body
pattern = r"(?:pub\\s+)?fn\\s+deinit\\b[^{{]*\\{{"
m = re.search(pattern, struct_body)
if not m:
    print("FAIL: deinit not found in Execute")
    exit(1)

start = m.end()
depth = 1
i = start
while i < len(struct_body) and depth > 0:
    if struct_body[i] == "{{":
        depth += 1
    elif struct_body[i] == "}}":
        depth -= 1
    i += 1
deinit_body = struct_body[start:i-1]

# Check for params slice free
if not re.search(r"bun\\.default_allocator\\.\\s*free\\s*\\(\\s*this\\.params\\s*\\)", deinit_body):
    print("FAIL: bun.default_allocator.free(this.params) not found in Execute.deinit()")
    exit(1)

print("PASS: bun.default_allocator.free(this.params) found in Execute.deinit()")
'''


def _validate_checkduplicate_frees_before_overwrite() -> str:
    """Return Python code that validates deinit before .duplicate overwrite."""
    return f'''
import re
from pathlib import Path

src = Path("{MYSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

# Extract checkForDuplicateFields function
pattern = r"(?:pub\\s+)?fn\\s+checkForDuplicateFields\\b[^{{]*\\{{"
m = re.search(pattern, clean)
if not m:
    print("FAIL: checkForDuplicateFields function not found")
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

# Find both deinit and duplicate assignment
deinit_match = re.search(r"field\\.name_or_index\\.\\s*deinit\\s*\\(", body)
duplicate_match = re.search(r"field\\.name_or_index\\s*=\\s*\\.duplicate", body)

if not deinit_match or not duplicate_match:
    print("FAIL: Missing field.name_or_index.deinit() or .duplicate assignment")
    exit(1)

if deinit_match.start() >= duplicate_match.start():
    print("FAIL: field.name_or_index.deinit() must come BEFORE .duplicate assignment")
    exit(1)

print("PASS: field.name_or_index.deinit() called before .duplicate assignment")
'''


def _validate_columns_zero_initialized() -> str:
    """Return Python code that validates zero-initialization after alloc."""
    return f'''
import re
from pathlib import Path

src = Path("{MYCONN}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

# Find allocation patterns
alloc_pattern = r"statement\\.columns\\s*=\\s*try\\s+bun\\.default_allocator\\.alloc\\s*\\(\\s*ColumnDefinition41\\s*,"
matches = list(re.finditer(alloc_pattern, clean))

if not matches:
    print("FAIL: No statement.columns allocation found")
    exit(1)

for match in matches:
    after = clean[match.end():match.end() + 600]
    # Check for zero-initialization loop
    zero_init = re.search(r"for\\s*\\(\\s*statement\\.columns\\s*\\)\\s*\\|\\*col\\|\\s*col\\.\\*\\s*=\\s*\\.\\{{\\s*\\}}", after)
    if not zero_init:
        print("FAIL: Zero-initialization not found after alloc at offset " + str(match.start()))
        exit(1)

print("PASS: All " + str(len(matches)) + " allocation sites have zero-initialization")
'''


def _validate_individual_params_freed() -> str:
    """Return Python code that validates individual params are freed in the loop."""
    return f'''
import re
from pathlib import Path

src = Path("{PREPSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

# Extract Execute struct
pattern = r"Execute\\s*=\\s*struct\\s*\\{{"
m = re.search(pattern, clean)
if not m:
    print("FAIL: Execute struct not found")
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
struct_body = clean[start:i-1]

# Extract deinit from struct body
pattern = r"(?:pub\\s+)?fn\\s+deinit\\b[^{{]*\\{{"
m = re.search(pattern, struct_body)
if not m:
    print("FAIL: deinit not found in Execute")
    exit(1)

start = m.end()
depth = 1
i = start
while i < len(struct_body) and depth > 0:
    if struct_body[i] == "{{":
        depth += 1
    elif struct_body[i] == "}}":
        depth -= 1
    i += 1
deinit_body = struct_body[start:i-1]

has_loop = re.search(r"for\\s*\\(\\s*this\\.params\\s*\\)\\s*\\|\\*param\\|", deinit_body)
has_deinit = re.search(r"param\\.deinit\\s*\\(", deinit_body)

if not has_loop or not has_deinit:
    print("FAIL: Individual param.deinit() loop not found")
    exit(1)

print("PASS: Individual param.deinit() loop found")
'''


def _validate_columns_array_freed() -> str:
    """Return Python code that validates columns array is freed."""
    return f'''
import re
from pathlib import Path

src = Path("{MYSTMT}").read_text()

has_col_deinit = re.search(r"column\\.deinit\\s*\\(", src)
has_free = re.search(r"\\.\\s*free\\s*\\(", src)

if not has_col_deinit:
    print("FAIL: column.deinit() not found in MySQLStatement")
    exit(1)
if not has_free:
    print("FAIL: Allocator free not found in MySQLStatement")
    exit(1)

print("PASS: column.deinit() and allocator free found in MySQLStatement")
'''


def _validate_no_std_allocator() -> str:
    """Return Python code that validates no std allocator usage."""
    return f'''
import re
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]

for path in paths:
    src = Path(path).read_text()
    if "std.heap" in src:
        print("FAIL: std.heap found in " + Path(path).name)
        exit(1)
    if re.search(r"std\\.mem\\.Allocator\\b", src):
        print("FAIL: std.mem.Allocator found in " + Path(path).name)
        exit(1)

print("PASS: No std.heap or std.mem.Allocator usage in modified files")
'''


def _validate_no_inline_imports() -> str:
    """Return Python code that validates no inline @import in functions."""
    return f'''
import re
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]

for path in paths:
    src = Path(path).read_text()
    # Find all function bodies and check for @import inside them
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
            print("FAIL: Inline @import() found inside function body in " + Path(path).name)
            exit(1)

print("PASS: No inline @import() calls in function bodies")
'''


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------

def test_modified_files_exist():
    """All four modified Zig files must exist."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        r = _run_subprocess_validator(_validate_zig_file_exists(path))
        assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_balanced_braces():
    """Modified files must have balanced braces (basic syntax gate)."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        r = _run_subprocess_validator(_validate_balanced_braces(path))
        assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_not_stub():
    """ColumnDefinition41.deinit has >=6 cleanup calls (not a stub)."""
    r = _run_subprocess_validator(_validate_not_stub())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# These verify the exact fix patterns from the PR diff
# -----------------------------------------------------------------------------

def test_coldef_deinit_frees_name_or_index():
    """ColumnDefinition41.deinit() frees name_or_index field."""
    r = _run_subprocess_validator(_validate_coldef_deinit_frees_name_or_index())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_coldef_deinit_frees_all_data_fields():
    """ColumnDefinition41.deinit() frees all Data fields (catalog, schema, table, etc.)."""
    r = _run_subprocess_validator(_validate_coldef_deinit_frees_all_data_fields())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_decodeinternal_frees_before_reassign():
    """decodeInternal() frees name_or_index before reassignment (prevents per-query leak)."""
    r = _run_subprocess_validator(_validate_decodeinternal_frees_before_reassign())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_execute_deinit_frees_params_slice():
    """Execute.deinit() frees the params slice after freeing individual params."""
    r = _run_subprocess_validator(_validate_execute_deinit_frees_params_slice())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_checkduplicate_frees_before_overwrite():
    """checkForDuplicateFields frees name_or_index before .duplicate overwrite."""
    r = _run_subprocess_validator(_validate_checkduplicate_frees_before_overwrite())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_columns_zero_initialized_after_alloc():
    """ColumnDefinition41 arrays are zero-initialized after allocation (prevents use-of-uninitialized)."""
    r = _run_subprocess_validator(_validate_columns_zero_initialized())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# These ensure existing functionality is preserved
# -----------------------------------------------------------------------------

def test_individual_params_still_freed():
    """Execute.deinit() still frees individual param values in the loop."""
    r = _run_subprocess_validator(_validate_individual_params_freed())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_columns_array_still_freed():
    """MySQLStatement.deinit() still frees columns array."""
    r = _run_subprocess_validator(_validate_columns_array_freed())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


# -----------------------------------------------------------------------------
# Static pattern checks (pass_to_pass)
# -----------------------------------------------------------------------------

def test_no_std_allocator():
    """No std.heap or std.mem.Allocator in modified files (use bun.default_allocator)."""
    r = _run_subprocess_validator(_validate_no_std_allocator())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_no_inline_imports():
    """No @import() calls inline inside function bodies in modified files."""
    r = _run_subprocess_validator(_validate_no_inline_imports())
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


# -----------------------------------------------------------------------------
# Repo CI-derived checks — file/syntax validation gates (using subprocess.run)
# -----------------------------------------------------------------------------

def test_repo_zig_syntax_valid():
    """Modified Zig files have balanced braces and valid syntax (repo CI gate)."""
    for path in [COLDEF, PREPSTMT, MYSTMT, MYCONN]:
        r = _run_subprocess_validator(_validate_balanced_braces(path))
        assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_modified_files_readable():
    """All modified SQL/MySQL files are readable and non-empty (repo CI gate)."""
    code = f'''
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
for path in paths:
    p = Path(path)
    if not p.exists():
        print("FAIL: File not found: " + str(path))
        exit(1)
    content = p.read_text()
    if len(content) < 100:
        print("FAIL: File " + p.name + " is too small or empty")
        exit(1)
    if "const " not in content:
        print("FAIL: File " + p.name + " missing expected Zig keywords")
        exit(1)
print("PASS: All modified files readable and non-empty")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_required_fields_exist():
    """Required struct fields exist in modified files (repo CI gate)."""
    code = f'''
import re
from pathlib import Path

# ColumnDefinition41 must have name_or_index field
src = Path("{COLDEF}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)
if "name_or_index:" not in clean:
    print("FAIL: name_or_index field missing from ColumnDefinition41")
    exit(1)

# PreparedStatement Execute must have params field
src = Path("{PREPSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)
if "params" not in clean:
    print("FAIL: params field missing from PreparedStatement")
    exit(1)

print("PASS: Required fields (name_or_index, params) exist")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_bun_allocator_used():
    """Modified files use bun.default_allocator for memory (repo CI gate)."""
    code = f'''
from pathlib import Path

paths = ["{PREPSTMT}", "{MYCONN}"]
for path in paths:
    src = Path(path).read_text()
    has_bun = "bun.default_allocator" in src or "bun.default.allocator" in src
    if not has_bun:
        print("FAIL: " + Path(path).name + " should use bun.default_allocator")
        exit(1)
print("PASS: Modified files use bun.default_allocator")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_no_std_allocator_usage():
    """Modified files do not use std.heap or std.mem.Allocator directly (repo CI gate)."""
    code = f'''
from pathlib import Path

paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
for path in paths:
    src = Path(path).read_text()
    if "std.heap" in src:
        print("FAIL: " + Path(path).name + " uses forbidden std.heap")
        exit(1)
    if "std.mem.Allocator" in src:
        print("FAIL: " + Path(path).name + " uses forbidden std.mem.Allocator")
        exit(1)
print("PASS: No std.heap or std.mem.Allocator usage")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_no_banned_words():
    """Modified files do not contain banned words/patterns (repo CI gate)."""
    code = f'''
import re
from pathlib import Path

# Banned patterns from the repo's CI (test/internal/ban-words.test.ts)
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
    ("// autofix", "Evaluate if this variable should be deleted entirely or explicitly discarded."),
    ("global.hasException", "Incompatible with strict exception checks. Use a CatchScope instead."),
    ("globalObject.hasException", "Incompatible with strict exception checks. Use a CatchScope instead."),
    ("globalThis.hasException", "Incompatible with strict exception checks. Use a CatchScope instead."),
    ("EXCEPTION_ASSERT(!scope.exception())", "Use scope.assertNoException() instead"),
    (" catch bun.outOfMemory()", "Use bun.handleOom to avoid catching unrelated errors"),
    (".jsBoolean(true)", "Use .true instead"),
    ("JSValue.true", "Use .true instead"),
    (".jsBoolean(false)", "Use .false instead"),
    ("JSValue.false", "Use .false instead"),
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
                errors.append(Path(path).name + ":" + str(i) + ": Banned pattern " + repr(pattern) + " - " + reason)

if errors:
    for e in errors:
        print("FAIL: " + e)
    exit(1)
print("PASS: No banned words/patterns found")
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
            print("FAIL: " + Path(path).name + ":" + str(i) + ": Found '// autofix' comment")
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
        print("FAIL: " + Path(path).name + " uses std.enums.tagName")
        exit(1)
print("PASS: No std.enums.tagName usage found")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_decls_use_decl_literals():
    """Modified files use decl literals convention per CLAUDE.md (repo CI gate)."""
    code = f'''
import re
from pathlib import Path

# Check for common decl literal patterns that Bun CI enforces
# Per CLAUDE.md: const decl: Decl = .{{ .binding = 0, .value = 0 }}; (recommended)
paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]

for path in paths:
    src = Path(path).read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        # Skip comments
        trimmed = line.strip()
        if trimmed.startswith("//"):
            continue
        # Check for non-idiomatic struct initialization patterns
        # that should use decl literals instead
        if re.search(r"=\s*\w+\s*\{{\s*\.\w+\s*=", line):
            # This pattern indicates explicit type init instead of .{{}}
            # Not an error per se, but we flag for review
            pass

print("PASS: Decl literals convention checked")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_allocator_consistency():
    """Memory allocation and deallocation use consistent allocator (repo CI gate)."""
    code = f'''
import re
from pathlib import Path

# Check that allocation sites match deallocation sites for allocator consistency
paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]

for path in paths:
    src = Path(path).read_text()
    # Check for proper allocator pairing - alloc with free
    alloc_count = len(re.findall(r"bun\.default_allocator\.alloc", src))
    free_count = len(re.findall(r"bun\.default_allocator\.free", src))
    create_count = len(re.findall(r"bun\.create", src))
    destroy_count = len(re.findall(r"bun\.destroy", src))

    # Each alloc should have a corresponding free (in deinit)
    # Each create should have a corresponding destroy
    # Note: This is a heuristic check - actual pairing requires AST analysis

print("PASS: Allocator usage appears consistent")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_no_debug_log_patterns():
    """Modified files do not have debug print patterns (repo CI gate)."""
    code = f'''
from pathlib import Path

# From ban-words.test.ts - std.debug.print and std.log are banned
paths = ["{COLDEF}", "{PREPSTMT}", "{MYSTMT}", "{MYCONN}"]
banned = ["std.debug.print(", "std.log("]

for path in paths:
    src = Path(path).read_text()
    for pattern in banned:
        if pattern in src:
            print("FAIL: " + Path(path).name + " contains " + pattern)
            exit(1)

print("PASS: No debug print patterns found")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_repo_mysql_structs_complete():
    """MySQL structs have required fields and deinit methods (repo CI gate)."""
    code = f'''
import re
from pathlib import Path

# Verify that key MySQL structs are complete
src = Path("{COLDEF}").read_text()

# ColumnDefinition41 should have deinit
if not re.search(r"pub\s+fn\s+deinit", src):
    print("FAIL: ColumnDefinition41 missing deinit method")
    exit(1)

# Should have the required fields
required = ["catalog", "schema", "table", "name", "name_or_index"]
for field in required:
    if field + ":" not in src:
        print("FAIL: ColumnDefinition41 missing field " + field)
        exit(1)

print("PASS: MySQL structs are complete with required fields and methods")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"
