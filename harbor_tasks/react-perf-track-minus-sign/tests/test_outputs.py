"""
Task: react-perf-track-minus-sign
Repo: facebook/react @ ff191f24b5f49252672ac4d3c46ef1e79cf7290d
PR:   35649

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET_FILE = Path(REPO) / "packages/shared/ReactPerformanceTrackProperties.js"
TEST_FILE = Path(REPO) / "packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js"


def _eval_js_constant(name: str) -> str:
    """Extract and evaluate a JS string constant from TARGET_FILE via node."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const match = src.match(/^const {name} = (.+);/m);
if (!match) {{ console.error('{name} not found'); process.exit(1); }}
const val = eval(match[1]);
// Output each codepoint as decimal, comma-separated
process.stdout.write([...val].map(c => c.codePointAt(0)).join(','));
""", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Failed to eval {name}: {r.stderr}"
    )
    return r.stdout.strip()


def _cp_list(name: str) -> list[int]:
    """Get codepoints of a JS string constant as a list of ints."""
    raw = _eval_js_constant(name)
    return [int(x) for x in raw.split(",")]


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# -----------------------------------------------------------------------------

def test_syntax_check():
    """ReactPerformanceTrackProperties.js must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# -----------------------------------------------------------------------------

def test_removed_constant_uses_minus_sign():
    """REMOVED constant first character must be ASCII minus sign '-' (U+002D, codepoint 45)."""
    cps = _cp_list("REMOVED")
    assert cps[0] == 45, (
        f"REMOVED first char codepoint is {cps[0]}, expected 45 (ASCII '-'). "
        f"Got codepoints: {cps}"
    )


def test_removed_not_en_dash():
    """REMOVED constant must not contain en dash U+2013 in any form."""
    cps = _cp_list("REMOVED")
    assert 8211 not in cps, (
        f"REMOVED contains en dash (U+2013, codepoint 8211). "
        f"Got codepoints: {cps}"
    )


def test_removed_exact_value():
    """REMOVED constant must be exactly '-\xa0' (minus + non-breaking space)."""
    cps = _cp_list("REMOVED")
    assert cps == [45, 160], (
        f"REMOVED should be [45, 160] ('-' + NBSP), got {cps}"
    )


def test_react_performance_track_tests():
    """React PerformanceTrack tests must pass with the correct minus sign."""
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=ReactPerformanceTrack-test", "--no-coverage", "--verbose=false"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"React PerformanceTrack tests failed. stderr:\n{r.stderr}\nstdout:\n{r.stdout}"
    )


# -----------------------------------------------------------------------------
# Pass-to-pass (static) - regression + anti-stub
# -----------------------------------------------------------------------------

def test_prefix_consistency():
    """REMOVED/ADDED/UNCHANGED prefixes are each 2 chars and end with non-breaking space."""
    for name in ("REMOVED", "ADDED", "UNCHANGED"):
        cps = _cp_list(name)
        assert len(cps) == 2, (
            f"{name} should be 2 chars, got {len(cps)}: {cps}"
        )
        assert cps[1] == 160, (
            f"{name} second char should be NBSP (160), got {cps[1]}"
        )


def test_not_stub():
    """File still defines REMOVED, ADDED, and UNCHANGED constants with non-empty values."""
    for name in ("REMOVED", "ADDED", "UNCHANGED"):
        cps = _cp_list(name)
        assert len(cps) >= 1, f"{name} evaluates to empty string"
