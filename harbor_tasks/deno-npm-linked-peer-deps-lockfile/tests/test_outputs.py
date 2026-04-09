"""
Task: deno-npm-linked-peer-deps-lockfile
Repo: deno @ dba93738662f4b6ad47356095f230f5be76a7908
PR:   33143

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/deno"
SNAPSHOT_RS = f"{REPO}/libs/npm/resolution/snapshot.rs"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_deno_npm_compiles():
    """The deno_npm crate must compile successfully after changes."""
    r = subprocess.run(
        ["cargo", "check", "-p", "deno_npm"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_raw_key_comparison_for_link_packages():
    """Link package lookup must not compare against raw serialized lockfile key.

    The bug: lockfile keys for packages with peer deps include a suffix
    (e.g. "@myorg/shared@1.0.0_zod@4.3.6"), but link_packages are stored as
    plain "name@version". Comparing the raw key always misses link packages
    that have peer deps.
    """
    content = Path(SNAPSHOT_RS).read_text()

    # The exact bug pattern: link_package_ids.contains(key)
    # where `key` is the raw serialized lockfile key with peer dep suffix
    assert "link_package_ids.contains(key)" not in content, (
        "link_package_ids.contains(key) compares the raw serialized lockfile key "
        "(which includes peer dep suffixes like _zod@4.3.6) against formatted "
        "name@version strings — this mismatch means linked packages with peer "
        "deps are never recognized as linked"
    )


# [pr_diff] fail_to_pass
def test_dist_check_not_using_raw_key():
    """The dist assignment must not use the raw serialized key for link matching.

    The dist field on each package is set to None for linked packages and
    Some(...) for remote packages. The conditional must compare against parsed
    name+version (not the raw lockfile key which includes peer dep suffixes).
    """
    content = Path(SNAPSHOT_RS).read_text()

    # Match the bug pattern: `dist: if !<word>.contains( key )`
    # where `key` is the full serialized lockfile key string.
    # Valid fixes use &id.nv, key_base, or other non-raw-key arguments.
    bug_pattern = re.search(
        r'dist:\s*if\s*!\s*\w+\.contains\(\s*key\s*\)', content
    )
    assert bug_pattern is None, (
        f"Found buggy pattern: {bug_pattern.group()!r} — "
        "the dist check must not compare against the raw serialized key "
        "(it includes peer dep suffixes that won't match link package entries)"
    )


# [pr_diff] fail_to_pass
def test_linked_peer_deps_unit_test_passes():
    """A unit test exercising linked packages with peer dep lockfile keys must pass.

    This verifies the fix actually works at runtime: a linked package whose
    lockfile key has a peer dep suffix (e.g. @myorg/shared@1.0.0_zod@4.3.6)
    should get dist=None in the snapshot (not be treated as a remote package).
    """
    r = subprocess.run(
        ["cargo", "test", "-p", "deno_npm", "--",
         "test_snapshot_from_lockfile_v5_with_linked_package_with_peer_deps"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    # Must actually find and run the test (not 0 matched)
    assert r.returncode == 0, (
        f"Test failed:\nstdout:\n{r.stdout[-1500:]}\nstderr:\n{r.stderr[-1500:]}"
    )
    assert "1 passed" in r.stdout, (
        f"Expected exactly 1 test to pass (test may not exist):\n{r.stdout[-1500:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_snapshot_tests():
    """Pre-existing snapshot unit tests must still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "deno_npm", "--", "snapshot::tests"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"Snapshot tests failed:\nstdout:\n{r.stdout[-2000:]}\n"
        f"stderr:\n{r.stderr[-2000:]}"
    )
