"""
Task: nextjs-turbopack-trace-fs-readdir
Repo: vercel/next.js @ 4582b5fa93dd65b6f9ed1dff7e66bdb93ddd653c
PR:   92148

Turbopack's node-file-trace (NFT) did not recognize fs.readdir / fs.readdirSync
calls as well-known functions, so directory assets referenced through readdir
were not traced. The fix adds FsReadDir to WellKnownFunctionKind, maps readdir
and readdirSync in well_known.rs, and adds a DirAssetReference handler in
references/mod.rs.

No Rust toolchain is available in the Docker image and cargo check would
exceed timeout even if it were. Tests use subprocess to execute Python
analysis scripts that parse the Rust source.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
MOD_RS = f"{REPO}/turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs"
WELL_KNOWN_RS = f"{REPO}/turbopack/crates/turbopack-ecmascript/src/analyzer/well_known.rs"
REFERENCES_RS = f"{REPO}/turbopack/crates/turbopack-ecmascript/src/references/mod.rs"
UNIT_RS = f"{REPO}/turbopack/crates/turbopack-tracing/tests/unit.rs"
WILDCARD_INPUT = f"{REPO}/turbopack/crates/turbopack-tracing/tests/node-file-trace/test/unit/wildcard/input.js"
WILDCARD3_INPUT = f"{REPO}/turbopack/crates/turbopack-tracing/tests/node-file-trace/test/unit/wildcard3/input.js"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python snippet via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — source file sanity
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_source_files_exist():
    """Required source files exist and are not stubbed."""
    r = _run_py(f"""
