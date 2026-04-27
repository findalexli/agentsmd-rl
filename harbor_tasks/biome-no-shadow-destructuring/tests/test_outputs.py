"""Verifies the noShadow rule correctly handles destructuring patterns.

The fail-to-pass tests run cargo's snapshot tests for two pre-placed
fixtures (invalidDestructuring.js and validDestructuring.js). On the base
commit those fixtures generate either no diagnostics or wrong diagnostics
that don't match the snapshots, so insta panics. After the fix, the
diagnostics match.

The pass-to-pass tests verify the rule's existing behavior (the original
valid.js / invalid.js fixtures + a TS fixture) still passes.
"""
import subprocess
from pathlib import Path

REPO = Path("/workspace/biome")


def _cargo_test(filter_arg: str, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run a single cargo test by name filter inside biome_js_analyze.

    The test bins are pre-built in the Docker image. After the agent edits
    no_shadow.rs, the rebuild is incremental (a few seconds for a
    single-crate change).
    """
    return subprocess.run(
        [
            "cargo", "test",
            "-p", "biome_js_analyze",
            "--test", "spec_tests",
            "--",
            "--exact",
            filter_arg,
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# -------- Fail-to-pass: destructuring detection --------

def test_invalid_destructuring_detected():
    """
    On base commit: the rule does not flag bindings inside destructuring
    patterns in sibling/child scopes, so invalidDestructuring.js produces
    no diagnostics, but the snapshot expects 7 noShadow diagnostics ->
    insta panics.

    After the fix: the rule walks through binding pattern declarations and
    correctly reports each shadowed binding -> matches snapshot.
    """
    r = _cargo_test("specs::nursery::no_shadow::invalid_destructuring_js")
    assert r.returncode == 0, (
        f"invalidDestructuring spec failed:\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )
    # Sanity check: the test was actually executed (not filtered to zero).
    assert "1 passed" in r.stdout or "test result: ok" in r.stdout, (
        f"Expected 'invalid_destructuring' test to be executed.\n{r.stdout[-1500:]}"
    )


def test_valid_destructuring_not_flagged():
    """
    On base commit: the rule treats destructured bindings as non-
    declarations, so on validDestructuring.js (which uses destructuring in
    sibling if/else branches) it incorrectly emits diagnostics — the
    snapshot says no diagnostics -> mismatch -> panic.

    After the fix: no diagnostics emitted for sibling-scope destructuring
    -> matches snapshot.
    """
    r = _cargo_test("specs::nursery::no_shadow::valid_destructuring_js")
    assert r.returncode == 0, (
        f"validDestructuring spec failed:\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )
    assert "1 passed" in r.stdout or "test result: ok" in r.stdout, (
        f"Expected 'valid_destructuring' test to be executed.\n{r.stdout[-1500:]}"
    )


# -------- Pass-to-pass: regression coverage from the repo's own tests --------

def test_existing_no_shadow_invalid_still_passes():
    """The rule's existing invalid.js fixture must still report shadows."""
    r = _cargo_test("specs::nursery::no_shadow::invalid_js")
    assert r.returncode == 0, (
        f"existing noShadow/invalid.js regressed:\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )


def test_existing_no_shadow_valid_still_passes():
    """The rule's existing valid.js fixture must remain quiet."""
    r = _cargo_test("specs::nursery::no_shadow::valid_js")
    assert r.returncode == 0, (
        f"existing noShadow/valid.js regressed:\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )


def test_existing_no_shadow_valid_func_in_type_still_passes():
    """The TypeScript-flavoured valid fixture must remain quiet."""
    r = _cargo_test("specs::nursery::no_shadow::valid_func_in_type_ts")
    assert r.returncode == 0, (
        f"existing noShadow/valid-func-in-type.ts regressed:\n"
        f"STDOUT (tail):\n{r.stdout[-2000:]}\n"
        f"STDERR (tail):\n{r.stderr[-1500:]}"
    )
