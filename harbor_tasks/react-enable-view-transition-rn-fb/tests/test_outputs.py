"""
Task: react-enable-view-transition-rn-fb
Repo: facebook/react @ b4546cd0d4db2b913d8e7503bee86e1844073b2e
PR:   36106

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
FLAG_NATIVE_FB = f"{REPO}/packages/shared/forks/ReactFeatureFlags.native-fb.js"
FLAG_TEST_RN = f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js"
FLAG_TEST_WWW = f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js"

# Node.js script that evaluates a feature flag's runtime value from a JS source file.
# Strips Flow import lines and type annotations so the JS engine can evaluate the constants.
_FLAG_EVAL_SCRIPT = r"""
const fs = require('fs');
const flagPath = process.argv[2];
const flagName = process.argv[3];

const src = fs.readFileSync(flagPath, 'utf8');

// Strip Flow import/import-type lines and 'export' keyword,
// then strip Flow type annotations (e.g. ': boolean') from const declarations.
const cleaned = src.split('\n')
  .filter(l => !/^\s*import\s/.test(l))
  .map(l => l.replace(/^export\s+/, ''))
  .map(l => l.replace(/(const\s+\w+)\s*:\s*\w+/g, '$1'))
  .join('\n');

try {
  const fn = new Function(cleaned + '\nreturn ' + flagName + ';');
  const val = fn();
  console.log(JSON.stringify({ flag: flagName, value: val, type: typeof val }));
  process.exit(val === true ? 0 : 1);
} catch (e) {
  console.error('Evaluation error: ' + e.message);
  process.exit(2);
}
"""


def _eval_flag(filepath: str, flag_name: str) -> subprocess.CompletedProcess:
    """Use Node.js to evaluate a feature flag's runtime value from a JS source file."""
    script_path = Path(REPO) / "_eval_flag.cjs"
    script_path.write_text(_FLAG_EVAL_SCRIPT)
    try:
        return subprocess.run(
            ["node", str(script_path), filepath, flag_name],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core flag changes via Node.js evaluation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_enable_view_transition_native_fb():
    """enableViewTransition evaluates to true in ReactFeatureFlags.native-fb.js."""
    r = _eval_flag(FLAG_NATIVE_FB, "enableViewTransition")
    assert r.returncode == 0, (
        f"enableViewTransition is not true in native-fb.js: "
        f"{r.stdout.strip()} {r.stderr.strip()}"
    )
    data = json.loads(r.stdout.strip())
    assert data["value"] is True


# [pr_diff] fail_to_pass
def test_enable_view_transition_test_renderer_native_fb():
    """enableViewTransition evaluates to true in ReactFeatureFlags.test-renderer.native-fb.js."""
    r = _eval_flag(FLAG_TEST_RN, "enableViewTransition")
    assert r.returncode == 0, (
        f"enableViewTransition is not true in test-renderer.native-fb.js: "
        f"{r.stdout.strip()} {r.stderr.strip()}"
    )
    data = json.loads(r.stdout.strip())
    assert data["value"] is True


# [pr_diff] fail_to_pass
def test_enable_view_transition_test_renderer_www():
    """enableViewTransition evaluates to true in ReactFeatureFlags.test-renderer.www.js."""
    r = _eval_flag(FLAG_TEST_WWW, "enableViewTransition")
    assert r.returncode == 0, (
        f"enableViewTransition is not true in test-renderer.www.js: "
        f"{r.stdout.strip()} {r.stderr.strip()}"
    )
    data = json.loads(r.stdout.strip())
    assert data["value"] is True


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub: no collateral flag changes
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_unintended_flag_changes():
    """Other flags remain at their base-commit values — only enableViewTransition was changed."""
    flags_must_stay_false = [
        "enableGestureTransition",
        "enableSuspenseyImages",
        "enableYieldingBeforePassive",
        "enableThrottledScheduling",
    ]
    for filepath in [FLAG_NATIVE_FB, FLAG_TEST_RN, FLAG_TEST_WWW]:
        content = Path(filepath).read_text()
        for flag in flags_must_stay_false:
            m = re.search(
                rf'export const {flag}(?::\s*\w+)?\s*=\s*(\S+?)\s*;', content
            )
            if m:
                actual = m.group(1)
                assert actual == "false", (
                    f"{flag} should remain 'false' in {Path(filepath).name}, "
                    f"found: '{actual}' — only enableViewTransition should be changed"
                )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that should pass on base and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Repo ESLint check
def test_repo_eslint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Shared package tests
def test_repo_shared_package_tests():
    """Shared package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=packages/shared", "--timeout=60"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Shared package tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Feature flags validation
def test_repo_flags_validation():
    """Feature flags validation passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flags"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flags validation failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Agent-config derived (agent_config) — .claude/skills/feature-flags/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/feature-flags/SKILL.md:78 @ b4546cd0d4db2b913d8e7503bee86e1844073b2e
def test_all_fork_files_have_view_transition_enabled():
    """All three fork files must have enableViewTransition enabled (not just one).

    Rule: 'Missing fork files — New flags must be added to ALL fork files, not just the main one'
    Source: .claude/skills/feature-flags/SKILL.md line 78
    """
    files = {
        "native-fb.js": FLAG_NATIVE_FB,
        "test-renderer.native-fb.js": FLAG_TEST_RN,
        "test-renderer.www.js": FLAG_TEST_WWW,
    }
    failures = []
    for name, filepath in files.items():
        r = _eval_flag(filepath, "enableViewTransition")
        if r.returncode != 0:
            failures.append(
                f"{name}: not true ({r.stdout.strip()} {r.stderr.strip()})"
            )
            continue
        data = json.loads(r.stdout.strip())
        if data["value"] is not True:
            failures.append(f"{name}: {data['value']}")

    assert not failures, (
        "enableViewTransition must evaluate to true in ALL fork files. "
        "Failed: " + ", ".join(failures)
    )
