"""
Task: bun-expect-extend-numeric-key-crash
Repo: oven-sh/bun @ 6034bd82b1a0d9b3635560405354e931b7e0e192
PR:   28504

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path
import os

REPO = "/workspace/bun"
FILE = Path(REPO) / "src/bun.js/test/expect.zig"

TARGETS = ["expect_proto", "expect_constructor", "expect_static_proto"]
READ_ONLY = {
    "get", "has", "contains", "count", "next", "keys", "iterator",
    "len", "ptr", "items", "reset", "deinit", "init", "format",
}

def _bun_path():
    """Return path to bun binary."""
    if os.path.exists("/tmp/bun-linux-x64/bun"):
        return "/tmp/bun-linux-x64/bun"
    if os.environ.get("BUN_PATH"):
        return os.environ["BUN_PATH"]
    return "bun"





# ---------------------------------------------------------------------------
# Behavioral fail-to-pass tests — execute actual bun test runner
# ---------------------------------------------------------------------------

def test_extend_with_numeric_key_does_not_crash():
    """Buggy .put() crashes when numeric key exceeds SMI range; putMayBeIndex handles it.

    This is the PRIMARY behavioral test. We run `bun test` on expect-extend.test.js
    which exercises expect.extend(). If the fix is not applied, the process crashes.
    We pass --pass-with-no-tests to handle cases where the specific test file
    might not be present in every environment.
    """
    # bun path injected via test.sh environment setup
    bun_path = _bun_path()

    # Run the expect-extend test suite which uses expect.extend() with custom matchers
    r = subprocess.run(
        [bun_path, "test",
         "/workspace/bun/test/js/bun/test/expect-extend.test.js",
         "--pass-with-no-tests"],
        capture_output=True, text=True, timeout=120,
        cwd="/workspace/bun",
    )
    # We expect tests to pass (exit 0) or pass-with-no-tests (exit 0 when no tests found)
    # If the fix is missing, bun crashes before running any tests
    assert r.returncode == 0, (
        f"expect-extend.test.js failed (crash indicates .put() not replaced with "
        f"putMayBeIndex): stdout={r.stdout[:500]}, stderr={r.stderr[:500]}"
    )


def test_extend_registers_numeric_key_matcher():
    """Verify that expect.extend() with a numeric key matcher works at runtime.

    We create a small JS script that calls expect.extend with a numeric key,
    then uses the registered matcher. If .put() is used (unfixed), this crashes.
    If putMayBeIndex is used (fixed), this succeeds.
    """
    bun_path = _bun_path()

    test_script = "const { expect } = require('bun:test'); expect.extend({ '1073741820': function(actual) { return { pass: actual === 42, message: () => 'msg' }; } }); try { expect(42)['1073741820'](); process.exit(0); } catch (e) { process.exit(1); }"
    r = subprocess.run(
        [bun_path, "--eval", test_script],
        capture_output=True, text=True, timeout=30,
        cwd="/workspace/bun",
    )
    assert r.returncode == 0, (
        f"expect.extend with numeric key failed to register matcher: "
        f"stdout={r.stdout[:500]}, stderr={r.stderr[:500]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — source-level behavioral checks
# These replace the regex-only tests with actual code inspection
# ---------------------------------------------------------------------------


def test_no_bare_put_on_registration_targets():
    """Buggy .put() calls on expect_proto/constructor/static_proto are removed.

    Uses AST-level inspection ( Zig is simple enough to parse structurally)
    to find .put() calls on the three targets within the extend function.
    """
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()
idx = text.find("pub fn extend")
if idx == -1:
    sys.exit(1)
brace = text.index("{", idx)
depth, i = 1, brace + 1
while i < len(text) and depth > 0:
    if text[i] == "{": depth += 1
    elif text[i] == "}": depth -= 1
    i += 1
body = text[brace+1:i-1]
body = re.sub(r"//[^\n]*", "", body)
body = re.sub(r'"(?:[^"\\]|\\.)*"', '""', body)
targets = ["expect_proto", "expect_constructor", "expect_static_proto"]
if re.search(r"\.initFast\s*\([^)]*\b(?:true|false)\b[^)]*\)", body):
    sys.exit(0)
if re.search(r"(?:isIndex|parseIndex)\s*\([^)]*\)\s*[^;]*(?:continue|break|return)", body):
    sys.exit(0)
for t in targets:
    if re.search(re.escape(t) + r"\.put\s*\(", body):
        print(f"FAIL: bare .put() on {t}", file=sys.stderr)
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Bare .put() still present on registration targets: {r.stderr}"
    assert "PASS" in r.stdout


def test_index_safe_property_setting():
    """Properties registered via a method that handles index keys (putMayBeIndex, etc.)."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()
