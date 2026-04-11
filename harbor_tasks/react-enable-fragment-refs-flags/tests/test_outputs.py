"""
Task: react-enable-fragment-refs-flags
Repo: facebook/react @ a74302c02d220e3663fcad5836cb90607fc2d006
PR:   36026

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"

# Relative paths (for Node.js runtime evaluation)
MAIN_FLAGS_REL       = "packages/shared/ReactFeatureFlags.js"
NATIVE_OSS_FLAGS_REL = "packages/shared/forks/ReactFeatureFlags.native-oss.js"
TEST_RENDERER_REL    = "packages/shared/forks/ReactFeatureFlags.test-renderer.js"
TEST_WWW_REL         = "packages/shared/forks/ReactFeatureFlags.test-renderer.www.js"

# Absolute paths (for file-reading structural tests)
MAIN_FLAGS       = Path(f"{REPO}/{MAIN_FLAGS_REL}")
NATIVE_OSS_FLAGS = Path(f"{REPO}/{NATIVE_OSS_FLAGS_REL}")
TEST_RENDERER    = Path(f"{REPO}/{TEST_RENDERER_REL}")
TEST_WWW         = Path(f"{REPO}/{TEST_WWW_REL}")

# Node.js script: strips Flow types, evaluates flag file in vm sandbox, checks value
_EVAL_SCRIPT = r'''
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const [,, relPath, flagName, expectedStr] = process.argv;
const expected = expectedStr === 'true';

let src = fs.readFileSync(path.resolve(relPath), 'utf8');

// Step 1: Strip all import lines (Flow type imports and value imports)
src = src.replace(/^import\s+.+$/gm, '');

// Step 2: Strip Flow type annotations
src = src.replace(/:\s*boolean\s*=/g, ' =');
src = src.replace(/:\s*number\s*=/g, ' =');

// Step 3: Convert 'export const X = V' to 'var X = V' (for function scope)
src = src.replace(/export\s+const\s+(\w+)\s*=/g, 'var $1 =');

// Step 4: Handle plain 'export' lines
src = src.replace(/^export\s+.+$/gm, '');

// Step 5: Remove trailing comments
src = src.replace(/\/\/.*$/gm, '');

// Step 6: Remove Flow cast expressions like "((((null: any): ExportsType): FeatureFlagsType): ExportsType);"
src = src.replace(/\({4,}\s*null\s*:\s*any\s*\)\s*:\s*\w+Type\s*\)\s*:\s*\w+Type\s*\)\s*:\s*\w+Type\s*\);?/g, '');
src = src.replace(/\(+\s*null\s*:\s*any\s*\)\s*[^;]*;/g, '');

// Step 7: Wrap in IIFE to handle variable dependencies
src = `(function() {\n${src}\nreturn ${flagName};\n})()`;

// Create sandbox with all magic constants defined
const sandbox = {
  __VARIANT__: '__VARIANT__',
  __EXPERIMENTAL__: false,
  __PROFILE__: false
};

try {
  const result = vm.runInNewContext(src, sandbox);
  if (result !== expected) {
    console.error(flagName + ': expected ' + expected + ', got ' + result);
    process.exit(1);
  }
  console.log('PASS: ' + flagName + ' = ' + result);
} catch (e) {
  console.error('Eval error:', e.message);
  process.exit(2);
}
'''


def _check_flag_runtime(rel_path: str, flag_name: str, expected: bool) -> subprocess.CompletedProcess:
    """Use Node.js vm module to evaluate a flag file and check a flag's runtime value."""
    script = Path(REPO) / "_eval_flags.cjs"
    script.write_text(_EVAL_SCRIPT)
    try:
        return subprocess.run(
            ["node", str(script), rel_path, flag_name, str(expected).lower()],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence / syntax
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_required_files_exist():
    """All 4 feature flag files must be present and have export const syntax."""
    for f in [MAIN_FLAGS, NATIVE_OSS_FLAGS, TEST_RENDERER, TEST_WWW]:
        assert f.exists(), f"Required file missing: {f}"
        assert "export const" in f.read_text(), f"File missing export syntax: {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core flag values verified via Node.js runtime eval
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_main_instance_handles_enabled():
    """enableFragmentRefsInstanceHandles evaluates to true at runtime in ReactFeatureFlags.js (was false)."""
    r = _check_flag_runtime(MAIN_FLAGS_REL, "enableFragmentRefsInstanceHandles", True)
    assert r.returncode == 0, f"Flag check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_native_oss_instance_handles_enabled():
    """enableFragmentRefsInstanceHandles evaluates to true at runtime in native-oss.js (was false)."""
    r = _check_flag_runtime(NATIVE_OSS_FLAGS_REL, "enableFragmentRefsInstanceHandles", True)
    assert r.returncode == 0, f"Flag check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_native_oss_text_nodes_enabled():
    """enableFragmentRefsTextNodes evaluates to true at runtime in native-oss.js (was false)."""
    r = _check_flag_runtime(NATIVE_OSS_FLAGS_REL, "enableFragmentRefsTextNodes", True)
    assert r.returncode == 0, f"Flag check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_test_renderer_instance_handles_enabled():
    """enableFragmentRefsInstanceHandles evaluates to true at runtime in test-renderer.js (was false)."""
    r = _check_flag_runtime(TEST_RENDERER_REL, "enableFragmentRefsInstanceHandles", True)
    assert r.returncode == 0, f"Flag check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_www_all_fragment_flags_enabled():
    """All 4 fragment ref flags evaluate to true at runtime in test-renderer.www.js (all were false)."""
    flags = [
        "enableFragmentRefs",
        "enableFragmentRefsScrollIntoView",
        "enableFragmentRefsInstanceHandles",
        "enableFragmentRefsTextNodes",
    ]
    for flag in flags:
        r = _check_flag_runtime(TEST_WWW_REL, flag, True)
        assert r.returncode == 0, f"{flag} check failed: {r.stderr}"
        assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural consistency
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_duplicate_flag_definitions():
    """Each fragment ref flag must be defined at most once per file."""
    flags = [
        "enableFragmentRefs",
        "enableFragmentRefsScrollIntoView",
        "enableFragmentRefsInstanceHandles",
        "enableFragmentRefsTextNodes",
    ]
    for f in [MAIN_FLAGS, NATIVE_OSS_FLAGS, TEST_RENDERER, TEST_WWW]:
        content = f.read_text()
        for flag in flags:
            count = content.count(f"{flag}:")
            assert count <= 1, f"{flag} defined {count} times in {f.name}"


# [static] pass_to_pass
def test_flag_values_are_boolean_literals():
    """Fragment ref flags must use boolean literal syntax (true/false/__VARIANT__), not expressions."""
    pattern = re.compile(r"enableFragmentRefs\w*\s*:\s*boolean\s*=\s*(.+?);")
    for f in [MAIN_FLAGS, NATIVE_OSS_FLAGS, TEST_RENDERER, TEST_WWW]:
        content = f.read_text()
        for match in pattern.finditer(content):
            value = match.group(1).strip()
            assert value in ("true", "false", "__VARIANT__"), \
                f"Non-literal flag value in {f.name}: {match.group(0)}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .claude/skills/feature-flags/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/feature-flags/SKILL.md:15 @ a74302c02d220e3663fcad5836cb90607fc2d006
def test_instance_handles_in_all_forks():
    """enableFragmentRefsInstanceHandles enabled in ALL fork files at runtime (SKILL.md: 'Add to ALL fork files')."""
    for rel, label in [
        (MAIN_FLAGS_REL, "ReactFeatureFlags.js"),
        (NATIVE_OSS_FLAGS_REL, "native-oss.js"),
        (TEST_RENDERER_REL, "test-renderer.js"),
        (TEST_WWW_REL, "test-renderer.www.js"),
    ]:
        r = _check_flag_runtime(rel, "enableFragmentRefsInstanceHandles", True)
        assert r.returncode == 0, \
            f"enableFragmentRefsInstanceHandles not enabled in {label}: {r.stderr}"
        assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Repo CI pass_to_pass tests — run on both base commit and after gold fix
# ---------------------------------------------------------------------------

def test_repo_lint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_flags():
    """Repo's feature flags check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flags"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Flags check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_version_check():
    """Repo's version check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/version-check.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Version check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_prettier_check():
    """Repo's Prettier formatting check passes (pass_to_pass).
    
    Note: This test may be skipped if the container has insufficient memory,
    as the React prettier check requires significant resources.
    """
    import pytest
    r = subprocess.run(
        ["node", "./scripts/prettier/index.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Skip if out of memory - this is a resource constraint, not a code issue
    if "out of memory" in r.stderr.lower() or "heap" in r.stderr.lower():
        pytest.skip("Prettier check skipped due to container memory constraints")
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_extract_errors():
    """Repo's error codes extraction check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/error-codes/extract-errors.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Extract errors failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
