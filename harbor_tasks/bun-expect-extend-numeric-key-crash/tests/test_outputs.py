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

REPO = "/workspace/bun"
FILE = Path(REPO) / "src/bun.js/test/expect.zig"

TARGETS = ["expect_proto", "expect_constructor", "expect_static_proto"]
READ_ONLY = {
    "get", "has", "contains", "count", "next", "keys", "iterator",
    "len", "ptr", "items", "reset", "deinit", "init", "format",
}


def _extract_extend_body_script() -> str:
    """Python script that extracts and prints the extend() body from expect.zig."""
    return r"""
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
# Strip single-line comments and string literals
body = re.sub(r"//[^\n]*", "", body)
body = re.sub(r'"(?:[^"\\]|\\.)*"', '""', body)
print(json.dumps({"body": body}))
"""


def _get_extend_body() -> str:
    """Run subprocess to extract the extend() function body."""
    r = subprocess.run(
        ["python3", "-c", _extract_extend_body_script()],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed to extract extend body: {r.stderr}"
    import json
    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert "error" not in data, data.get("error", "unknown error")
    return data["body"]


def _iterator_skips_indices(body: str) -> bool:
    """Check if the JSPropertyIterator is configured to skip index properties."""
    if re.search(r"\.initFast\s*\([^)]*\b(?:true|false)\b[^)]*\)", body):
        return True
    if re.search(
        r"(?:isIndex|parseIndex)\s*\([^)]*\)\s*[^;]*(?:continue|break|return)", body
    ):
        return True
    return False


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_no_bare_put_on_registration_targets():
    """Buggy .put() calls on expect_proto/constructor/static_proto are removed."""
    r = subprocess.run(
        ["python3", "-c", """
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
# Check for iterator-based index skipping as alternative fix
if re.search(r"\\.initFast\\s*\\([^)]*\\b(?:true|false)\\b[^)]*\\)", body):
    sys.exit(0)
if re.search(r"(?:isIndex|parseIndex)\\s*\\([^)]*\\)\\s*[^;]*(?:continue|break|return)", body):
    sys.exit(0)
for t in targets:
    if re.search(re.escape(t) + r"\\.put\\s*\\(", body):
        print(f"FAIL: bare .put() on {t}", file=sys.stderr)
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Bare .put() still present on registration targets: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_index_safe_property_setting():
    """Properties registered via a method that handles index keys (putMayBeIndex, etc.)."""
    r = subprocess.run(
        ["python3", "-c", """
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
# Check for iterator-based index skipping as alternative fix
if re.search(r"\\.initFast\\s*\\([^)]*\\b(?:true|false)\\b[^)]*\\)", body):
    sys.exit(0)
if re.search(r"(?:isIndex|parseIndex)\\s*\\([^)]*\\)\\s*[^;]*(?:continue|break|return)", body):
    sys.exit(0)
targets = ["expect_proto", "expect_constructor", "expect_static_proto"]
for t in targets:
    methods = re.findall(re.escape(t) + r"\\.(\\w+)\\s*\\(", body)
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


# [pr_diff] fail_to_pass
def test_all_three_targets_use_safe_setter():
    """All three registration targets are updated, not just one or two."""
    r = subprocess.run(
        ["python3", "-c", """
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
# Check for iterator-based index skipping as alternative fix
if re.search(r"\\.initFast\\s*\\([^)]*\\b(?:true|false)\\b[^)]*\\)", body):
    sys.exit(0)
if re.search(r"(?:isIndex|parseIndex)\\s*\\([^)]*\\)\\s*[^;]*(?:continue|break|return)", body):
    sys.exit(0)
targets = ["expect_proto", "expect_constructor", "expect_static_proto"]
safe_count = 0
for t in targets:
    bare_puts = re.findall(re.escape(t) + r"\\.put\\s*\\(", body)
    all_methods = re.findall(re.escape(t) + r"\\.(\\w+)\\s*\\(", body)
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


# [pr_diff] pass_to_pass
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


# [static] pass_to_pass
def test_key_functions_preserved():
    """Core expect functions still exist in expect.zig."""
    text = FILE.read_text()
    required = ["applyCustomMatcher", "pub fn extend", "pub fn call", "pub fn getNot"]
    missing = [fn for fn in required if fn not in text]
    assert not missing, f"Missing functions: {missing}"


# [static] pass_to_pass
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


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 6034bd82
def test_no_inline_import_in_functions():
    """No @import() inline inside the extend function body (src/CLAUDE.md:11)."""
    body = _get_extend_body()
    for line in body.split("\n"):
        stripped = line.strip()
        assert "@import" not in stripped, (
            f"Inline @import found inside extend() body: {stripped[:80]}"
        )


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 6034bd82
def test_no_std_direct_usage():
    """No std.fs/std.posix/std.os introduced in the extend function (src/CLAUDE.md:16)."""
    body = _get_extend_body()
    violations = re.findall(r"std\.(fs|posix|os)\.\w+", body)
    assert not violations, f"Found std.* in extend() (should use bun.* instead): {violations}"


# [agent_config] pass_to_pass — src/CLAUDE.md:232 @ 6034bd82
def test_no_wrong_allocator():
    """New allocator usage should use bun.default_allocator (src/CLAUDE.md:232)."""
    body = _get_extend_body()
    assert "std.heap" not in body, "extend() uses std.heap — should use bun.default_allocator"
    assert "GeneralPurposeAllocator" not in body, (
        "extend() uses GeneralPurposeAllocator — should use bun.default_allocator"
    )


# [agent_config] pass_to_pass — src/CLAUDE.md:234 @ 6034bd82
def test_no_catch_outofmemory_pattern():
    """Must not use 'catch bun.outOfMemory()' — use bun.handleOom() (src/CLAUDE.md:234)."""
    body = _get_extend_body()
    assert not re.search(r"catch\s+bun\.outOfMemory\s*\(\s*\)", body), (
        "extend() uses 'catch bun.outOfMemory()' — use bun.handleOom() instead"
    )