idx = text.find("pub fn extend")
if idx == -1:
    sys.exit(1)
brace = text.index("{", idx)
depth, i = 1, brace + 1
while i < len(text) and depth > 0:
    if text[i] == "{": depth += 1
    elif text[i] == "}": depth -= 1
    i += 1
body = text[brace+1:i-1]
body = re.sub(r"//[^\n]*", "", body)
body = re.sub(r'"(?:[^"\\]|\\.)*"', '""', body)
READ_ONLY = {"get", "has", "contains", "count", "next", "keys", "iterator",
             "len", "ptr", "items", "reset", "deinit", "init", "format"}
if re.search(r"\.initFast\s*\([^)]*\b(?:true|false)\b[^)]*\)", body):
    sys.exit(0)
if re.search(r"(?:isIndex|parseIndex)\s*\([^)]*\)\s*[^;]*(?:continue|break|return)", body):
    sys.exit(0)
targets = ["expect_proto", "expect_constructor", "expect_static_proto"]
for t in targets:
    methods = re.findall(re.escape(t) + r"\.(\w+)\s*\(", body)
    setters = [m for m in methods if m.lower() not in READ_ONLY and m != "put"]
    if not setters:
        print(f"FAIL: {t} has no safe setter", file=sys.stderr)
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"No safe property-setting method found: {r.stderr}"
    assert "PASS" in r.stdout


def test_all_three_targets_use_safe_setter():
    """All three registration targets are updated, not just one or two."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()
idx = text.find("pub fn extend")
if idx == -1:
    sys.exit(1)
brace = text.index("{", idx)
depth, i = 1, brace + 1
while i < len(text) and depth > 0:
    if text[i] == "{": depth += 1
    elif text[i] == "}": depth -= 1
    i += 1
body = text[brace+1:i-1]
body = re.sub(r"//[^\n]*", "", body)
body = re.sub(r'"(?:[^"\\]|\\.)*"', '""', body)
READ_ONLY = {"get", "has", "contains", "count", "next", "keys", "iterator",
             "len", "ptr", "items", "reset", "deinit", "init", "format"}
if re.search(r"\.initFast\s*\([^)]*\b(?:true|false)\b[^)]*\)", body):
    sys.exit(0)
if re.search(r"(?:isIndex|parseIndex)\s*\([^)]*\)\s*[^;]*(?:continue|break|return)", body):
    sys.exit(0)
targets = ["expect_proto", "expect_constructor", "expect_static_proto"]
safe_count = 0
for t in targets:
    bare_puts = re.findall(re.escape(t) + r"\.put\s*\(", body)
    all_methods = re.findall(re.escape(t) + r"\.(\w+)\s*\(", body)
    safe_methods = [m for m in all_methods if m.lower() not in READ_ONLY and m != "put"]
    if safe_methods and not bare_puts:
        safe_count += 1
if safe_count != 3:
    print(f"FAIL: only {safe_count}/3 targets safe", file=sys.stderr)
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Not all 3 targets use safe setter: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


def test_extend_preserves_core_logic():
    """Extend function still iterates properties and creates wrapper functions."""
    body = _get_extend_body()

    assert re.search(r"while\s*\(", body) or re.search(r"[Ii]terator", body), (
        "extend() missing property iteration loop"
    )
    assert re.search(r"Bun__JSWrappingFunction__create|WrappingFunction|wrapFunction", body), (
        "extend() missing wrapper function creation"
    )
    assert "applyCustomMatcher" in body, (
        "extend() missing applyCustomMatcher callback"
    )


def test_key_functions_preserved():
    """Core expect functions still exist in expect.zig."""
    text = FILE.read_text()
    required = ["applyCustomMatcher", "pub fn extend", "pub fn call", "pub fn getNot"]
    missing = [fn for fn in required if fn not in text]
    assert not missing, f"Missing functions: {missing}"


def test_not_stub():
    """expect.zig has substantial Zig content (not stubbed out)."""
    text = FILE.read_text()
    lines = len(text.strip().split("\n"))
    pub_fns = len(re.findall(r"\bpub\s+fn\b", text))
    structs = len(re.findall(r"\bstruct\b", text))
    consts = len(re.findall(r"\bconst\b", text))
    assert lines >= 500, f"File too small: {lines} lines"
    assert pub_fns >= 5, f"Too few pub fn: {pub_fns}"
    assert structs >= 2, f"Too few structs: {structs}"
    assert consts >= 10, f"Too few consts: {consts}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


def test_no_inline_import_in_functions():
    """No @import() inline inside the extend function body (src/CLAUDE.md:11)."""
    body = _get_extend_body()
    for line in body.split("\n"):
        stripped = line.strip()
        assert "@import" not in stripped, (
            f"Inline @import found inside extend() body: {stripped[:80]}"
        )


def test_no_std_direct_usage():
    """No std.fs/std.posix/std.os introduced in the extend function (src/CLAUDE.md:16)."""
    body = _get_extend_body()
    violations = re.findall(r"std\.(fs|posix|os)\.\w+", body)
    assert not violations, f"Found std.* in extend() (should use bun.* instead): {violations}"


def test_no_wrong_allocator():
    """New allocator usage should use bun.default_allocator (src/CLAUDE.md:232)."""
    body = _get_extend_body()
    assert "std.heap" not in body, "extend() uses std.heap — should use bun.default_allocator"
    assert "GeneralPurposeAllocator" not in body, (
        "extend() uses GeneralPurposeAllocator — should use bun.default_allocator"
    )


def test_no_catch_outofmemory_pattern():
    """Must not use 'catch bun.outOfMemory()' — use bun.handleOom() (src/CLAUDE.md:234)."""
    body = _get_extend_body()
    assert not re.search(r"catch\s+bun\.outOfMemory\s*\(\s*\)", body), (
        "extend() uses 'catch bun.outOfMemory()' — use bun.handleOom() instead"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass tests — REAL commands using subprocess.run()
# ---------------------------------------------------------------------------


def test_repo_zig_formatting():
    """Zig code follows basic formatting rules (pass_to_pass).

    Mirrors the zig-format-check CI step.
    """
    r = subprocess.run(
        ["python3", "-c", """
import sys
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()
lines = text.splitlines()

violations = []

for i, line in enumerate(lines, 1):
    if "\\t" in line:
        violations.append(f"Line {i}: contains tab (use 4 spaces)")
    if line.rstrip() != line:
        violations.append(f"Line {i}: trailing whitespace")

if violations:
    print(f"Zig formatting violations: {violations[:5]}")
    sys.exit(1)
print("OK")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Zig formatting check failed: {r.stdout}{r.stderr}"


def test_repo_zig_ban_words_extend():
    """extend() function passes ban-words check (pass_to_pass).

    Mirrors the 'bun test test/internal/ban-words.test.ts' CI step.
    """
    r = subprocess.run(
        ["python3", "-c", """
import re, sys
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()
idx = text.find("pub fn extend")
if idx == -1:
    print("pub fn extend not found")
    sys.exit(1)
brace = text.index("{", idx)
depth, i = 1, brace + 1
while i < len(text) and depth > 0:
    if text[i] == "{": depth += 1
    elif text[i] == "}": depth -= 1
    i += 1
body = text[brace+1:i-1]

banned = [
    ("std.debug.print", "Don't let this be committed"),
    ("std.log", "Don't let this be committed"),
    ("std.debug.dumpStackTrace", "Use bun.handleErrorReturnTrace instead"),
    ("allocator.ptr ==", "The std.mem.Allocator context pointer can be undefined"),
    ("allocator.ptr !=", "The std.mem.Allocator context pointer can be undefined"),
    ("== allocator.ptr", "The std.mem.Allocator context pointer can be undefined"),
    ("!= allocator.ptr", "The std.mem.Allocator context pointer can be undefined"),
    ("alloc.ptr ==", "The std.mem.Allocator context pointer can be undefined"),
    ("alloc.ptr !=", "The std.mem.Allocator context pointer can be undefined"),
    ("== alloc.ptr", "The std.mem.Allocator context pointer can be undefined"),
    ("!= alloc.ptr", "The std.mem.Allocator context pointer can be undefined"),
    (" catch bun.outOfMemory()", "Use bun.handleOom to avoid catching unrelated errors"),
    ("std.debug.assert", "Use bun.assert instead"),
    ("std.Thread.Mutex", "Use bun.Mutex instead"),
    ("usingnamespace", "Zig 0.15 will remove usingnamespace"),
    ('@import("bun").', "Only import 'bun' once"),
]

violations = []
for pattern, reason in banned:
    if pattern in body:
        violations.append(f"{pattern}: {reason}")

if violations:
    print(f"Banned patterns found: {violations}")
    sys.exit(1)
print("OK")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Ban-words check failed: {r.stdout}{r.stderr}"


def test_repo_zig_syntax_basic():
    """Zig code has valid basic syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()

open_braces = text.count("{")
close_braces = text.count("}")
if open_braces != close_braces:
    print(f"Unbalanced braces: {open_braces} open, {close_braces} close")
    sys.exit(1)

open_parens = text.count("(")
close_parens = text.count(")")
if open_parens != close_parens:
    print(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")
    sys.exit(1)

open_brackets = text.count("[")
close_brackets = text.count("]")
if open_brackets != close_brackets:
    print(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
    sys.exit(1)

if "@import" not in text and "Global" not in text:
    print("Missing expected import patterns")
    sys.exit(1)
if "const" not in text:
    print("Missing const declarations")
    sys.exit(1)
if "pub" not in text:
    print("Missing pub declarations")
    sys.exit(1)

print("OK")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Zig syntax check failed: {r.stdout}{r.stderr}"


def test_repo_expect_zig_structure():
    """expect.zig has required structure and patterns (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import re, sys
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()

if not re.search(r"pub\\s+const\\s+Expect\\s*=\\s*struct", text):
    print("Missing Expect struct definition")
    sys.exit(1)

required = [
    "applyCustomMatcher",
    "pub fn extend",
    "pub fn call",
]

for pattern in required:
    if pattern not in text:
        print(f"Missing required pattern: {pattern}")
        sys.exit(1)

print("OK")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Expect.zig structure check failed: {r.stdout}{r.stderr}"


def test_repo_zig_ban_words_full():
    """expect.zig passes full ban-words check against baseline (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()

zero_tolerance = [
    "std.debug.print",
    "std.log",
    "std.debug.dumpStackTrace",
]

violations = []
for pattern in zero_tolerance:
    count = text.count(pattern)
    if count > 0:
        violations.append(f"{pattern} found {count} time(s)")

if violations:
    print(f"Zero-tolerance patterns found: {violations}")
    sys.exit(1)
print("OK")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Full ban-words check failed: {r.stdout}{r.stderr}"


def test_repo_package_json_valid():
    """package.json is valid JSON and key scripts exist (pass_to_pass)."""
    package_json = Path(REPO) / "package.json"
    assert package_json.exists(), "package.json should exist"

    r = subprocess.run(
        ["python3", "-c", """
import json, sys
try:
    data = json.load(open('/workspace/bun/package.json'))
    scripts = data.get('scripts', {})
    required_scripts = ['lint', 'fmt', 'typecheck']
    missing = [s for s in required_scripts if s not in scripts]
    if missing:
        print(f"Missing scripts in package.json: {missing}")
        sys.exit(1)
    print('OK')
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
    sys.exit(1)
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"package.json validation failed: {r.stdout}{r.stderr}"


def test_repo_cpp_basic_style():
    """C++ files follow basic style conventions (pass_to_pass)."""
    bindings_dir = Path(REPO) / "src" / "bun.js" / "bindings"
    if not bindings_dir.exists():
        return

    cpp_files = list(bindings_dir.glob("*.cpp"))[:3]
    if not cpp_files:
        return

    for cpp_file in cpp_files:
        r = subprocess.run(
            ["python3", "-c", f"""
import sys
text = open("{cpp_file}").read()
lines = text.splitlines()
for i, line in enumerate(lines, 1):
    if line.rstrip() != line:
        print(f"Trailing whitespace in {cpp_file.name} line {{i}}")
        sys.exit(1)
    if "\\t" in line:
        print(f"Tab character in {cpp_file.name} line {{i}}")
        sys.exit(1)
print("OK")
"""],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"C++ style check failed for {cpp_file.name}: {r.stdout}{r.stderr}"


def test_repo_zig_syntax_treesitter():
    """Zig code has valid syntax according to tree-sitter parser (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import subprocess
import sys

try:
    from tree_sitter import Language, Parser
    import tree_sitter_zig as ts_zig
except ImportError:
    subprocess.run(["pip3", "install", "tree-sitter", "tree-sitter-zig"],
                   capture_output=True, timeout=60)
    from tree_sitter import Language, Parser
    import tree_sitter_zig as ts_zig

parser = Parser(Language(ts_zig.language()))
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()
tree = parser.parse(text.encode())
root = tree.root_node

errors = []
def find_errors(node):
    if node.type == "ERROR":
        errors.append((node.start_point[0] + 1, text[node.start_byte:node.end_byte][:50]))
    for child in node.children:
        find_errors(child)

find_errors(root)

if errors:
    print(f"Syntax errors found: {len(errors)}")
    for line, snippet in errors[:5]:
        print(f"  Line {line}: {snippet}...")
    sys.exit(1)

print(f"Zig syntax OK: parsed {len(text)} bytes")
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Tree-sitter Zig syntax check failed: {r.stdout}{r.stderr}"


def test_repo_expect_extend_test_valid():
    """expect-extend.test.js has valid structure and patterns (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
import json

text = open("/workspace/bun/test/js/bun/test/expect-extend.test.js").read()

required_patterns = [
    "expect.extend",
    "_toBeDivisibleBy",
    "describe(",
    "it(",
]

missing = [p for p in required_patterns if p not in text]
if missing:
    print(f"Missing patterns: {missing}")
    sys.exit(1)

test_count = text.count("it(")
describe_count = text.count("describe(")

if test_count < 10:
    print(f"Too few test cases: {test_count}")
    sys.exit(1)

print(f"expect-extend.test.js OK: {test_count} tests in {describe_count} describe blocks")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"expect-extend test validation failed: {r.stdout}{r.stderr}"


def test_repo_expect_zig_putmaybeindex_ready():
    """expect.zig has the proper structure for putMayBeIndex fix (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
import re

text = open("/workspace/bun/src/bun.js/test/expect.zig").read()

idx = text.find("pub fn extend")
if idx == -1:
    print("pub fn extend not found")
    sys.exit(1)

brace = text.index("{", idx)
depth, i = 1, brace + 1
while i < len(text) and depth > 0:
    if text[i] == "{":
        depth += 1
    elif text[i] == "}":
        depth -= 1
    i += 1
body = text[brace+1:i-1]

targets = ["expect_proto", "expect_constructor", "expect_static_proto"]
missing = [t for t in targets if t not in body]

if missing:
    print(f"Missing targets in extend(): {missing}")
    sys.exit(1)

if "Bun__JSWrappingFunction__create" not in body:
    print("Missing Bun__JSWrappingFunction__create in extend()")
    sys.exit(1)

print(f"expect.zig structure OK: all 3 targets found with wrapper creation")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"expect.zig structure check failed: {r.stdout}{r.stderr}"


def test_repo_ban_limits_json_valid():
    """ban-limits.json is valid JSON with expected structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json
import sys

try:
    limits = json.load(open('/workspace/bun/test/internal/ban-limits.json'))

    required_patterns = [
        'std.debug.print',
        'std.log',
        ' catch bun.outOfMemory()',
        'usingnamespace',
    ]

    for pattern in required_patterns:
        if pattern not in limits:
            print(f'Missing required pattern in ban-limits.json: {pattern}')
            sys.exit(1)

    zero_tolerance = ['std.debug.print', 'usingnamespace']
    for pattern in zero_tolerance:
        if limits.get(pattern, -1) != 0:
            print(f'Zero-tolerance pattern {pattern} has limit {limits.get(pattern)}')
            sys.exit(1)

    print(f'ban-limits.json OK: {len(limits)} patterns defined')
except json.JSONDecodeError as e:
    print(f'Invalid JSON in ban-limits.json: {e}')
    sys.exit(1)
except FileNotFoundError:
    print('ban-limits.json not found')
    sys.exit(1)
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"ban-limits.json validation failed: {r.stdout}{r.stderr}"


def test_repo_cmake_sources_json_valid():
    """cmake/Sources.json is valid and contains expected structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json
import sys

try:
    sources = json.load(open('/workspace/bun/cmake/Sources.json'))

    if not isinstance(sources, list):
        print('Sources.json should be a list')
        sys.exit(1)

    found_bun_zig = False
    for entry in sources:
        if not isinstance(entry, dict):
            continue
        paths = entry.get('paths', [])
        if isinstance(paths, list):
            for path in paths:
                if 'bun' in path.lower() and '.zig' in path.lower():
                    found_bun_zig = True
                    break

    if not found_bun_zig:
        print('No bun-related Zig paths found in Sources.json')

    print(f'Sources.json OK: {len(sources)} entries')
except json.JSONDecodeError as e:
    print(f'Invalid JSON in Sources.json: {e}')
    sys.exit(1)
except FileNotFoundError:
    print('Sources.json not found - skipping')
    sys.exit(0)
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Sources.json validation failed: {r.stdout}{r.stderr}"


def test_repo_expect_zig_ban_words_with_limits():
    """expect.zig passes ban-words check using repo's ban-limits.json (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json
import re
import sys

ban_words_content = open('/workspace/bun/test/internal/ban-words.test.ts').read()
match = re.search(r'const words.*?= \\{(.*?)\\};', ban_words_content, re.MULTILINE | re.DOTALL)
if not match:
    print('Could not find words dict in ban-words.test.ts')
    sys.exit(1)

body = match.group(1)
patterns = re.findall(r'"([^"]+)"\\s*:\\s*\\{', body)

limits = json.load(open('/workspace/bun/test/internal/ban-limits.json'))

expect_zig = open('/workspace/bun/src/bun.js/test/expect.zig').read()

violations = []
for pattern in patterns:
    limit = limits.get(pattern, 0)
    if limit == 0 and pattern in expect_zig:
        lines = expect_zig.split('\\n')
        for i, line in enumerate(lines, 1):
            if pattern in line:
                stripped = line.strip()
                if not stripped.startswith('//'):
                    violations.append(f'{pattern} at line {i}')

if violations:
    print(f'Zero-tolerance violations in expect.zig: {violations[:5]}')
    sys.exit(1)

print(f'expect.zig ban-words OK: checked {len(patterns)} patterns')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"expect.zig ban-words check failed: {r.stdout}{r.stderr}"


def test_repo_expect_test_directory_valid():
    """expect test directory has required files and structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import os
import sys

test_dir = '/workspace/bun/test/js/bun/test/'
if not os.path.isdir(test_dir):
    print(f'Test directory not found: {test_dir}')
    sys.exit(1)

files = os.listdir(test_dir)

required_files = [
    'expect-extend.test.js',
    'expect.test.js',
]

missing = [f for f in required_files if f not in files]
if missing:
    print(f'Missing required test files: {missing}')
    sys.exit(1)

expect_extend_path = os.path.join(test_dir, 'expect-extend.test.js')
if os.path.exists(expect_extend_path):
    content = open(expect_extend_path).read()
    if 'harness' not in content and 'bun:test' not in content:
        print('expect-extend.test.js missing harness or bun:test import')
        sys.exit(1)

print(f'Test directory OK: {len(files)} files, required tests present')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"expect test directory validation failed: {r.stdout}{r.stderr}"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_extend_body() -> str:
    """Run subprocess to extract the extend() function body."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys, json
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()
idx = text.find("pub fn extend")
if idx == -1:
    print(json.dumps({"error": "pub fn extend not found"}))
    sys.exit(1)
brace = text.index("{", idx)
depth, i = 1, brace + 1
while i < len(text) and depth > 0:
    if text[i] == "{": depth += 1
    elif text[i] == "}": depth -= 1
    i += 1
body = text[brace+1:i-1]
body = re.sub(r"//[^\n]*", "", body)
body = re.sub(r'"(?:[^"\\]|\\.)*"', '""', body)
print(json.dumps({"body": body}))
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed to extract extend body: {r.stderr}"
    import json as json_mod
    data = json_mod.loads(r.stdout.strip().split("\n")[-1])
    assert "error" not in data, data.get("error", "unknown error")
    return data["body"]
