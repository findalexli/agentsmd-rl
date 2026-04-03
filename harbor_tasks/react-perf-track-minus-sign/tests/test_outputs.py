"""
Task: react-perf-track-minus-sign
Repo: facebook/react @ ff191f24b5f49252672ac4d3c46ef1e79cf7290d
PR:   35649

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/react"
TARGET_FILE = Path(REPO) / "packages/shared/ReactPerformanceTrackProperties.js"


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
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, (
        f"Failed to eval {name}: {r.stderr.decode()}"
    )
    return r.stdout.decode().strip()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """ReactPerformanceTrackProperties.js must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", str(TARGET_FILE)],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_removed_constant_uses_minus_sign():
    """REMOVED constant first character must be ASCII minus sign '-' (U+002D, codepoint 45)."""
    codepoints = _eval_js_constant("REMOVED")
    first_cp = int(codepoints.split(",")[0])
    assert first_cp == 45, (
        f"REMOVED first char codepoint is {first_cp}, expected 45 (ASCII '-'). "
        f"Got codepoints: {codepoints}"
    )


# [pr_diff] fail_to_pass
def test_removed_not_en_dash():
    """REMOVED constant must not contain en dash U+2013 in any form."""
    src = TARGET_FILE.read_text()
    match = re.search(r"^const REMOVED = .+;", src, re.MULTILINE)
    assert match, "Could not find 'const REMOVED' in file"
    line = match.group(0)
    assert "\\u2013" not in line, f"REMOVED uses unicode escape \\u2013 (en dash): {line!r}"
    assert "\u2013" not in line, f"REMOVED contains literal en dash U+2013: {line!r}"


# [pr_diff] fail_to_pass
def test_removed_exact_value():
    """REMOVED constant must be exactly '-\\xa0' (minus + non-breaking space)."""
    codepoints = _eval_js_constant("REMOVED")
    cp_list = [int(x) for x in codepoints.split(",")]
    # Must be exactly [45, 160] = '-' + non-breaking space
    assert cp_list == [45, 160], (
        f"REMOVED should be [45, 160] ('-' + NBSP), got {cp_list}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_prefix_consistency():
    """REMOVED/ADDED/UNCHANGED prefixes are each 2 chars and end with non-breaking space."""
    for name in ("REMOVED", "ADDED", "UNCHANGED"):
        codepoints = _eval_js_constant(name)
        cp_list = [int(x) for x in codepoints.split(",")]
        assert len(cp_list) == 2, (
            f"{name} should be 2 chars, got {len(cp_list)}: {cp_list}"
        )
        assert cp_list[1] == 160, (
            f"{name} second char should be NBSP (160), got {cp_list[1]}"
        )


# [static] pass_to_pass
def test_not_stub():
    """File still defines REMOVED, ADDED, and UNCHANGED constants with non-empty values."""
    src = TARGET_FILE.read_text()
    assert re.search(r"^const REMOVED = '.+';", src, re.MULTILINE), \
        "REMOVED constant missing or empty"
    assert re.search(r"^const ADDED = '.+';", src, re.MULTILINE), \
        "ADDED constant missing or empty"
    assert re.search(r"^const UNCHANGED = '.+';", src, re.MULTILINE), \
        "UNCHANGED constant missing or empty"
