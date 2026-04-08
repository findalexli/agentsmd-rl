"""
Task: uv-python-source-explicit-method
Repo: astral-sh/uv @ d7da792648a6e8bc2e56162f5890f44333df9ab8
PR:   #18569

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Rust project without cargo/rustc in Docker image.
f2p tests use subprocess to run grep and Python analysis scripts
that parse and simulate the Rust code's behavior.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/repo")
FILE = REPO / "crates/uv-python/src/discovery.rs"

EXPLICIT_VARIANTS = [
    "ProvidedPath", "ParentInterpreter", "ActiveEnvironment", "CondaPrefix",
]
NON_EXPLICIT_VARIANTS = [
    "Managed", "DiscoveredEnvironment", "SearchPath", "SearchPathFirst",
    "Registry", "MicrosoftStore", "BaseCondaPrefix",
]
ALL_VARIANTS = EXPLICIT_VARIANTS + NON_EXPLICIT_VARIANTS


def _extract_method_body(src: str, method_pattern: str) -> str:
    """Extract the brace-matched body of a Rust method."""
    m = re.search(method_pattern, src)
    assert m, f"Method matching {method_pattern!r} not found"
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    return src[start : i - 1]


def _grep_count(pattern: str) -> int:
    """Count lines matching pattern in FILE via grep."""
    r = subprocess.run(
        ["grep", "-c", pattern, str(FILE)],
        capture_output=True, text=True, timeout=10,
    )
    try:
        return int(r.stdout.strip())
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_is_explicit_method_exists():
    """PythonSource has an is_explicit method returning bool."""
    r = subprocess.run(
        ["grep", "-qE", r"fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{", str(FILE)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, (
        "is_explicit(&self) -> bool method not found on PythonSource"
    )


# [pr_diff] fail_to_pass
def test_is_explicit_variant_mapping():
    """is_explicit returns true for explicit variants, false for non-explicit.

    Behavioral test: writes a Python script that parses the Rust source,
    extracts the is_explicit method body, builds a variant->bool mapping,
    and simulates calling is_explicit() for every variant.
    """
    script = REPO / "_eval_is_explicit.py"
    script.write_text(
        r"""
import re, sys
from pathlib import Path

src = Path("/repo/crates/uv-python/src/discovery.rs").read_text()

# Locate is_explicit method
m = re.search(r'fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{', src)
if not m:
    print("FAIL: is_explicit method not found", file=sys.stderr)
    sys.exit(1)

# Extract brace-matched body
start = m.end()
depth, i = 1, m.end()
while i < len(src) and depth > 0:
    if src[i] == '{': depth += 1
    elif src[i] == '}': depth -= 1
    i += 1
body = src[start:i-1]

explicit = ["ProvidedPath", "ParentInterpreter", "ActiveEnvironment", "CondaPrefix"]
non_explicit = ["Managed", "DiscoveredEnvironment", "SearchPath", "SearchPathFirst",
                "Registry", "MicrosoftStore", "BaseCondaPrefix"]

# Build variant -> bool mapping from match arms
mapping = {}
for arm_match in re.finditer(
    r'((?:(?:Self|PythonSource)::\w+\s*\|?\s*)+)\s*=>\s*(true|false)', body
):
    value = arm_match.group(2) == "true"
    for v in re.findall(r'(?:Self|PythonSource)::(\w+)', arm_match.group(1)):
        mapping[v] = value

# Handle wildcard _ => false
if re.search(r'_\s*=>\s*false', body):
    for v in non_explicit:
        if v not in mapping:
            mapping[v] = False

# Try matches! macro if no match arms found
if not mapping:
    matches_call = re.search(r'matches!\s*\(\s*self\s*,\s*(.*?)\)', body, re.DOTALL)
    if matches_call:
        for v in re.findall(r'(?:Self|PythonSource)::(\w+)', matches_call.group(1)):
            mapping[v] = True
        for v in non_explicit:
            if v not in mapping:
                mapping[v] = False

# Try !matches! macro
if not mapping:
    neg = re.search(r'!\s*matches!\s*\(\s*self\s*,\s*(.*?)\)', body, re.DOTALL)
    if neg:
        for v in re.findall(r'(?:Self|PythonSource)::(\w+)', neg.group(1)):
            mapping[v] = False
        for v in explicit:
            if v not in mapping:
                mapping[v] = True

if not mapping:
    print("FAIL: could not parse is_explicit logic", file=sys.stderr)
    sys.exit(1)

expected = {
    "ProvidedPath": True, "ParentInterpreter": True,
    "ActiveEnvironment": True, "CondaPrefix": True,
    "Managed": False, "DiscoveredEnvironment": False,
    "SearchPath": False, "SearchPathFirst": False,
    "Registry": False, "MicrosoftStore": False,
    "BaseCondaPrefix": False,
}

