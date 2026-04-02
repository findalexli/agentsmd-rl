"""
Task: react-perf-track-minus-sign
Repo: facebook/react @ ff191f24b5f49252672ac4d3c46ef1e79cf7290d

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/react"
TARGET_FILE = Path(REPO) / "packages/shared/ReactPerformanceTrackProperties.js"


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
    # AST-only because: evaluating the JS constant value is simpler via node eval
    # than importing the ES module; the constant is a plain string literal
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const match = src.match(/^const REMOVED = (.+);/m);
if (!match) { console.error('REMOVED constant not found'); process.exit(1); }
const val = eval(match[1]);
const code = val.codePointAt(0);
process.stdout.write(String(code));
if (code !== 45) { process.exit(1); }
""", str(TARGET_FILE)],
        capture_output=True, timeout=15,
    )
    stdout = r.stdout.decode().strip()
    assert r.returncode == 0, (
        f"REMOVED first char codepoint is {stdout!r}, expected 45 (ASCII '-').\n"
        f"stderr: {r.stderr.decode()}"
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


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

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
