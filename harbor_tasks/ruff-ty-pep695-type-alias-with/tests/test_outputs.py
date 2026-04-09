"""
Task: ruff-ty-pep695-type-alias-with
Repo: astral-sh/ruff @ 2f839db9e4045e93de0ef6b67a62cb9fc31fe373
PR:   24395

PEP 695 type aliases (type X = A | B) fail to work in with statements because
the TypeAlias match arm in member_lookup_with_policy comes after the
no_instance_fallback() guard, which short-circuits dunder method lookups.
The fix moves the TypeAlias arm earlier in the match.

No Rust toolchain compilation in verifier — tests use Python subprocess to
analyze the Rust source code since cargo build of the full ruff workspace
would exceed verifier timeout.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/ruff"
TYPES_FILE = f"{REPO}/crates/ty_python_semantic/src/types.rs"
MDTEST_FILE = f"{REPO}/crates/ty_python_semantic/resources/mdtest/with/sync.md"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python snippet via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence and basic integrity
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_source_files_exist():
    """Required source files exist with substantial content."""
    r = _run_py(f"""
import sys
from pathlib import Path
types_rs = Path("{TYPES_FILE}")
mdtest = Path("{MDTEST_FILE}")
if not types_rs.is_file():
    print("FAIL: types.rs missing")
    sys.exit(1)
if not mdtest.is_file():
    print("FAIL: with/sync.md missing")
    sys.exit(1)