# Simulate calling is_explicit for each variant and verify behavior
for variant, exp in expected.items():
    got = mapping.get(variant)
    if got != exp:
        print(f"FAIL: is_explicit({variant}) = {got}, expected {exp}", file=sys.stderr)
        sys.exit(1)

print("PASS")
"""
    )
    try:
        r = subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=30, cwd=str(REPO),
        )
        assert r.returncode == 0, f"Variant mapping analysis failed: {r.stderr}"
        assert "PASS" in r.stdout
    finally:
        script.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_allows_installation_delegates():
    """allows_installation calls source.is_explicit() instead of inline match."""
    count = _grep_count(".is_explicit()")
    assert count >= 2, (
        f"Expected >=2 calls to .is_explicit(), found {count}"
    )


# [pr_diff] fail_to_pass
def test_allows_installation_no_inline_variant_match():
    """allows_installation no longer contains PythonSource variant arms for the explicit check."""
    count = _grep_count("let is_explicit = match")
    assert count == 0, (
        "allows_installation still has 'let is_explicit = match source { ... }'"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guards
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_is_maybe_system_preserved():
    """is_maybe_system method must still exist (regression guard)."""
    r = subprocess.run(
        ["grep", "-qE", r"fn\s+is_maybe_system\s*\(\s*&?\s*self\s*\)\s*->\s*bool", str(FILE)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, "is_maybe_system method missing — regression"


# [repo_tests] pass_to_pass
def test_allows_installation_preserved():
    """allows_installation method must still exist."""
    r = subprocess.run(
        ["grep", "-qE", r"fn\s+allows_installation\s*\(", str(FILE)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, "allows_installation method missing — regression"


# [repo_tests] pass_to_pass
def test_python_source_enum_preserved():
    """PythonSource enum must still have all expected variants."""
    script = REPO / "_eval_enum.py"
    script.write_text(
        r"""
import re, sys
from pathlib import Path

src = Path("/repo/crates/uv-python/src/discovery.rs").read_text()
variants = [
    "ProvidedPath", "ParentInterpreter", "ActiveEnvironment", "CondaPrefix",
    "Managed", "DiscoveredEnvironment", "SearchPath", "SearchPathFirst",
    "Registry", "MicrosoftStore", "BaseCondaPrefix",
]
for v in variants:
    if not re.search(rf"\b{v}\b", src):
        print(f"FAIL: variant {v} missing", file=sys.stderr)
        sys.exit(1)
print("PASS")
"""
    )
    try:
        r = subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=10, cwd=str(REPO),
        )
        assert r.returncode == 0, f"Enum variant check failed: {r.stderr}"
        assert "PASS" in r.stdout
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_is_explicit_not_stub():
    """is_explicit must have match/matches! with >=4 variant refs, not a trivial stub."""
    src = FILE.read_text()
    body = _extract_method_body(
        src, r"fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{"
    )
    assert "match" in body or "matches!" in body, (
        "is_explicit has no match/matches! expression"
    )
    variant_refs = set(re.findall(r"(?:Self|PythonSource)::(\w+)", body))
    assert len(variant_refs) >= 4, (
        f"is_explicit references only {len(variant_refs)} variants (need >=4)"
    )
    lines = [l.strip() for l in body.strip().splitlines() if l.strip()]
    assert len(lines) >= 3, f"is_explicit body too short ({len(lines)} lines)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:7 @ d7da792648a6e8bc2e56162f5890f44333df9ab8
def test_no_panic_unwrap_in_is_explicit():
    """AVOID using panic!, unreachable!, .unwrap(), unsafe code (CLAUDE.md:7)."""
    src = FILE.read_text()
    body = _extract_method_body(
        src, r"fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{"
    )
    for bad in [".unwrap()", "panic!", "unreachable!", "unsafe"]:
        assert bad not in body, f"is_explicit contains forbidden pattern: {bad}"


# [agent_config] fail_to_pass — CLAUDE.md:7,10 @ d7da792648a6e8bc2e56162f5890f44333df9ab8
def test_no_clippy_allow_in_is_explicit():
    """No #[allow(clippy::...)] — prefer #[expect()] if needed (CLAUDE.md:7,10)."""
    src = FILE.read_text()
    m = re.search(
        r"((?:#\[.*?\]\s*)*fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{)",
        src, re.DOTALL,
    )
    assert m, "is_explicit method not found"
    preamble = m.group(1)
    body = _extract_method_body(
        src, r"fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{"
    )
    combined = preamble + body
    assert "#[allow(" not in combined, (
        "is_explicit uses #[allow(...)]; prefer #[expect()] per CLAUDE.md:10"
    )
