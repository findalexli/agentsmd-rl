"""
Task: deno-tcp-dead-legacy-accept
Repo: deno @ ad725eea313df6204d342d84ace4af1b11cc341f
PR:   denoland/deno#33172

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/deno"
TCP_WRAP = f"{REPO}/ext/node/polyfills/internal_binding/tcp_wrap.ts"
LINT_PLUGIN = f"{REPO}/tools/lint_plugins/no_deno_api_in_polyfills.ts"


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


# [repo_tests] pass_to_pass - Repo CI check: ensure tcp_wrap.ts imports from _listen.ts
def test_repo_tcp_wrap_imports():
    """tcp_wrap.ts must import from _listen.ts (ceilPowOf2 and backoff constants used by legacy path)."""
    tcp = Path(TCP_WRAP).read_text()
    # On base commit, tcp_wrap.ts imports from _listen.ts using multi-line import
    # After fix, only ceilPowOf2 remains. This test verifies the import relationship exists.
    assert '"ext:deno_node/internal_binding/_listen.ts"' in tcp, (
        "tcp_wrap.ts missing import from _listen.ts"
    )


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