import sys
from pathlib import Path
files = [
    "{MOD_RS}",
    "{WELL_KNOWN_RS}",
    "{REFERENCES_RS}",
    "{UNIT_RS}",
    "{WILDCARD_INPUT}",
    "{WILDCARD3_INPUT}",
]
for f in files:
    p = Path(f)
    if not p.is_file():
        print(f"FAIL: {{f}} missing")
        sys.exit(1)
    lines = p.read_text().split("\\n")
    if len(lines) < 20:
        print(f"FAIL: {{f}} only {{len(lines)}} lines — likely stubbed")
        sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Source check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_fsreaddir_enum_variant():
    """WellKnownFunctionKind enum has FsReadDir variant in correct position.

    Verifies the complete mapping chain part 1: the enum variant exists
    and is positioned between FsReadMethod and PathToFileUrl (ASCII order
    per cargo fmt convention).
    """
    r = _run_py(f"""
import re, sys
src = open("{MOD_RS}").read()

# Find the WellKnownFunctionKind enum body
enum_match = re.search(r'pub enum WellKnownFunctionKind\\s*\\{{', src)
if not enum_match:
    print("FAIL: WellKnownFunctionKind enum not found")
    sys.exit(1)

# Extract enum body
start = enum_match.end()
depth = 1
pos = start
while pos < len(src) and depth > 0:
    if src[pos] == '{{':
        depth += 1
    elif src[pos] == '}}':
        depth -= 1
    pos += 1
enum_body = src[start:pos]

# FsReadDir must exist as a variant
if "FsReadDir" not in enum_body:
    print("FAIL: FsReadDir variant missing from WellKnownFunctionKind")
    sys.exit(1)

# Extract variant names in order (simple parse: lines with uppercase identifiers)
variants = []
for line in enum_body.split("\\n"):
    stripped = line.strip().rstrip(",")
    if stripped and stripped[0].isupper() and "(" in stripped or stripped[0].isupper() and not stripped.startswith("//"):
        # Extract variant name
        name = stripped.split("(")[0].split("//")[0].strip()
        if name and name[0].isupper():
            variants.append(name)

# Check FsReadDir is between FsReadMethod and PathToFileUrl
fs_read_idx = None
path_to_file_idx = None
for i, v in enumerate(variants):
    if v == "FsReadDir":
        fs_read_idx = i
    if v == "PathToFileUrl":
        path_to_file_idx = i

if fs_read_idx is None:
    print("FAIL: FsReadDir not found in variant list")
    sys.exit(1)
if path_to_file_idx is None:
    print("FAIL: PathToFileUrl not found in variant list")
    sys.exit(1)
if fs_read_idx > path_to_file_idx:
    print("FAIL: FsReadDir should come before PathToFileUrl (ASCII order)")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Enum check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_readdir_sync_mapping():
    """well_known.rs maps readdir and readdirSync to FsReadDir.

    Verifies the complete mapping chain part 2: the fs_module_member function
    recognizes both 'readdir' and 'readdirSync' property names and returns
    WellKnownFunctionKind::FsReadDir.
    """
    r = _run_py(f"""
import re, sys
src = open("{WELL_KNOWN_RS}").read()

# Find the match arm that handles readdir
# Must contain both "readdir" and "readdirSync" in the same match arm
readdir_pattern = r'"readdir"\\s*\\|\\s*"readdirSync"'
if not re.search(readdir_pattern, src):
    # Try alternative pattern
    if '"readdir"' not in src or '"readdirSync"' not in src:
        print("FAIL: readdir/readdirSync pattern not found in well_known.rs")
        sys.exit(1)

# The match arm must return FsReadDir
if "WellKnownFunctionKind::FsReadDir" not in src:
    print("FAIL: WellKnownFunctionKind::FsReadDir not used in well_known.rs")
    sys.exit(1)

# The mapping must be inside fs_module_member function context
# Find lines around the readdir match
lines = src.split("\\n")
found_context = False
for i, line in enumerate(lines):
    if '"readdir"' in line:
        # Check surrounding context for WellKnownFunction mapping
        context = "\\n".join(lines[max(0, i - 2):i + 5])
        if "FsReadDir" in context and "WellKnownFunction" in context:
            found_context = True
            break

if not found_context:
    print("FAIL: readdir mapping does not produce WellKnownFunction(FsReadDir)")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Mapping check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_dir_asset_reference_handler():
    """references/mod.rs has FsReadDir handler creating DirAssetReference.

    Verifies the complete mapping chain part 3: when FsReadDir is encountered
    during asset tracing, the handler creates a DirAssetReference with proper
    pattern analysis, dynamic pattern warnings, and error handling.
    """
    r = _run_py(f"""
import re, sys
src = open("{REFERENCES_RS}").read()

# Must have a match arm for FsReadDir with tracing_assets guard
if "WellKnownFunctionKind::FsReadDir" not in src:
    print("FAIL: FsReadDir match arm missing from references/mod.rs")
    sys.exit(1)

# Must check analyze_mode.is_tracing_assets()
if "is_tracing_assets()" not in src:
    print("FAIL: is_tracing_assets guard missing")
    sys.exit(1)

# Must create DirAssetReference
if "DirAssetReference::new" not in src:
    print("FAIL: DirAssetReference::new not used in FsReadDir handler")
    sys.exit(1)

# Must handle dynamic patterns (warn about very dynamic readdir calls)
if "fs.readdir" not in src:
    print("FAIL: fs.readdir diagnostic message missing")
    sys.exit(1)

# Must handle non-analyzable case (empty args)
if "not statically analyze-able" not in src:
    print("FAIL: error message for non-analyzable readdir missing")
    sys.exit(1)

# Verify the handler adds the reference via analysis.add_reference
if "analysis.add_reference" not in src:
    print("FAIL: analysis.add_reference call missing")
    sys.exit(1)

# The handler must use js_value_to_pattern to convert args
if "js_value_to_pattern" not in src:
    print("FAIL: js_value_to_pattern not used — handler may not properly convert paths")
    sys.exit(1)

# The handler must check has_constant_parts for dynamic detection
if "has_constant_parts" not in src:
    print("FAIL: has_constant_parts check missing — dynamic pattern detection absent")
    sys.exit(1)

# The handler must handle ignore_dynamic_requests
if "ignore_dynamic_requests" not in src:
    print("FAIL: ignore_dynamic_requests handling missing")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Handler check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_fsreaddir_description_in_impl():
    """FsReadDir has human-readable description in the WellKnownFunction match.

    Verifies that FsReadDir is covered by the impl block that provides
    descriptive names for well-known functions (used in diagnostics).
    """
    r = _run_py(f"""
import re, sys
src = open("{MOD_RS}").read()

# Find the match arm for FsReadDir in the impl block
# It should map to ("fs.readdir", description)
lines = src.split("\\n")
found = False
for i, line in enumerate(lines):
    if "WellKnownFunctionKind::FsReadDir" in line:
        context = "\\n".join(lines[i:i + 5])
        if '"fs.readdir"' in context:
            found = True
            # Description must mention fs or readdir
            if "readdir" not in context.lower():
                print("FAIL: FsReadDir description does not mention readdir")
                sys.exit(1)
            break

if not found:
    print("FAIL: FsReadDir has no description in the WellKnownFunction impl")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Description check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_wildcard_fixtures_have_fs_import():
    """Test fixture files have const fs = require('fs') for readdir tracing.

    The PR adds fs require to wildcard/input.js and wildcard3/input.js
    so the readdir call is recognized through the fs module member path.
    """
    r = _run_py(f"""
import sys
for path in ["{WILDCARD_INPUT}", "{WILDCARD3_INPUT}"]:
    content = open(path).read()
    if "require('fs')" not in content and 'require("fs")' not in content:
        print(f"FAIL: {{path}} missing fs require")
        sys.exit(1)
    if "const fs" not in content:
        print(f"FAIL: {{path}} missing 'const fs' declaration")
        sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Fixture check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_nft_unit_tests_enabled():
    """NFT unit test cases are enabled (uncommented) in unit.rs.

    The PR enables dirname_emit, dirname_emit_concat, wildcard_require,
    and wildcard3 test cases that were previously commented out.
    """
    r = _run_py(f"""
import re, sys
src = open("{UNIT_RS}").read()

# These test cases must be active (not commented out)
required_cases = [
    ("dirname_emit", "dirname-emit"),
    ("dirname_emit_concat", "dirname-emit-concat"),
    ("wildcard_require", "wildcard-require"),
    ("wildcard3", "wildcard3"),
]

for case_name, case_arg in required_cases:
    # Active test case: #[case::name("arg")]
    pattern = rf'#\\[case::{case_name}\\("{case_arg}"\\)\\]'
    if not re.search(pattern, src):
        # Check if it's commented out
        commented = rf'//\\s*#\\[case::{case_name}\\("{case_arg}"\\)\\]'
        if re.search(commented, src):
            print(f"FAIL: {{case_name}} is still commented out")
        else:
            print(f"FAIL: {{case_name}} test case not found at all")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Unit test check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_well_known_module_intact():
    """well_known.rs still has core fs_module_member function.

    Regression test: verifies the fix didn't corrupt the module by checking
    that the fs_module_member function exists with substantial body.
    """
    r = _run_py(f"""
import re, sys
src = open("{WELL_KNOWN_RS}").read()

# fs_module_member function must exist
if "fn fs_module_member" not in src:
    print("FAIL: fs_module_member function missing")
    sys.exit(1)

# Find function body
fn_match = re.search(r'fn fs_module_member\\([^)]*\\)\\s*->\\s*JsValue\\s*\\{{', src)
if not fn_match:
    print("FAIL: fs_module_member signature not found")
    sys.exit(1)

start = fn_match.end()
depth = 1
pos = start
while pos < len(src) and depth > 0:
    if src[pos] == '{{':
        depth += 1
    elif src[pos] == '}}':
        depth -= 1
    pos += 1
body = src[start:pos]
body_lines = [l for l in body.split("\\n") if l.strip() and not l.strip().startswith("//")]

if len(body_lines) < 20:
    print(f"FAIL: fs_module_member only {{len(body_lines)}} non-comment lines — likely stubbed")
    sys.exit(1)

# Must still have existing fs method mappings (not just readdir)
essential = ["readFileSync", "readFile", "promises"]
for pattern in essential:
    if pattern not in body:
        print(f"FAIL: fs_module_member missing {{pattern}} — existing mappings removed")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Module intact check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_references_module_not_stubbed():
    """references/mod.rs has substantial code in the tracing handler section.

    Anti-stub test: verifies that the FsReadDir handler is part of a
    substantial module, not just a few placeholder lines.
    """
    r = _run_py(f"""
import sys
src = open("{REFERENCES_RS}").read()
lines = src.split("\\n")
non_empty = [l for l in lines if l.strip() and not l.strip().startswith("//")]
if len(non_empty) < 100:
    print(f"FAIL: references/mod.rs only {{len(non_empty)}} non-empty lines — likely stubbed")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Stub check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout
