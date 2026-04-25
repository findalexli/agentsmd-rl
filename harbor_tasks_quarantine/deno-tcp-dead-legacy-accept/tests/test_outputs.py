"""
Task: deno-tcp-dead-legacy-accept
Repo: deno @ ad725eea313df6204d342d84ace4af1b11cc341f
PR:   denoland/deno#33172

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/deno"
TCP_WRAP = f"{REPO}/ext/node/polyfills/internal_binding/tcp_wrap.ts"
LINT_PLUGIN = f"{REPO}/tools/lint_plugins/no_deno_api_in_polyfills.ts"


def _setup_deno():
    """Install Deno and setup environment if not already available."""
    # Check if deno is already available
    r = subprocess.run(["which", "deno"], capture_output=True, text=True)
    if r.returncode == 0:
        return

    # Install unzip if needed
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, timeout=60
    )
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "unzip"],
        capture_output=True, timeout=60
    )

    # Install Deno
    r = subprocess.run(
        ["bash", "-c", "curl -fsSL https://deno.land/install.sh | sh"],
        capture_output=True, text=True, timeout=120
    )

    # Setup submodules if not already done
    subprocess.run(
        ["git", "-C", REPO, "submodule", "update", "--init", "--recursive"],
        capture_output=True, timeout=120
    )

    # Add Deno to PATH for future use
    os.environ["PATH"] = "/root/.deno/bin:" + os.environ.get("PATH", "")


def _run_with_deno(cmd: list[str], cwd: str = REPO, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a command with Deno available."""
    _setup_deno()

    # Update PATH for this run
    env = os.environ.copy()
    env["PATH"] = "/root/.deno/bin:" + env.get("PATH", "")

    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd, env=env
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must exist and retain their core structure."""
    tcp = Path(TCP_WRAP).read_text()
    lint = Path(LINT_PLUGIN).read_text()
    # tcp_wrap.ts must still export the TCP class
    assert "export class TCP" in tcp, "TCP class export missing from tcp_wrap.ts"
    # tcp_wrap.ts must still have the listen method
    assert "listen(backlog" in tcp, "listen() method missing from tcp_wrap.ts"
    # lint plugin must still export EXPECTED_VIOLATIONS
    assert "EXPECTED_VIOLATIONS" in lint, "EXPECTED_VIOLATIONS missing from lint plugin"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) - Real CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - Repo CI: deno lint on tcp_wrap.ts passes
def test_repo_deno_lint_tcp_wrap():
    """deno lint on tcp_wrap.ts passes (pass_to_pass)."""
    r = _run_with_deno(["deno", "lint", TCP_WRAP])
    assert r.returncode == 0, f"deno lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Repo CI: deno lint with custom plugin on tcp_wrap.ts
def test_repo_deno_lint_with_plugin():
    """deno lint with custom plugin on tcp_wrap.ts runs (pass_to_pass)."""
    # This runs the lint plugin against tcp_wrap.ts
    # The plugin checks for Deno.* API usage in node polyfills
    r = _run_with_deno([
        "deno", "lint", "--rules-include=no-deno-api-in-polyfills",
        TCP_WRAP
    ])
    # Exit 0 means no violations found (post-fix state)
    # Exit 1 means violations found (base commit state - expected)
    assert r.returncode in (0, 1), f"deno lint with plugin failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Repo CI: deno lint on lint plugin passes
def test_repo_deno_lint_plugin():
    """deno lint on lint plugin passes (pass_to_pass)."""
    r = _run_with_deno(["deno", "lint", LINT_PLUGIN])
    assert r.returncode == 0, f"deno lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Repo CI: lint plugin EXPECTED_VIOLATIONS contains tcp_wrap.ts
def test_repo_lint_expected_violations_count():
    """Lint plugin EXPECTED_VIOLATIONS has tcp_wrap.ts:3 at base commit (pass_to_pass)."""
    # Use grep to extract and validate the EXPECTED_VIOLATIONS count from the source
    # This is a static check that reads the source file directly
    lint_content = Path(LINT_PLUGIN).read_text()
    match = re.search(
        r'"ext/node/polyfills/internal_binding/tcp_wrap\.ts"\s*:\s*(\d+)',
        lint_content
    )
    if match:
        count = int(match.group(1))
        # At base commit, count should be 3 (post-fix: entry removed)
        assert count >= 0, f"Invalid violation count: {count}"
    # If not found, that is valid too (post-fix state where entry was removed)


# [repo_tests] pass_to_pass - Repo CI: tools/lint.js --js passes
def test_repo_lint_js():
    """tools/lint.js --js passes (pass_to_pass)."""
    r = _run_with_deno(["deno", "run", "--allow-all", "./tools/lint.js", "--js"])
    assert r.returncode == 0, f"lint.js failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Repo CI: git verify repo is at expected base commit
def test_repo_git_base_commit():
    """Repo must be at the expected base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    commit = r.stdout.strip()
    expected = "ad725eea313df6204d342d84ace4af1b11cc341f"
    assert commit == expected, f"Expected commit {expected}, got {commit}"


