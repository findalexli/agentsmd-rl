"""
Task: bun-dns-promises-getdefaultresultorder
Repo: oven-sh/bun @ 0ff0065f9e5a34c26bd8d1bede19d4239bb95b55
PR:   28949

Tests for node:dns getDefaultResultOrder fix and promises exports.
All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/bun"
BUN = "bun"
VALID_ORDERS = ["ipv4first", "ipv6first", "verbatim"]


def run_bun_js(src: str, timeout: int = 60) -> tuple[str, str, int]:
    """Run a JS snippet with bun and return (stdout, stderr, exit_code)."""
    r = subprocess.run(
        [BUN, "-e", src],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return r.stdout, r.stderr, r.returncode


def build_bun():
    """Build bun debug binary."""
    r = subprocess.run(
        ["bun", "run", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if r.returncode != 0:
        # Build failed - this is a setup issue, not a test failure
        print(f"Build output: {r.stdout}\n{r.stderr}")
    return r.returncode == 0


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def test_getdefaultresultorder_returns_string_not_function():
    """dns.getDefaultResultOrder() returns a string, not the function object."""
    stdout, stderr, exit_code = run_bun_js("""
        const dns = require("node:dns");
        const v = dns.getDefaultResultOrder();
        console.log(typeof dns.getDefaultResultOrder, typeof v, v);
    """)

    parts = stdout.strip().split(" ")
    assert len(parts) == 3, f"Expected 3 parts in output, got: {stdout}"
    kind, value_type, value = parts

    assert kind == "function", f"Expected typeof dns.getDefaultResultOrder to be 'function', got '{kind}'"
    assert value_type == "string", f"Expected return type to be 'string', got '{value_type}'. Bug: returning function object instead of calling it"
    assert value in VALID_ORDERS, f"Expected value to be one of {VALID_ORDERS}, got '{value}'"
    assert exit_code == 0, f"Process exited with code {exit_code}, stderr: {stderr}"


def test_promises_getdefaultresultorder_exists():
    """dns.promises.getDefaultResultOrder is a function returning a string."""
    stdout, stderr, exit_code = run_bun_js("""
        const dns = require("node:dns");
        const v = dns.promises.getDefaultResultOrder();
        console.log(typeof dns.promises.getDefaultResultOrder, typeof v, v);
    """)

    parts = stdout.strip().split(" ")
    assert len(parts) == 3, f"Expected 3 parts in output, got: {stdout}"
    kind, value_type, value = parts

    assert kind == "function", f"Expected typeof dns.promises.getDefaultResultOrder to be 'function', got '{kind}'. Bug: function not exported on promises object"
    assert value_type == "string", f"Expected return type to be 'string', got '{value_type}'"
    assert value in VALID_ORDERS, f"Expected value to be one of {VALID_ORDERS}, got '{value}'"
    assert exit_code == 0, f"Process exited with code {exit_code}, stderr: {stderr}"


def test_promises_getservers_exists():
    """dns.promises.getServers is a function returning an array."""
    stdout, stderr, exit_code = run_bun_js("""
        const dns = require("node:dns");
        console.log(typeof dns.promises.getServers);
        console.log(Array.isArray(dns.promises.getServers()));
    """)

    lines = stdout.strip().split("\n")
    assert len(lines) >= 2, f"Expected 2 lines in output, got: {stdout}"

    func_type = lines[0]
    is_array = lines[1]

    assert func_type == "function", f"Expected typeof dns.promises.getServers to be 'function', got '{func_type}'. Bug: function not exported on promises object"
    assert is_array == "true", f"Expected dns.promises.getServers() to return an array, got isArray={is_array}"
    assert exit_code == 0, f"Process exited with code {exit_code}, stderr: {stderr}"


def test_shared_state_consistency():
    """dns and dns.promises share the same default result order state."""
    stdout, stderr, exit_code = run_bun_js("""
        const dns = require("node:dns");
        const dnsp = require("node:dns/promises");

        // Set via dns, read from both
        dns.setDefaultResultOrder("ipv4first");
        console.log(dns.getDefaultResultOrder());
        console.log(dns.promises.getDefaultResultOrder());
        console.log(dnsp.getDefaultResultOrder());

        // Set via dns.promises, read from dns
        dnsp.setDefaultResultOrder("verbatim");
        console.log(dns.getDefaultResultOrder());
        console.log(dnsp.getDefaultResultOrder());
    """)

    lines = stdout.strip().split("\n")
    assert len(lines) >= 5, f"Expected at least 5 lines in output, got: {stdout}"

    # First set: all should be ipv4first
    assert lines[0] == "ipv4first", f"Expected 'ipv4first', got '{lines[0]}'"
    assert lines[1] == "ipv4first", f"Expected 'ipv4first' from dns.promises, got '{lines[1]}'. Bug: state not shared"
    assert lines[2] == "ipv4first", f"Expected 'ipv4first' from node:dns/promises, got '{lines[2]}'. Bug: state not shared"

    # Second set: all should be verbatim
    assert lines[3] == "verbatim", f"Expected 'verbatim', got '{lines[3]}'"
    assert lines[4] == "verbatim", f"Expected 'verbatim' from node:dns/promises, got '{lines[4]}'. Bug: state not shared"

    assert exit_code == 0, f"Process exited with code {exit_code}, stderr: {stderr}"
