"""
Task: bun-windows-arm64-ci-build-fix
Repo: bun @ cd4459476a5f0af4e45b8594ac88732ba6d79afb
PR:   28922

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified ci.mjs file must parse as valid JavaScript."""
    r = subprocess.run(
        ["node", "--check", f"{REPO}/.buildkite/ci.mjs"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_windows_arm64_uses_bun_runtime():
    """Windows ARM64 target uses bun runtime instead of node --experimental-strip-types."""
    test_script = f"""
const fs = require('fs');
const code = fs.readFileSync('{REPO}/.buildkite/ci.mjs', 'utf8');
if (!code.includes('target.os === "windows" && target.arch === "aarch64"')) {{
    console.error('Runtime selection logic not found');
    process.exit(1);
}}
if (!code.includes('? "bun" : "node --experimental-strip-types"')) {{
    console.error('Ternary runtime selection not found');
    process.exit(1);
}}
const buildCommandMatch = code.match(/function getBuildCommand[\\s\\S]*?return `\\$\\{{runtime\\}} scripts/);
if (!buildCommandMatch) {{
    console.error('getBuildCommand function does not use runtime variable in return');
    process.exit(1);
}}
console.log('Windows ARM64 runtime fix verified');
process.exit(0);
"""
    r = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Windows ARM64 test failed: {r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_skip_size_check_option_parsed():
    ci_mjs = Path(f"{REPO}/.buildkite/ci.mjs").read_text()
    assert "skipSizeCheck" in ci_mjs, "skipSizeCheck not found in ci.mjs"
    assert "skip size" in ci_mjs.lower() or "skip-size-check" in ci_mjs.lower(), \
        "skip size check regex pattern not found"
    assert "options.skipSizeCheck" in ci_mjs, "options.skipSizeCheck usage not found"


# [pr_diff] fail_to_pass
def test_binary_size_step_function_exists():
    ci_mjs = Path(f"{REPO}/.buildkite/ci.mjs").read_text()
    assert "function getBinarySizeStep(" in ci_mjs, "getBinarySizeStep function not found"
    assert 'key: "binary-size"' in ci_mjs, "binary-size key not found"
    assert "bun scripts/binary-size.ts" in ci_mjs, "binary-size.ts command not found"
    assert "depends_on" in ci_mjs, "depends_on property not found"
    assert "threshold-mb" in ci_mjs, "threshold-mb parameter not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    ci_mjs = Path(f"{REPO}/.buildkite/ci.mjs").read_text()
    func_match = __import__('re').search(
        r'function getBuildCommand\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
        ci_mjs
    )
    assert func_match, "Could not find getBuildCommand function"
    func_body = func_match.group(1)
    meaningful_lines = [
        line for line in func_body.split('\n')
        if line.strip()
        and not line.strip().startswith('//')
        and not line.strip().startswith('*')
        and not line.strip().startswith('/*')
    ]
    assert len(meaningful_lines) >= 2, "getBuildCommand function body is too simple (stub-like)"
    assert 'runtime' in func_body, "Function doesn't use runtime variable"


# [static] pass_to_pass
def test_other_platforms_use_node():
    ci_mjs = Path(f"{REPO}/.buildkite/ci.mjs").read_text()
    assert "node --experimental-strip-types" in ci_mjs, \
        "Node runtime option not preserved for other platforms"
    assert '? "bun" : "node --experimental-strip-types"' in ci_mjs or \
           '? "bun" : "node --experimental-strip-types"' in ci_mjs.replace("'", '"'), \
        "Ternary operator for runtime selection not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's JavaScript lint (oxlint) passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "lint"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    install = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert install.returncode == 0, f"bun install failed: {install.stderr}"
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_banned_words():
    """Repo's banned words check passes (pass_to_pass)."""
    install = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert install.returncode == 0, f"bun install failed: {install.stderr}"
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Banned words check failed:\n{r.stderr[-500:]}"
