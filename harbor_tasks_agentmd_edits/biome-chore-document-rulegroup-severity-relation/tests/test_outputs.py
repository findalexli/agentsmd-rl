"""
Task: biome-chore-document-rulegroup-severity-relation
Repo: biomejs/biome @ 72afdfa3451eb02d499c1a2a7dc826b37e3d5f8d
PR:   7827

Documents the relationship between rule groups and expected severity levels
in crates/biome_analyze/CONTRIBUTING.md, and expands xtask/rules_check to
enforce these constraints for all groups (not just style + actions).

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/biome"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------


def test_errors_struct_refactored():
    """Errors struct uses named 'message' field with new() constructor, not old tuple struct."""
    r = subprocess.run(
        ["python3", "-c", r"""
import sys

content = open('/workspace/biome/xtask/rules_check/src/lib.rs').read()

# Must have named field struct, not tuple struct
if 'struct Errors {' not in content:
    print("FAIL: Errors struct should use named fields (struct Errors { ... })")
    sys.exit(1)

if 'message: String' not in content:
    print("FAIL: Errors struct should have 'message: String' field")
    sys.exit(1)

# Must have Errors::new() constructor
if 'fn new(message: String)' not in content:
    print("FAIL: Errors should have fn new(message: String) constructor")
    sys.exit(1)

# Old tuple struct pattern should not exist
if 'struct Errors(String)' in content:
    print("FAIL: Old tuple struct Errors(String) should be removed")
    sys.exit(1)

# Old specific error methods should be removed
if 'fn style_rule_error' in content or 'fn action_error' in content:
    print("FAIL: Old style_rule_error/action_error methods should be removed")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_group_severity_checks():
    """check_rules() validates severity for a11y/correctness/security, complexity/style, performance, and suspicious groups."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys

content = open('/workspace/biome/xtask/rules_check/src/lib.rs').read()

# Must check a11y/correctness/security group requires Error severity
if not re.search(r'"a11y"\s*\|\s*"correctness"\s*\|\s*"security"', content):
    print("FAIL: Must check a11y | correctness | security group severity")
    sys.exit(1)

# Must check complexity/style group can't have Error severity
if not re.search(r'"complexity"\s*\|\s*"style"', content):
    print("FAIL: Must check complexity | style group severity")
    sys.exit(1)

# Must check performance group requires Warning severity
if '"performance"' not in content:
    print("FAIL: Must check performance group severity")
    sys.exit(1)

# Must check suspicious group can't have Information severity
if not re.search(r'group\s*==\s*"suspicious"', content):
    print("FAIL: Must check suspicious group severity")
    sys.exit(1)

# Must have exception lists for legacy rules (at least 3 of these known exceptions)
exceptions = ['noNodejsModules', 'noUnusedImports', 'noAlert', 'noAwaitInLoops']
found = sum(1 for e in exceptions if e in content)
if found < 3:
    print(f"FAIL: Expected at least 3 of the known exception rules, found {found}")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_contributing_severity_section():
    """CONTRIBUTING.md documents rule-group severity constraints for all groups."""
    r = subprocess.run(
        ["python3", "-c", r"""
import sys

content = open('/workspace/biome/crates/biome_analyze/CONTRIBUTING.md').read()

# Must have the new section header
if '#### Rule group and severity' not in content:
    print("FAIL: CONTRIBUTING.md must have 'Rule group and severity' section")
    sys.exit(1)

# Extract text after the new section header (up to next #### section)
import re
m = re.search(
    r'#### Rule group and severity\n(.*?)(?=\n####\s|\Z)',
    content, re.DOTALL,
)
if not m:
    print("FAIL: Could not extract 'Rule group and severity' section body")
    sys.exit(1)

section = m.group(1)

# Must document severity constraint for each group
required_groups = ['correctness', 'security', 'a11y', 'style',
                   'complexity', 'suspicious', 'performance']
for group in required_groups:
    if group not in section:
        print(f"FAIL: Section must document severity for '{group}' group")
        sys.exit(1)

# Must mention actions
if 'action' not in section.lower():
    print("FAIL: Section must document Actions severity")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------


def test_check_rules_function_exists():
    """The check_rules() public function still exists in lib.rs."""
    content = Path(f"{REPO}/xtask/rules_check/src/lib.rs").read_text()
    assert "pub fn check_rules()" in content, \
        "check_rules() function must exist in lib.rs"


def test_contributing_existing_sections():
    """Existing CONTRIBUTING.md sections (Rule severity, Rule domains) still present."""
    content = Path(f"{REPO}/crates/biome_analyze/CONTRIBUTING.md").read_text()
    assert "#### Rule severity" in content, \
        "Rule severity section must still exist"
    assert "#### Rule domains" in content, \
        "Rule domains section must still exist"
