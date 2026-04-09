"""
Task: ruff-ty-make-possiblymissingattribute-ignored-by
Repo: ruff @ 74c7fe849fdfe8b79e8e8e031e5e7b3673be3f4a
PR:   astral-sh/ruff#23918

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/ruff"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_schema_attribute_default_ignore():
    """ty.schema.json: possibly-missing-attribute default must be 'ignore'."""
    r = subprocess.run(
        ["python3", "-c", """
import json, sys
schema = json.load(open('ty.schema.json'))
rules = schema['definitions']['Rules']['properties']
rule = rules.get('possibly-missing-attribute', {})
default = rule.get('default')
if default != 'ignore':
    print(f"FAIL: possibly-missing-attribute default is {default!r}, expected 'ignore'", file=sys.stderr)
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_schema_submodule_rule_exists():
    """ty.schema.json: possibly-missing-submodule rule must exist with default 'warn'."""
    r = subprocess.run(
        ["python3", "-c", """
import json, sys
schema = json.load(open('ty.schema.json'))
rules = schema['definitions']['Rules']['properties']
rule = rules.get('possibly-missing-submodule')
if rule is None:
    print("FAIL: possibly-missing-submodule rule not found in schema", file=sys.stderr)
    sys.exit(1)
default = rule.get('default')
if default != 'warn':
    print(f"FAIL: possibly-missing-submodule default is {default!r}, expected 'warn'", file=sys.stderr)
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_diagnostic_rs_submodule_lint_defined():
    """diagnostic.rs must define POSSIBLY_MISSING_SUBMODULE lint."""
    diag = Path(REPO) / "crates/ty_python_semantic/src/types/diagnostic.rs"
    content = diag.read_text()
    assert "POSSIBLY_MISSING_SUBMODULE" in content, \
        "diagnostic.rs should define POSSIBLY_MISSING_SUBMODULE"


# [pr_diff] fail_to_pass
def test_diagnostic_rs_attribute_default_ignore():
    """diagnostic.rs: POSSIBLY_MISSING_ATTRIBUTE must have default_level: Level::Ignore."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

content = open('crates/ty_python_semantic/src/types/diagnostic.rs').read()

# Find the POSSIBLY_MISSING_ATTRIBUTE block — it ends at the next closing brace+newline
marker = 'static POSSIBLY_MISSING_ATTRIBUTE'
idx = content.find(marker)
if idx == -1:
    print("FAIL: POSSIBLY_MISSING_ATTRIBUTE not found", file=sys.stderr)
    sys.exit(1)

# Extract the block (up to ~500 chars after the marker is plenty)
block = content[idx:idx+500]

if 'Level::Ignore' not in block:
    if 'Level::Warn' in block:
        print("FAIL: POSSIBLY_MISSING_ATTRIBUTE still uses Level::Warn, should be Level::Ignore", file=sys.stderr)
    else:
        print("FAIL: Could not find default_level in POSSIBLY_MISSING_ATTRIBUTE block", file=sys.stderr)
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_builder_uses_submodule_lint():
    """builder.rs must use POSSIBLY_MISSING_SUBMODULE for submodule diagnostics."""
    builder = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder.rs"
    content = builder.read_text()
    assert "POSSIBLY_MISSING_SUBMODULE" in content, \
        "builder.rs should import and use POSSIBLY_MISSING_SUBMODULE"


# [pr_diff] fail_to_pass
def test_mdtest_submodule_diagnostics_updated():
    """mdtest files must use [possibly-missing-submodule] for submodule access cases."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

# Check nonstandard_conventions.md uses the new rule for submodule cases
path = 'crates/ty_python_semantic/resources/mdtest/import/nonstandard_conventions.md'
content = open(path).read()

# There should be references to possibly-missing-submodule
if 'possibly-missing-submodule' not in content:
    print(f"FAIL: {path} should reference possibly-missing-submodule", file=sys.stderr)
    sys.exit(1)

# The old submodule messages should be gone
if 'possibly-missing-attribute' in content and 'Submodule' in content.split('possibly-missing-attribute')[1][:100]:
    print(f"FAIL: {path} still uses possibly-missing-attribute for submodule diagnostics", file=sys.stderr)
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_primer_toml_enables_attribute_rule():
    """mypy-primer-ty.toml must explicitly enable possibly-missing-attribute for ecosystem testing."""
    toml_path = Path(REPO) / ".github/mypy-primer-ty.toml"
    content = toml_path.read_text()
    assert 'possibly-missing-attribute' in content, \
        "mypy-primer-ty.toml should explicitly enable possibly-missing-attribute since it's now off by default"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_diagnostic_registry_has_attribute_lint():
    """diagnostic.rs must still register POSSIBLY_MISSING_ATTRIBUTE."""
    diag = Path(REPO) / "crates/ty_python_semantic/src/types/diagnostic.rs"
    content = diag.read_text()
    assert "register_lint(&POSSIBLY_MISSING_ATTRIBUTE)" in content, \
        "POSSIBLY_MISSING_ATTRIBUTE must still be registered"


# [static] pass_to_pass
def test_schema_valid_json():
    """ty.schema.json must be valid JSON."""
    r = subprocess.run(
        ["python3", "-c", "import json; json.load(open('ty.schema.json')); print('PASS')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Agent config (AGENTS.md) — pass_to_pass
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
def test_agents_md_generate_all_instruction():
    """AGENTS.md documents running cargo dev generate-all after changing lint rules."""
    content = (Path(REPO) / "AGENTS.md").read_text()
    assert "cargo dev generate-all" in content, \
        "AGENTS.md should instruct running cargo dev generate-all after lint rule changes"
