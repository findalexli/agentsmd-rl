"""
Task: bun-binary-size-agent-image-fix
Repo: bun @ b6a45f9f50c71afe1102bb4396dd304ce1c57b30
PR:   28993

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
from pathlib import Path

REPO = "/workspace/bun"
TARGET_FILE = ".buildkite/ci.mjs"


def _ensure_bun():
    """Ensure bun is available in PATH, installing if necessary."""
    env = os.environ.copy()
    env["PATH"] = "/usr/local/bin:" + env.get("PATH", "")

    # Check if bun is available
    result = subprocess.run(
        ["which", "bun"],
        capture_output=True,
        env=env,
    )
    if result.returncode != 0:
        # Install bun globally via npm
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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
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

# [pr_diff] fail_to_pass
def test_uses_buildplatforms_find():
    """getBinarySizeStep should use buildPlatforms.find() to get the correct agent config."""
    file_path = Path(f"{REPO}/{TARGET_FILE}")
    content = file_path.read_text()

    # The fix: should use buildPlatforms.find() with the correct platform criteria
    assert "buildPlatforms.find" in content, (
        "Must use buildPlatforms.find() to locate the linux-aarch64-amazonlinux platform"
    )

    # Verify the specific criteria are passed to find()
    assert 'p.os === "linux"' in content, "Must filter by os: linux"
    assert 'p.arch === "aarch64"' in content, "Must filter by arch: aarch64"
    assert 'p.distro === "amazonlinux"' in content, "Must filter by distro: amazonlinux"


# [pr_diff] fail_to_pass
def test_no_handbuilt_platform_object():
    """Should not use hand-built platform object that omits features field."""
    file_path = Path(f"{REPO}/{TARGET_FILE}")
    content = file_path.read_text()

    # Look for getBinarySizeStep function and check it does not have the old pattern
    # The old buggy code had: getEc2Agent({ os: "linux", arch: "aarch64", distro: "amazonlinux", release: "2023" }

    import re

    # Find the getBinarySizeStep function
    func_match = re.search(
        r"function getBinarySizeStep\([^)]*\)\s*\{[\s\S]*?return\s*\{[\s\S]*?\};\s*\}",
        content,
    )
    assert func_match, "Could not find getBinarySizeStep function"

    func_content = func_match.group(0)

    # Should NOT have the hand-built object pattern in the return statement
    handbuilt_pattern = r'\{\s*os:\s*"linux"\s*,\s*arch:\s*"aarch64"\s*,\s*distro:\s*"amazonlinux"\s*,\s*release:\s*"2023"\s*\}'
    assert not re.search(handbuilt_pattern, func_content), (
        "Must NOT use hand-built platform object with os/arch/distro/release - "
        "this omits the features field needed for correct image key generation"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
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

# [static] pass_to_pass
def test_not_stub():
    """getBinarySizeStep function has real implementation, not just a stub."""
    file_path = Path(f"{REPO}/{TARGET_FILE}")
    content = file_path.read_text()

    import re

    # Find the getBinarySizeStep function
    func_match = re.search(
        r"function getBinarySizeStep\([^)]*\)\s*\{[\s\S]*?return\s*\{[\s\S]*?\};\s*\}",
        content,
    )
    assert func_match, "Could not find getBinarySizeStep function - it may have been removed or stubbed"

    func_content = func_match.group(0)

    # Should have the key structure elements
    assert 'key: "binary-size"' in func_content, "Function should define the binary-size step key"
    assert "agents:" in func_content, "Function should define agents configuration"
    assert "getEc2Agent" in func_content, "Function should call getEc2Agent"

    # Function body should have more than minimal content
    lines = [line.strip() for line in func_content.split("\n") if line.strip()]
    assert len(lines) >= 5, f"Function body is too short/stub-like ({len(lines)} lines)"


# [static] pass_to_pass
def test_binary_size_step_structure():
    """getBinarySizeStep returns properly structured step object."""
    file_path = Path(f"{REPO}/{TARGET_FILE}")
    content = file_path.read_text()

    import re

    # Find the return statement within getBinarySizeStep
    func_match = re.search(
        r"function getBinarySizeStep\([^)]*\)\s*\{[\s\S]*?return\s*(\{[\s\S]*?\});\s*\}",
        content,
    )
    assert func_match, "Could not find getBinarySizeStep return statement"

    return_content = func_match.group(1)

    # Check for required step properties
    assert "key:" in return_content, "Step must have a key"
    assert "label:" in return_content, "Step must have a label"
    assert "agents:" in return_content, "Step must have agents"
    assert "depends_on:" in return_content, "Step must have depends_on"
