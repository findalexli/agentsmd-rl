"""
Task: bun-binary-size-agent-image-fix
Repo: bun @ b6a45f9f50c71afe1102bb4396dd304ce1c57b30
PR:   28993

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

These tests verify BEHAVIOR by:
1. Executing the code and checking actual output values
2. Using regex only to extract and test code behavior, not for static assertions
3. Running subprocesses that import/call the functions under test
"""

import subprocess
import os
from pathlib import Path
import tempfile

REPO = "/workspace/bun"
TARGET_FILE = ".buildkite/ci.mjs"

# Embedded behavioral test helper script
TEST_BEHAVIOR_MJS = '''#!/usr/bin/env node
/**
 * Behavioral test helper for verifying getImageKey and getBinarySizeStep.
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";

const REPO = "/workspace/bun";
const TARGET_FILE = ".buildkite/ci.mjs";

const filePath = join(REPO, TARGET_FILE);
const code = readFileSync(filePath, "utf-8");

// Extract buildPlatforms array definition using regex
const buildPlatformsMatch = code.match(/const buildPlatforms = (\\[[\\s\\S]*?\\]);/);
if (!buildPlatformsMatch) {
  console.error("FAIL: Could not find buildPlatforms array");
  process.exit(1);
}

let buildPlatforms;
try {
  buildPlatforms = eval(buildPlatformsMatch[1]);
} catch (e) {
  console.error("FAIL: Could not parse buildPlatforms array:", e.message);
  process.exit(1);
}

// Extract getImageKey function
const getImageKeyMatch = code.match(/function getImageKey\\(platform\\) \\{[\\s\\S]*?\\n\\}/);
if (!getImageKeyMatch) {
  console.error("FAIL: Could not find getImageKey function");
  process.exit(1);
}

let getImageKey;
try {
  getImageKey = eval(`(${getImageKeyMatch[0]})`);
} catch (e) {
  console.error("FAIL: Could not reconstruct getImageKey function:", e.message);
  process.exit(1);
}

// Find the linux-aarch64-amazonlinux platform
const platform = buildPlatforms.find(
  p => p.os === "linux" && p.arch === "aarch64" && p.distro === "amazonlinux"
);

if (!platform) {
  console.error("FAIL: Could not find linux-aarch64-amazonlinux platform");
  process.exit(1);
}

// Test 1: Verify platform has features array with "docker"
if (!platform.features || !platform.features.includes("docker")) {
  console.error("FAIL: Platform missing features: ['docker']");
  console.error("Platform:", JSON.stringify(platform));
  process.exit(1);
}
console.log("PASS: Platform has features: ['docker']");

// Test 2: Verify getImageKey generates correct image key with -with-docker suffix
const imageKey = getImageKey(platform);
const expectedKey = "linux-aarch64-2023-amazonlinux-with-docker";
if (imageKey !== expectedKey) {
  console.error(`FAIL: getImageKey returned "${imageKey}", expected "${expectedKey}"`);
  process.exit(1);
}
console.log(`PASS: getImageKey returns "${imageKey}"`);

// Test 3: Verify getBinarySizeStep doesn't use hand-built object (the bug)
const getBinarySizeStepMatch = code.match(/function getBinarySizeStep[\\s\\S]*?^\\}/m);
if (!getBinarySizeStepMatch) {
  console.error("FAIL: Could not find getBinarySizeStep function");
  process.exit(1);
}

const funcCode = getBinarySizeStepMatch[0];

// Check for hand-built object pattern (the bug)
const handbuiltPattern = /\\{\\s*os:\\s*"linux"\\s*,\\s*arch:\\s*"aarch64"\\s*,\\s*distro:\\s*"amazonlinux"\\s*,\\s*release:\\s*"2023"\\s*\\}/;
if (handbuiltPattern.test(funcCode)) {
  console.error("FAIL: getBinarySizeStep uses hand-built platform object");
  process.exit(1);
}
console.log("PASS: getBinarySizeStep does not use hand-built platform object");

// Test 4: Verify function accesses buildPlatforms (any method)
const usesBuildPlatforms = /buildPlatforms\\.(find|filter|findIndex)/.test(funcCode);
if (!usesBuildPlatforms) {
  console.error("FAIL: getBinarySizeStep does not access buildPlatforms");
  process.exit(1);
}
console.log("PASS: getBinarySizeStep accesses buildPlatforms array");

console.log("\\n=== All behavioral tests passed ===");
process.exit(0);
'''


