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
from pathlib import Path

REPO = "/workspace/cypress"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """baseConfig.ts is valid TypeScript (no unclosed braces/brackets)."""
    src = Path(f"{REPO}/packages/eslint-config/src/baseConfig.ts").read_text()
    # Basic bracket balance check — catches most syntax errors
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
    """mocha/no-exclusive-tests must be set to 'error' in ESLint base config."""
    src = Path(f"{REPO}/packages/eslint-config/src/baseConfig.ts").read_text()
    # The rule must appear and be set to error
    assert "mocha/no-exclusive-tests" in src, (
        "baseConfig.ts must include mocha/no-exclusive-tests rule"
    )
    # Check it's set to 'error', not 'off' or 'warn'
    import re
    match = re.search(r"['\"]mocha/no-exclusive-tests['\"]:\s*['\"](\w+)['\"]", src)
    assert match is not None, "Could not parse mocha/no-exclusive-tests rule value"
    assert match.group(1) == "error", (
        f"mocha/no-exclusive-tests should be 'error', got '{match.group(1)}'"
    )


# [pr_diff] fail_to_pass
def test_stop_only_scripts_removed():
    """package.json must not contain stop-only or stop-only-all scripts."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "stop-only" not in scripts, "package.json still has stop-only script"
    assert "stop-only-all" not in scripts, "package.json still has stop-only-all script"


# [pr_diff] fail_to_pass
def test_stop_only_dep_removed():
    """stop-only must not be listed as a devDependency in package.json."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    dev_deps = pkg.get("devDependencies", {})
    assert "stop-only" not in dev_deps, (
        "package.json still lists stop-only as a devDependency"
    )


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — AGENTS.md updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — CI pipeline cleanup
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ci_no_stop_only_step():
    """CircleCI pipeline should not reference the stop-only step."""
    pipeline = Path(f"{REPO}/.circleci/src/pipeline/@pipeline.yml").read_text()
    assert "Stop .only" not in pipeline, (
        "CircleCI pipeline still has the 'Stop .only' step"
    )
    assert "yarn stop-only-all" not in pipeline, (
        "CircleCI pipeline still references yarn stop-only-all"
    )