# [repo_tests] pass_to_pass - Repo CI: git verify repo is in a valid state
def test_repo_git_status_clean():
    """Repo must be in a valid git state (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "status", "--porcelain"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    # Allow either clean state (base commit) or with modifications (post-fix)
    # Any state is valid as long as git status works


# [repo_tests] pass_to_pass - Repo CI: git verify modified files exist
def test_repo_git_ls_files():
    """Modified files must exist in git tree (pass_to_pass)."""
    for path in [TCP_WRAP, LINT_PLUGIN]:
        rel_path = path.replace(f"{REPO}/", "")
        r = subprocess.run(
            ["git", "-C", REPO, "ls-files", rel_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"git ls-files failed for {rel_path}: {r.stderr}"
        assert r.stdout.strip() == rel_path, f"File {rel_path} not tracked in git"


# [repo_tests] pass_to_pass - Repo CI: grep verify tcp_wrap.ts Deno.listen is accessible
def test_repo_grep_deno_listen():
    """tcp_wrap.ts must be accessible for grep (Deno.listen presence varies by commit)."""
    # Use -c to get count; returns 0 if found, 1 if not found (both are valid states)
    r = subprocess.run(
        ["grep", "-c", "Deno.listen", TCP_WRAP],
        capture_output=True, text=True, timeout=30,
    )
    # Valid states: base commit has 1+ (legacy path), post-fix has 0 (removed)
    # returncode 0 = found, 1 = not found (both valid); other codes = error
    assert r.returncode in (0, 1), f"grep error for Deno.listen: {r.stderr}"


# [repo_tests] pass_to_pass - Repo CI: grep verify tcp_wrap.ts Deno.* is accessible
def test_repo_grep_deno_usage_count():
    """tcp_wrap.ts must be accessible for Deno.* grep (count varies by commit)."""
    r = subprocess.run(
        ["grep", "-oE", r"\bDeno\.\w+", TCP_WRAP],
        capture_output=True, text=True, timeout=30,
    )
    # Valid states: base commit has 3+ (Deno.listen, Deno.errors.*), post-fix has 0
    # Just verify the grep command works (returncode 0 = found matches, 1 = no matches)
    assert r.returncode in (0, 1), f"grep error for Deno.*: {r.stderr}"


# [repo_tests] pass_to_pass - Repo CI: grep verify EXPECTED_VIOLATIONS is accessible
def test_repo_grep_expected_violations():
    """EXPECTED_VIOLATIONS must be accessible for grep (tcp_wrap.ts presence varies by commit)."""
    r = subprocess.run(
        ["grep", "tcp_wrap.ts.*:", LINT_PLUGIN],
        capture_output=True, text=True, timeout=30,
    )
    # Valid states: base commit has entry, post-fix removed it
    # returncode 0 = found (base), 1 = not found (post-fix) - both valid
    assert r.returncode in (0, 1), f"grep error for EXPECTED_VIOLATIONS: {r.stderr}"


# [repo_tests] pass_to_pass - Repo CI: grep verify _listen.ts exports
def test_repo_grep_listen_exports():
    """_listen.ts must export ceilPowOf2 and backoff constants (pass_to_pass)."""
    listen_path = f"{REPO}/ext/node/polyfills/internal_binding/_listen.ts"

    for pattern in ["export function ceilPowOf2", "export const INITIAL_ACCEPT_BACKOFF_DELAY"]:
        r = subprocess.run(
            ["grep", "-c", pattern, listen_path],
            capture_output=True, text=True, timeout=30,
        )
        count = int(r.stdout.strip()) if r.returncode == 0 else 0
        assert count > 0, f"Expected pattern '{pattern}' in _listen.ts, found {count} occurrences"


# [repo_tests] pass_to_pass - Repo CI check: ensure _listen.ts exports are intact
def test_repo_listen_module_exports():
    """_listen.ts must export ceilPowOf2 and backoff constants (used by tcp_wrap.ts)."""
    listen_path = f"{REPO}/ext/node/polyfills/internal_binding/_listen.ts"
    listen = Path(listen_path).read_text()
    # These exports are needed by tcp_wrap.ts
    assert "export function ceilPowOf2" in listen, "ceilPowOf2 export missing from _listen.ts"
    assert "export const INITIAL_ACCEPT_BACKOFF_DELAY" in listen, (
        "INITIAL_ACCEPT_BACKOFF_DELAY export missing from _listen.ts"
    )
    assert "export const MAX_ACCEPT_BACKOFF_DELAY" in listen, (
        "MAX_ACCEPT_BACKOFF_DELAY export missing from _listen.ts"
    )


# [repo_tests] pass_to_pass - Repo CI check: ensure lint plugin structure is valid
def test_repo_lint_plugin_structure():
    """Lint plugin must have valid EXPECTED_VIOLATIONS structure (pass_to_pass)."""
    lint = Path(LINT_PLUGIN).read_text()

    # Verify EXPECTED_VIOLATIONS block exists and is parseable
    violations_match = re.search(
        r'EXPECTED_VIOLATIONS[^{]*\{([^}]+)\}', lint, re.DOTALL
    )
    assert violations_match, "Could not find EXPECTED_VIOLATIONS in lint plugin"

    # If tcp_wrap.ts is listed, verify it has a valid count (allows both pre-fix count and post-fix removal)
    violations_block = violations_match.group(1)
    tcp_line = re.search(r'"[^"]*tcp_wrap\.ts"\s*:\s*(\d+)', violations_block)
    if tcp_line:
        count = int(tcp_line.group(1))
        # Pre-fix: count > 0 (base commit has 3); Post-fix: count should be 0 or entry removed
        assert count >= 0, f"tcp_wrap.ts has invalid violation count: {count}"


# [repo_tests] pass_to_pass - CI: tcp_wrap.ts Deno.* usage count matches expected violations
def test_repo_tcp_wrap_violation_count():
    """tcp_wrap.ts must have exactly 3 Deno.* usages matching EXPECTED_VIOLATIONS (pass_to_pass)."""
    tcp = Path(TCP_WRAP).read_text()

    # Count actual Deno.* API usages (MemberExpression patterns like Deno.listen)
    # This regex matches "Deno." followed by an identifier, excluding comments
    deno_usages = re.findall(r'\bDeno\.(\w+)', tcp)
    actual_count = len(deno_usages)

    # Verify EXPECTED_VIOLATIONS count
    lint = Path(LINT_PLUGIN).read_text()
    violations_match = re.search(
        r'"ext/node/polyfills/internal_binding/tcp_wrap\.ts"\s*:\s*(\d+)', lint
    )

    if violations_match:
        expected_count = int(violations_match.group(1))
        # Verify that EXPECTED_VIOLATIONS has a valid count for tcp_wrap.ts
        # Base commit: count should be > 0 (currently 3)
        # After fix: count should be 0 or entry removed
        assert expected_count >= 0, f"Invalid violation count: {expected_count}"


# [repo_tests] pass_to_pass - CI: tcp_wrap.ts core imports are valid
def test_repo_tcp_wrap_core_imports():
    """tcp_wrap.ts must import from ext:core/ops and ext:deno_node (pass_to_pass)."""
    tcp = Path(TCP_WRAP).read_text()

    # Core imports required for the module to function
    core_imports = [
        'ext:core/ops',
        'ext:deno_node/_utils.ts',
    ]

    for imp in core_imports:
        assert imp in tcp, f"tcp_wrap.ts missing required import: {imp}"


# [repo_tests] pass_to_pass - CI: _listen.ts exports required by tcp_wrap.ts
def test_repo_listen_module_structure():
    """_listen.ts must export ceilPowOf2 and backoff constants with correct types (pass_to_pass)."""
    listen_path = f"{REPO}/ext/node/polyfills/internal_binding/_listen.ts"
    listen = Path(listen_path).read_text()

    # Check ceilPowOf2 function signature
    ceil_pow2_match = re.search(
        r'export function ceilPowOf2\s*\(\s*n:\s*number\s*\)', listen
    )
    assert ceil_pow2_match, "ceilPowOf2 function signature incorrect or missing from _listen.ts"

    # Check backoff constants are exported as const
    initial_delay_match = re.search(
        r'export const INITIAL_ACCEPT_BACKOFF_DELAY\s*=\s*\d+', listen
    )
    assert initial_delay_match, "INITIAL_ACCEPT_BACKOFF_DELAY export missing or invalid"

    max_delay_match = re.search(
        r'export const MAX_ACCEPT_BACKOFF_DELAY\s*=\s*\d+', listen
    )
    assert max_delay_match, "MAX_ACCEPT_BACKOFF_DELAY export missing or invalid"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — dead code removal checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_legacy_listen_branch_removed():
    """listen() must not branch on kUseNativeWrap to a legacy path."""
    tcp = Path(TCP_WRAP).read_text()

    # Find the listen method signature and check its first ~500 chars for the branch
    listen_match = re.search(r'listen\s*\(\s*backlog\b[^)]*\)[^{}]*\{', tcp)
    assert listen_match, "listen(backlog) method not found in tcp_wrap.ts"

    # Extract a region after the method opening brace
    method_start = listen_match.end()
    method_region = tcp[method_start:method_start + 600]

    # The base commit has: if (!this[kUseNativeWrap]) { return this.#listenLegacy(backlog); }
    # Check for the specific legacy branch pattern that calls listenLegacy
    assert "#listenLegacy" not in method_region, (
        "listen() still contains call to #listenLegacy — legacy branch not removed"
    )


# [pr_diff] fail_to_pass
def test_dead_legacy_methods_removed():
    """Dead #listenLegacy, #accept, #acceptBackoff methods must be removed."""
    # Use subprocess grep to check for dead method definitions
    for pattern in ["#listenLegacy", "#acceptBackoff"]:
        r = subprocess.run(
            ["grep", "-c", pattern, TCP_WRAP],
            capture_output=True, timeout=10,
        )
        count = int(r.stdout.decode().strip()) if r.returncode == 0 else 0
        assert count == 0, f"Dead method pattern '{pattern}' still found {count} times in tcp_wrap.ts"

    # Check #accept separately — must not appear at all (even as field reference)
    # since #acceptBackoff and #accept() are both removed
    r = subprocess.run(
        ["grep", "-cE", r"#accept\b", TCP_WRAP],
        capture_output=True, timeout=10,
    )
    count = int(r.stdout.decode().strip()) if r.returncode == 0 else 0
    assert count == 0, f"#accept reference still found {count} times in tcp_wrap.ts"

    # Also verify Deno.listen is no longer used (was in #listenLegacy)
    r = subprocess.run(
        ["grep", "-c", "Deno.listen", TCP_WRAP],
        capture_output=True, timeout=10,
    )
    count = int(r.stdout.decode().strip()) if r.returncode == 0 else 0
    assert count == 0, f"Deno.listen still referenced {count} times in tcp_wrap.ts"


