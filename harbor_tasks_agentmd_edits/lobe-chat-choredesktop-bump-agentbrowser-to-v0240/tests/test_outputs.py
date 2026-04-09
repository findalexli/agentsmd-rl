"""
Task: lobe-chat-choredesktop-bump-agentbrowser-to-v0240
Repo: lobehub/lobe-chat @ 918e4a8fa182a564ed5bbb59cf7f3075c3cbce29
PR:   13550

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/lobe-chat"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS files must parse without errors."""
    # Check download-agent-browser.mjs parses correctly using Node.js
    script_path = Path(f"{REPO}/apps/desktop/scripts/download-agent-browser.mjs")
    r = subprocess.run(
        ["node", "--check", str(script_path)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"JS syntax error: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_version_constant_updated():
    """download-agent-browser.mjs has VERSION constant set to 0.24.0."""
    # Read the file and extract VERSION using Node.js to validate JS parsing
    script_path = Path(f"{REPO}/apps/desktop/scripts/download-agent-browser.mjs")
    code = """
import fs from 'fs';
const content = fs.readFileSync('""" + str(script_path) + """', 'utf8');
const match = content.match(/const VERSION = '([0-9.]+)';/);
if (match) {
    console.log(match[1]);
} else {
    console.log('NOT_FOUND');
}
"""
    tmp_script = Path(f"{REPO}/_eval_version.mjs")
    tmp_script.write_text(code)
    try:
        r = subprocess.run(
            ["node", str(tmp_script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Failed to extract VERSION: {r.stderr}"
        version = r.stdout.strip()
        assert version == "0.24.0", f"VERSION should be '0.24.0', got '{version}'"
    finally:
        tmp_script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified files have real logic, not just placeholders."""
    # Check download-agent-browser.mjs has real implementation code
    script_path = Path(f"{REPO}/apps/desktop/scripts/download-agent-browser.mjs")
    content = script_path.read_text()

    # Should have actual implementation code
    assert "pipeline(" in content, "download-agent-browser.mjs missing pipeline call"
    assert "fetch(" in content, "download-agent-browser.mjs missing fetch call"
    assert "createWriteStream" in content, "download-agent-browser.mjs missing file write logic"

    # Check the file has more than just the VERSION line
    lines = [l for l in content.split('\n') if l.strip()]
    assert len(lines) > 20, f"File too short ({len(lines)} lines), likely incomplete"