lines = types_rs.read_text().split("\\n")
if len(lines) < 3000:
    print(f"FAIL: types.rs only {{len(lines)}} lines — likely stubbed")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Source check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_typealias_before_no_instance_fallback():
    """TypeAlias match arm must appear before no_instance_fallback guard.

    The core bug: Type::TypeAlias was matched AFTER the no_instance_fallback()
    guard in member_lookup_with_policy. This meant that dunder lookups
    (__enter__, __exit__) on type alias types hit the descriptor protocol
    fallback instead of unwrapping the alias first. The fix moves the
    TypeAlias arm earlier so it runs before the fallback.
    """
    r = _run_py(f"""
import re, sys

src = open("{TYPES_FILE}").read()
lines = src.split("\\n")

# Find the member_lookup_with_policy function
func_start = None
for i, line in enumerate(lines):
    if "fn member_lookup_with_policy" in line:
        func_start = i
        break

if func_start is None:
    print("FAIL: member_lookup_with_policy function not found")
    sys.exit(1)

# Find all Type::TypeAlias match arms and no_instance_fallback references
# within the function body (up to the next fn at same indent or end of impl)
func_body_lines = []
depth = 0
started = False
for i in range(func_start, min(func_start + 200, len(lines))):
    line = lines[i]
    if "{{" in line:
        depth += line.count("{{")
        started = True
    if started:
        func_body_lines.append((i + 1, line))
    depth -= line.count("}}")
    if started and depth <= 0:
        break

# Find line numbers of TypeAlias match arm and first no_instance_fallback
alias_lines = []
fallback_lines = []
for lineno, line in func_body_lines:
    stripped = line.strip()
    if "Type::TypeAlias" in stripped and "=>" in stripped:
        alias_lines.append(lineno)
    if "no_instance_fallback" in stripped:
        fallback_lines.append(lineno)

if not alias_lines:
    print("FAIL: No Type::TypeAlias match arm found in member_lookup_with_policy")
    sys.exit(1)

if not fallback_lines:
    print("FAIL: No no_instance_fallback reference found")
    sys.exit(1)

# The TypeAlias arm must come BEFORE the first no_instance_fallback reference
first_alias = min(alias_lines)
first_fallback = min(fallback_lines)

if first_alias >= first_fallback:
    print(f"FAIL: TypeAlias arm at line {{first_alias}} is NOT before no_instance_fallback at line {{first_fallback}}")
    sys.exit(1)

print(f"PASS: TypeAlias at {{first_alias}} before no_instance_fallback at {{first_fallback}}")
""")
    assert r.returncode == 0, f"TypeAlias ordering check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_typealias_unwraps_to_value_type():
    """TypeAlias match arm must delegate to value_type's member_lookup.

    The fix doesn't just move the arm — the arm must actually call
    alias.value_type(db).member_lookup_with_policy() to unwrap the alias
    and delegate the lookup to the underlying type.
    """
    types_file = TYPES_FILE
    code = """
import sys

src = open("{{types_file}}").read()
lines = src.split("\\n")

# Find the member_lookup_with_policy function
func_start = None
for i, line in enumerate(lines):
    if "fn member_lookup_with_policy" in line:
        func_start = i
        break

if func_start is None:
    print("FAIL: member_lookup_with_policy not found")
    sys.exit(1)

# Collect lines for each TypeAlias match arm
# Check that each TypeAlias arm body contains value_type and member_lookup_with_policy
in_typealias_arm = False
arm_depth = 0
arm_content = []
found_delegation = False

depth = 0
started = False
for i in range(func_start, min(func_start + 200, len(lines))):
    line = lines[i]
    depth += line.count("{{") - line.count("}}")
    if depth > 0:
        started = True
    stripped = line.strip()

    if "Type::TypeAlias" in stripped and "=>" in stripped:
        in_typealias_arm = True
        arm_depth = 0
        arm_content = [stripped]
        continue

    if in_typealias_arm:
        arm_depth += line.count("{{") - line.count("}}")
        arm_content.append(stripped)
        if arm_depth <= 0 and started:
            # End of this match arm
            arm_text = " ".join(arm_content)
            if "value_type" in arm_text and "member_lookup_with_policy" in arm_text:
                found_delegation = True
            in_typealias_arm = False

    if started and depth <= 0:
        break

if not found_delegation:
    print("FAIL: TypeAlias arm does not call value_type().member_lookup_with_policy()")
    sys.exit(1)

print("PASS")
""".replace("{{types_file}}", types_file)
    r = _run_py(code)
    assert r.returncode == 0, f"Value type delegation check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_mdtest_type_alias_with_section():
    """Regression mdtest for type aliases in with statements exists.

    The PR adds a "Type aliases preserve context manager behavior" section
    to the with/sync.md mdtest file, testing that Union types created via
    TypeAlias, PEP 695 type statement, and TypeAliasType all work correctly
    in with statements.
    """
    r = _run_py(f"""
import sys
from pathlib import Path

mdtest = Path("{MDTEST_FILE}")
if not mdtest.is_file():
    print("FAIL: with/sync.md not found")
    sys.exit(1)

content = mdtest.read_text()

# Must have the section header
if "Type aliases preserve context manager behavior" not in content:
    print("FAIL: 'Type aliases preserve context manager behavior' section missing")
    sys.exit(1)

# Must test all three forms of type alias
required_patterns = [
    ("TypeAlias annotation", "TypeAlias"),
    ("PEP 695 type statement", "type UnionAB"),
    ("TypeAliasType call", "TypeAliasType"),
]
for desc, pattern in required_patterns:
    if pattern not in content:
        print(f"FAIL: Missing {{desc}} test case (pattern: {{pattern}})")
        sys.exit(1)

# Must test with statement usage
if "with x as y:" not in content:
    print("FAIL: No with statement test found in the new section")
    sys.exit(1)

# Must have reveal_type checks showing correct inference
if "reveal_type(y)" not in content:
    print("FAIL: No reveal_type assertions for with statement variable")
    sys.exit(1)

# Must include python-version = "3.12" for PEP 695 support
if 'python-version = "3.12"' not in content:
    print("FAIL: Missing python-version 3.12 config for PEP 695 syntax")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Mdtest section check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static / repo_tests) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_descriptor_protocol_still_exists():
    """The no_instance_fallback / descriptor_protocol path still exists.

    The fix only reorders match arms — it doesn't remove the descriptor
    protocol fallback. This should exist on both base and fix.
    """
    r = _run_py(f"""
import sys

src = open("{TYPES_FILE}").read()

if "invoke_descriptor_protocol" not in src:
    print("FAIL: invoke_descriptor_protocol method missing")
    sys.exit(1)

if "no_instance_fallback" not in src:
    print("FAIL: no_instance_fallback check missing")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Descriptor protocol check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_member_lookup_not_stubbed():
    """member_lookup_with_policy function has substantial body (anti-stub).

    The function should have many match arms — it's the central dispatch
    for member lookups in the type system.
    """
    r = _run_py(f"""
import re, sys

src = open("{TYPES_FILE}").read()
lines = src.split("\\n")

# Find function start
func_start = None
for i, line in enumerate(lines):
    if "fn member_lookup_with_policy" in line:
        func_start = i
        break

if func_start is None:
    print("FAIL: member_lookup_with_policy not found")
    sys.exit(1)

# Count match arms (Type:: patterns) in the function body
match_arms = 0
depth = 0
started = False
func_lines = 0
for i in range(func_start, min(func_start + 300, len(lines))):
    line = lines[i]
    if "{{" in line:
        depth += line.count("{{")
        started = True
    if started:
        func_lines += 1
        if re.search(r'Type::\w+', line.strip()):
            match_arms += 1
    depth -= line.count("}}")
    if started and depth <= 0:
        break

if func_lines < 50:
    print(f"FAIL: Function only {{func_lines}} lines — likely stubbed")
    sys.exit(1)

if match_arms < 5:
    print(f"FAIL: Only {{match_arms}} Type:: match arms — likely stubbed (need >= 5)")
    sys.exit(1)

print(f"PASS: {{func_lines}} lines, {{match_arms}} match arms")
""")
    assert r.returncode == 0, f"Anti-stub check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_no_local_use_statements():
    """Rust imports at function scope are forbidden per AGENTS.md.

    AGENTS.md: 'Rust imports should always go at the top of the file,
    never locally in functions.'
    """
    r = _run_py(f"""
import re, sys

src = open("{TYPES_FILE}").read()
lines = src.split("\\n")

# Track function depth and check for local use statements
in_fn = 0
violations = []
for i, line in enumerate(lines):
    stripped = line.strip()
    in_fn += line.count("{{") - line.count("}}")

    # Check for 'use ' inside a function (indent > 0 suggests function scope)
    if in_fn > 0 and stripped.startswith("use ") and not stripped.startswith("#"):
        # Allow use inside closures (check if it's a common pattern)
        # But flag any `use X::Y;` at function level
        if re.match(r'^use\\\\s+\\\\w', stripped):
            violations.append((i + 1, stripped))

if violations:
    print(f"FAIL: Found local use statements (AGENTS.md violation):")
    for lineno, stmt in violations[:5]:
        print(f"  Line {{lineno}}: {{stmt}}")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Local imports check failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout
