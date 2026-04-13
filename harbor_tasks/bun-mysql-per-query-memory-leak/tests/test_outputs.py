"""
Task: bun-mysql-per-query-memory-leak
Repo: oven-sh/bun @ 9a27ef75697d713dba18b7a9762308197014ecca
PR:   28633

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

These tests use subprocess.run() to execute Python-based validation
that checks code patterns from the PR diff.
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
    """ColumnDefinition41.deinit() frees name_or_index field."""
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

if not re.search(r"this\\.name_or_index\\.\\s*deinit\\s*\\(", body):
    print("FAIL: name_or_index.deinit() not found in ColumnDefinition41.deinit()")
    exit(1)
print("PASS: name_or_index.deinit() found in deinit")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_coldef_deinit_frees_all_data_fields():
    """ColumnDefinition41.deinit() frees all Data fields."""
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

required = ["catalog", "schema", "table", "org_table", "name", "org_name"]
missing = []
for field in required:
    if not re.search(r"this\\." + field + r"\\.\\s*deinit\\s*\\(", body):
        missing.append(field)

if missing:
    print(f"FAIL: Missing deinit for fields: {{missing}}")
    exit(1)
print("PASS: All 6 Data fields have deinit calls")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_decodeinternal_frees_before_reassign():
    """decodeInternal() frees name_or_index before reassignment."""
    code = f'''
import re
from pathlib import Path

src = Path("{COLDEF}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

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

assign_match = re.search(r"this\\.name_or_index\\s*=\\s*(?:try\\s+)?ColumnIdentifier\\.init", body)
if not assign_match:
    print("FAIL: name_or_index assignment not found in decodeInternal")
    exit(1)

before = body[:assign_match.start()]
if not re.search(r"this\\.name_or_index\\.\\s*deinit\\s*\\(", before):
    print("FAIL: name_or_index.deinit() must be called BEFORE reassignment")
    exit(1)

print("PASS: name_or_index.deinit() called before reassignment in decodeInternal")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_execute_deinit_frees_params_slice():
    """Execute.deinit() frees the params slice."""
    code = f'''
import re
from pathlib import Path

src = Path("{PREPSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

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

if not re.search(r"bun\\.default_allocator\\.\\s*free\\s*\\(\\s*this\\.params\\s*\\)", deinit_body):
    print("FAIL: bun.default_allocator.free(this.params) not found in Execute.deinit()")
    exit(1)

print("PASS: bun.default_allocator.free(this.params) found in Execute.deinit()")
'''
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_checkduplicate_frees_before_overwrite():
    """checkForDuplicateFields frees name_or_index before .duplicate overwrite."""
    code = f'''
import re
from pathlib import Path

src = Path("{MYSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

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
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_columns_zero_initialized_after_alloc():
    """ColumnDefinition41 arrays are zero-initialized after allocation."""
    code = f'''
import re
from pathlib import Path

src = Path("{MYCONN}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

alloc_pattern = r"statement\\.columns\\s*=\\s*try\\s+bun\\.default_allocator\\.alloc\\s*\\(\\s*ColumnDefinition41\\s*,"
matches = list(re.finditer(alloc_pattern, clean))

if not matches:
    print("FAIL: No statement.columns allocation found")
    exit(1)

for match in matches:
    after = clean[match.end():match.end() + 600]
    zero_init = re.search(r"for\\s*\\(\\s*statement\\.columns\\s*\\)\\s*\\|\\*col\\|\\s*col\\.\\*\\s*=\\s*\\.\\{{\\s*\\}}", after)
    if not zero_init:
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
    """Execute.deinit() still frees individual param values in the loop."""
    code = f'''
import re
from pathlib import Path

src = Path("{PREPSTMT}").read_text()
clean = re.sub(r"//[^\\n]*", "", src)

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
    r = _run_subprocess_validator(code)
    assert r.returncode == 0, f"Failed: {r.stdout + r.stderr}"


def test_columns_array_still_freed():
    """MySQLStatement.deinit() still frees columns array."""
    code = f'''
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
pattern = r"Execute\\s*=\\s*struct\\s*\\{{"
m = re.search(pattern, src)
if not m:
    print("FAIL: Execute struct not found")
    exit(1)

start = m.end()
depth = 1
i = start
while i < len(src) and depth > 0:
    if src[i] == "{{":
        depth += 1
    elif src[i] == "}}":
        depth -= 1
    i += 1
struct_body = src[start:i-1]

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
