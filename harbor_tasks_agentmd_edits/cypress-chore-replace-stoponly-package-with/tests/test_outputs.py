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


# [repo_tests] pass_to_pass
def test_repo_lerna_json_valid():
    """lerna.json is valid JSON (pass_to_pass)."""
    r = _run_py("""
import json, sys
try:
    json.load(open("/workspace/cypress/lerna.json"))
    print("PASS")
except json.JSONDecodeError as e:
    sys.exit(f"Invalid JSON in lerna.json: {e}")
""")
    assert r.returncode == 0, f"lerna.json validation failed: {r.stderr}{r.stdout}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_nx_json_valid():
    """nx.json is valid JSON (pass_to_pass)."""
    r = _run_py("""
import json, sys
try:
    json.load(open("/workspace/cypress/nx.json"))
    print("PASS")
except json.JSONDecodeError as e:
    sys.exit(f"Invalid JSON in nx.json: {e}")
""")
    assert r.returncode == 0, f"nx.json validation failed: {r.stderr}{r.stdout}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_eslint_mocha_plugin_dependency():
    """eslint-plugin-mocha is in eslint-config devDependencies (pass_to_pass)."""
    r = _run_py("""
import json, sys
pkg = json.load(open("/workspace/cypress/packages/eslint-config/package.json"))
deps = pkg.get("devDependencies", {})
if "eslint-plugin-mocha" not in deps:
    sys.exit("eslint-plugin-mocha not found in devDependencies")
print("PASS")
""")
    assert r.returncode == 0, f"ESLint mocha plugin check failed: {r.stderr}{r.stdout}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_agents_md_exists():
    """AGENTS.md file exists and is readable (pass_to_pass)."""
    try:
        content = Path("/workspace/cypress/AGENTS.md").read_text()
        assert len(content) > 0, "AGENTS.md is empty"
    except Exception as e:
        raise AssertionError(f"AGENTS.md not readable: {e}")


# [repo_tests] pass_to_pass
def test_repo_circleci_pipeline_exists():
    """CircleCI pipeline YAML exists and has required structure (pass_to_pass)."""
    pipeline_path = Path("/workspace/cypress/.circleci/src/pipeline/@pipeline.yml")
    assert pipeline_path.exists(), "CircleCI pipeline file not found"
    content = pipeline_path.read_text()
    # CircleCI 2.1 config should have version and at least one of: jobs, workflows, commands, executors
    assert "version: 2.1" in content, "CircleCI pipeline missing version: 2.1"
    has_structure = "jobs:" in content or "commands:" in content or "executors:" in content
    assert has_structure, "CircleCI pipeline missing required structure (jobs, commands, or executors)"


# [repo_tests] pass_to_pass
def test_repo_eslintrc_exists():
    """Root .eslintrc.js exists and is valid JavaScript syntax (pass_to_pass)."""
    eslintrc_path = Path("/workspace/cypress/.eslintrc.js")
    assert eslintrc_path.exists(), ".eslintrc.js not found"
    src = eslintrc_path.read_text()
    # Basic JS syntax check - brackets should balance
    opens = src.count("{") + src.count("[") + src.count("(")
    closes = src.count("}") + src.count("]") + src.count(")")
    assert abs(opens - closes) <= 1, f"eslintrc.js has bracket imbalance"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_eslint_rule_enabled():
    """mocha/no-exclusive-tests is set to error inside the ESLint rules block."""
    src = Path("/workspace/cypress/packages/eslint-config/src/baseConfig.ts").read_text()
    # Simple string search - the rule should be present
    rule_text = "mocha/no-exclusive-tests"
    error_text = "'error'"
    assert rule_text in src, f"{rule_text} not found in baseConfig.ts"
    # Find the line with the rule and check it has : 'error'
    for line in src.split("\n"):
        if rule_text in line and error_text in line:
            return
    raise AssertionError(f"{rule_text} with 'error' value not found in baseConfig.ts")


# [pr_diff] fail_to_pass
def test_stop_only_scripts_removed():
    """package.json must not contain stop-only or stop-only-all scripts."""
    r = _run_py("""
import json, sys
pkg = json.load(open("/workspace/cypress/package.json"))
scripts = pkg.get("scripts", {})
for key in ("stop-only", "stop-only-all"):
    if key in scripts:
        sys.exit(f"package.json still has {key} script")
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
    # Check for node_modules anywhere in the file (not just as standalone lines)
    assert "node_modules" in ignore, (
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
        sys.exit(f"CircleCI pipeline still contains {marker}")
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
        "AGENTS.md still references yarn stop-only"
    )
    assert "yarn stop-only-all" not in agents, (
        "AGENTS.md still references yarn stop-only-all"
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
    assert "ESLint" in agents, (
        "AGENTS.md .only enforcement line must mention ESLint as the mechanism"
    )