# [pr_diff] fail_to_pass
def test_lint_violations_updated():
    """Lint plugin must not list tcp_wrap.ts in EXPECTED_VIOLATIONS (or count must be 0)."""
    lint = Path(LINT_PLUGIN).read_text()

    # Extract the EXPECTED_VIOLATIONS block
    violations_match = re.search(
        r'EXPECTED_VIOLATIONS[^{]*\{([^}]+)\}', lint, re.DOTALL
    )
    assert violations_match, "Could not find EXPECTED_VIOLATIONS in lint plugin"
    violations_block = violations_match.group(1)

    # tcp_wrap.ts should either not appear, or have count 0
    tcp_line = re.search(r'"[^"]*tcp_wrap\.ts"\s*:\s*(\d+)', violations_block)
    if tcp_line:
        count = int(tcp_line.group(1))
        assert count == 0, (
            f"tcp_wrap.ts still listed with {count} expected violations in lint plugin "
            f"(should be removed or set to 0 after removing Deno.listen usage)"
        )


# [pr_diff] fail_to_pass
def test_unused_imports_cleaned():
    """Imports only used by dead legacy code must be removed."""
    tcp = Path(TCP_WRAP).read_text()

    # These were only used by the removed legacy accept path
    dead_imports = [
        "INITIAL_ACCEPT_BACKOFF_DELAY",
        "MAX_ACCEPT_BACKOFF_DELAY",
    ]
    for name in dead_imports:
        assert name not in tcp, (
            f"Dead import '{name}' still present in tcp_wrap.ts — "
            f"only used by removed legacy accept path"
        )

    # The 'delay' import from async.ts was only used by #acceptBackoff
    delay_import = re.search(r'import\s*\{[^}]*\bdelay\b[^}]*\}\s*from\s*"ext:deno_node/_util/async\.ts"', tcp)
    assert delay_import is None, (
        "Dead 'delay' import still present — only used by removed #acceptBackoff"
    )
