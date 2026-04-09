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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — dead code removal checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_legacy_listen_branch_removed():
    """listen() must not branch on kUseNativeWrap to a legacy path."""
    tcp = Path(TCP_WRAP).read_text()

    # Find the listen method signature and check its first ~500 chars for the branch
    listen_match = re.search(r'listen\s*\(\s*backlog\b[^)]*\)[^{]*\{', tcp)
    assert listen_match, "listen(backlog) method not found in tcp_wrap.ts"

    # Extract a region after the method opening brace
    method_start = listen_match.end()
    method_region = tcp[method_start:method_start + 600]

    # The base commit has: if (!this[kUseNativeWrap]) { return this.#listenLegacy(backlog); }
    assert "kUseNativeWrap" not in method_region, (
        "listen() still contains kUseNativeWrap conditional — legacy branch not removed"
    )
    assert "#listenLegacy" not in method_region, (
        "listen() still references #listenLegacy"
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
