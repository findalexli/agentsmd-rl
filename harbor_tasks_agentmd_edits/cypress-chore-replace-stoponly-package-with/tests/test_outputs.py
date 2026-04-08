"""
Task: cypress-chore-replace-stoponly-package-with
Repo: cypress-io/cypress @ d9cf1844842203937859811c814845fb42d7683a
PR:   33492

Replace the stop-only package with ESLint mocha/no-exclusive-tests rule,
and update AGENTS.md to reflect the new enforcement mechanism.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/cypress"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess for isolation."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """baseConfig.ts is valid TypeScript (no unclosed braces/brackets)."""
    src = Path(f"{REPO}/packages/eslint-config/src/baseConfig.ts").read_text()
    opens = src.count("{") + src.count("[") + src.count("(")
    closes = src.count("}") + src.count("]") + src.count(")")
    assert abs(opens - closes) <= 2, (
        f"Bracket imbalance in baseConfig.ts: opens={opens}, closes={closes}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_eslint_rule_enabled():
    """mocha/no-exclusive-tests is set to 'error' inside the ESLint rules block."""
    r = _run_py("""
import re, sys
src = open("/workspace/cypress/packages/eslint-config/src/baseConfig.ts").read()
# Must contain the rule declaration in the expected format
pattern = r"['"]mocha/no-exclusive-tests['"]\\s*:\\s*['"]error['"]"
match = re.search(pattern, src)
if not match:
    sys.exit("mocha/no-exclusive-tests: 'error' not found in baseConfig.ts")
# Verify it's inside a config object (not a comment or string elsewhere)
idx = match.start()
before = src[:idx]
depth = before.count("{") - before.count("}")
if depth <= 0:
    sys.exit("Rule appears outside of any config object")
print("PASS")
""")
    assert r.returncode == 0, f"ESLint rule check failed: {r.stderr}{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_stop_only_scripts_removed():
    """package.json must not contain stop-only or stop-only-all scripts."""
    r = _run_py("""
import json, sys
pkg = json.load(open("/workspace/cypress/package.json"))
scripts = pkg.get("scripts", {})
for key in ("stop-only", "stop-only-all"):
    if key in scripts:
        sys.exit(f"package.json still has '{key}' script")
print("PASS")
""")
    assert r.returncode == 0, f"Script removal check failed: {r.stderr}{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_stop_only_dependency_removed():
    """stop-only must not be listed as a devDependency."""
    r = _run_py("""
import json, sys
pkg = json.load(open("/workspace/cypress/package.json"))
deps = pkg.get("devDependencies", {})
if "stop-only" in deps:
    sys.exit(f"stop-only still in devDependencies: {deps['stop-only']}")
print("PASS")
""")
    assert r.returncode == 0, f"Dependency check failed: {r.stderr}{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_eslint_disable_on_cypress_tests():
    """cypress-tests.ts has eslint-disable for mocha/no-exclusive-tests at top."""
    src = Path(f"{REPO}/cli/types/tests/cypress-tests.ts").read_text()
    first_line = src.split("\n")[0]
    assert "eslint-disable" in first_line, (
        "First line of cypress-tests.ts must have an eslint-disable comment"
    )
    assert "mocha/no-exclusive-tests" in first_line, (
        "eslint-disable must target mocha/no-exclusive-tests"
    )


# [pr_diff] fail_to_pass
def test_eslintignore_has_node_modules():
    """npm/eslint-plugin-dev/.eslintignore includes node_modules."""
    ignore = Path(f"{REPO}/npm/eslint-plugin-dev/.eslintignore").read_text()
    lines = [l.strip() for l in ignore.strip().split("\n")]
    assert "node_modules" in lines, (
        "node_modules must be listed in npm/eslint-plugin-dev/.eslintignore"
    )


# [pr_diff] fail_to_pass
def test_ci_no_stop_only_step():
    """CircleCI pipeline should not reference the Stop .only step or yarn stop-only-all."""
    r = _run_py("""
import sys
pipeline = open("/workspace/cypress/.circleci/src/pipeline/@pipeline.yml").read()
for marker in ("Stop .only", "yarn stop-only-all"):
    if marker in pipeline:
        sys.exit(f"CircleCI pipeline still contains '{marker}'")
print("PASS")
""")
    assert r.returncode == 0, f"CI check failed: {r.stderr}{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — AGENTS.md updates
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass
def test_agentsmd_no_stop_only_commands():
    """AGENTS.md must not reference yarn stop-only commands."""
    agents = Path(f"{REPO}/AGENTS.md").read_text()
    assert "yarn stop-only\n" not in agents, (
        "AGENTS.md still references 'yarn stop-only'"
    )
    assert "yarn stop-only-all" not in agents, (
        "AGENTS.md still references 'yarn stop-only-all'"
    )


# [agent_config] fail_to_pass
def test_agentsmd_eslint_enforcement():
    """AGENTS.md describes ESLint-based .only enforcement mechanism."""
    agents = Path(f"{REPO}/AGENTS.md").read_text()
    # Find the .only enforcement line — must mention ESLint as the mechanism
    only_lines = [
        line for line in agents.split("\n")
        if ".only" in line and "no-exclusive-tests" in line
    ]
    assert len(only_lines) > 0, "AGENTS.md missing .only enforcement documentation"
    line = only_lines[0]
    assert "ESLint" in line, (
        "AGENTS.md .only enforcement line must mention ESLint as the mechanism"
    )