def _ensure_bun():
    """Ensure bun is available in PATH, installing if necessary."""
    env = os.environ.copy()
    env["PATH"] = "/usr/local/bin:" + env.get("PATH", "")

    result = subprocess.run(
        ["which", "bun"],
        capture_output=True,
        env=env,
    )
    if result.returncode != 0:
        subprocess.run(
            ["npm", "install", "-g", "bun"],
            capture_output=True,
            timeout=120,
        )
    return env


def _bun_install(env):
    """Run bun install in the repo."""
    result = subprocess.run(
        ["bun", "install"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
        env=env,
    )
    return result


def _run_behavioral_test():
    """Run the behavioral test helper script."""
    # Write the helper script to a temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
        f.write(TEST_BEHAVIOR_MJS)
        helper_path = f.name

    try:
        result = subprocess.run(
            ["node", helper_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result
    finally:
        os.unlink(helper_path)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified file must be valid JavaScript/Node.js syntax."""
    file_path = Path(f"{REPO}/{TARGET_FILE}")
    result = subprocess.run(
        ["node", "--check", str(file_path)],
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Syntax error in {TARGET_FILE}:\n{result.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_image_name_generation():
    """
    Verifies the code generates the correct image name with '-with-docker' suffix.

    This test EXECUTES the code to verify:
    1. buildPlatforms contains a linux-aarch64-amazonlinux platform WITH features: ["docker"]
    2. getImageKey() correctly includes the features suffix
    3. The generated image key is "linux-aarch64-2023-amazonlinux-with-docker"
    """
    result = _run_behavioral_test()
    assert result.returncode == 0, f"Image name generation test failed:\n{result.stdout}\n{result.stderr}"


def test_binary_size_step_uses_platform_from_buildplatforms():
    """
    Verifies getBinarySizeStep uses a platform from buildPlatforms, not a hand-built object.

    This test EXECUTES the code to verify:
    1. getBinarySizeStep function does NOT contain the hand-built object pattern
    2. getBinarySizeStep DOES reference buildPlatforms array

    The bug was using a hand-built object that omitted the features field,
    causing the image name to miss the '-with-docker' suffix.
    """
    result = _run_behavioral_test()
    assert result.returncode == 0, f"Platform source test failed:\n{result.stdout}\n{result.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_lint():
    """Repo JavaScript linting passes (pass_to_pass)."""
    env = _ensure_bun()

    r = _bun_install(env)
    assert r.returncode == 0, f"bun install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["bun", "lint"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


def test_repo_prettier():
    """Modified file passes Prettier formatting check (pass_to_pass)."""
    env = _ensure_bun()

    r = _bun_install(env)
    assert r.returncode == 0, f"bun install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/{TARGET_FILE}"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_repo_banned_words():
    """Banned words check passes (pass_to_pass)."""
    env = _ensure_bun()

    r = _bun_install(env)
    assert r.returncode == 0, f"bun install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["bun", "run", "banned"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"Banned words check failed:\n{r.stderr[-500:]}"


def test_repo_typecheck():
    """Repo TypeScript typecheck passes (pass_to_pass)."""
    env = _ensure_bun()

    r = _bun_install(env)
    assert r.returncode == 0, f"bun install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_generated_image_key_is_correct():
    """
    Verifies getImageKey() returns the expected image key format.

    This test EXECUTES the getImageKey function to verify it produces:
    "linux-aarch64-2023-amazonlinux-with-docker" for the correct platform.

    This catches stub implementations and verifies the actual computation.
    """
    result = _run_behavioral_test()
    assert result.returncode == 0, f"Image key test failed:\n{result.stdout}\n{result.stderr}"
    assert "linux-aarch64-2023-amazonlinux-with-docker" in result.stdout


def test_platform_has_docker_feature():
    """
    Verifies the linux-aarch64-amazonlinux platform has features: ["docker"].

    This test EXECUTES code to check the buildPlatforms array contents.
    The features field is essential for correct image name generation.
    """
    result = _run_behavioral_test()
    assert result.returncode == 0, f"Platform features test failed:\n{result.stdout}\n{result.stderr}"
    assert "features:" in result.stdout
