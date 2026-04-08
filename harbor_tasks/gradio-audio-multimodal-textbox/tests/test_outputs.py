"""
Task: gradio-audio-multimodal-textbox
Repo: gradio-app/gradio @ 7874d0411c81dcde9c4b08e7e064ca0dbef94e2e
PR:   12999

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/gradio"
RECORDER = Path(REPO) / "js/audio/shared/MinimalAudioRecorder.svelte"
PLAYER = Path(REPO) / "js/audio/shared/MinimalAudioPlayer.svelte"

# ── Helpers ──────────────────────────────────────────────────────────────────

_SCRIPT_EXTRACTOR = """
import re, sys
from pathlib import Path

filepath = sys.argv[1]
content = Path(filepath).read_text()
m = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
if not m:
    print("NO_SCRIPT_TAG", end="")
    sys.exit(0)
script = m.group(1)
# Strip comments
script = re.sub(r'//.*?$', '', script, flags=re.MULTILINE)
script = re.sub(r'/\\*.*?\\*/', '', script, flags=re.DOTALL)
print(script)
"""

_JS_SYNTAX_CHECK = """
import subprocess, sys, tempfile
from pathlib import Path

filepath = sys.argv[1]
content = Path(filepath).read_text()
m = __import__('re').search(r'<script[^>]*>(.*?)</script>', content, __import__('re').DOTALL)
if not m:
    print("NO_SCRIPT_TAG")
    sys.exit(0)
script = m.group(1)
# Replace Svelte-specific runes with plain JS for syntax checking
script = script.replace('$state(', '(/* $state */')
script = script.replace('$derived(', '(/* $derived */')
script = script.replace('$effect(', '(/* $effect */')
script = script.replace('$props()', '({})')
# Check basic structure: balanced braces, brackets, parens
opens = script.count('{') + script.count('(') + script.count('[')
closes = script.count('}') + script.count(')') + script.count(']')
if opens != closes:
    print(f"UNBALANCED: opens={opens} closes={closes}")
    sys.exit(1)
print("OK")
"""


def _extract_script(filepath: Path) -> str:
    """Extract <script> content with comments stripped."""
    content = filepath.read_text()
    m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    assert m, f"No <script> tag in {filepath}"
    script = m.group(1)
    script = re.sub(r"//.*?$", "", script, flags=re.MULTILINE)
    script = re.sub(r"/\*.*?\*/", "", script, flags=re.DOTALL)
    return script


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_recorder_state_reactive():
    """Recording state vars must use $state() for Svelte 5 reactivity — validated via subprocess."""
    required_vars = [
        "record", "seconds", "is_recording", "has_started",
        "mic_devices", "selected_device_id", "show_device_selection",
    ]
    script = f"""
import re, sys
filepath = sys.argv[1]
content = open(filepath).read()
m = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
assert m, f"No <script> tag in {{filepath}}"
script = m.group(1)
script = re.sub(r'//.*?$', '', script, flags=re.MULTILINE)
script = re.sub(r'/\\*.*?\\*/', '', script, flags=re.DOTALL)

required = {required_vars!r}
missing = []
for var in required:
    # Must find: let/var/const varName ... = $state(
    # NOT: let varName = plain_value
    pattern = rf'(?:let|var|const)\\s+{{var}}\\b[^=]*=\\s*\\$state\\s*[<(]'
    if not re.search(pattern, script):
        missing.append(var)
if missing:
    print(f"NOT_REACTIVE: {{missing}}")
    sys.exit(1)
print("ALL_REACTIVE")
"""
    r = subprocess.run(
        ["python3", "-c", script, str(RECORDER)],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Recorder vars not using $state(): {r.stdout.strip()} {r.stderr.strip()}"
    assert "ALL_REACTIVE" in r.stdout


# [pr_diff] fail_to_pass
def test_player_state_reactive():
    """Playback state vars must use $state() — validated via subprocess."""
    required_vars = ["playing", "duration", "currentTime", "waveform_ready"]
    script = f"""
import re, sys
filepath = sys.argv[1]
content = open(filepath).read()
m = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
assert m, f"No <script> tag in {{filepath}}"
script = m.group(1)
script = re.sub(r'//.*?$', '', script, flags=re.MULTILINE)
script = re.sub(r'/\\*.*?\\*/', '', script, flags=re.DOTALL)

required = {required_vars!r}
missing = []
for var in required:
    pattern = rf'(?:let|var|const)\\s+{{var}}\\b[^=]*=\\s*\\$state\\s*[<(]'
    if not re.search(pattern, script):
        missing.append(var)
if missing:
    print(f"NOT_REACTIVE: {{missing}}")
    sys.exit(1)
print("ALL_REACTIVE")
"""
    r = subprocess.run(
        ["python3", "-c", script, str(PLAYER)],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Player vars not using $state(): {r.stdout.strip()} {r.stderr.strip()}"
    assert "ALL_REACTIVE" in r.stdout


# [pr_diff] fail_to_pass
def test_stop_button_conditional():
    """Stop button onclick must branch on is_recording — validated via subprocess."""
    script = """
import re, sys
filepath = sys.argv[1]
content = open(filepath).read()

# Strip comments
content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
content = re.sub(r'/\\*.*?\\*/', '', content, flags=re.DOTALL)

assert 'stop-button' in content, "No stop-button class found"

# Find the onclick handler for stop-button
# The fix changes: recording = false
# To: if (is_recording) { recording = false } else { onclear?.() }
# Look for the conditional branch pattern
has_if_check = bool(re.search(
    r'is_recording\\s*\\)\\s*\\{[^}]*recording\\s*=\\s*false',
    content
))
has_else_clear = bool(re.search(
    r'else\\s*\\{[^}]*onclear',
    content
))
if not (has_if_check and has_else_clear):
    print(f"FAIL: if_check={has_if_check}, else_clear={has_else_clear}")
    sys.exit(1)
print("OK")
"""
    r = subprocess.run(
        ["python3", "-c", script, str(RECORDER)],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Stop button lacks conditional: {r.stdout.strip()} {r.stderr.strip()}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_startmic_error_handling():
    """startMic() call must have .catch() error handler — validated via subprocess."""
    script = """
import re, sys
filepath = sys.argv[1]
content = open(filepath).read()
content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
content = re.sub(r'/\\*.*?\\*/', '', content, flags=re.DOTALL)

# Find the startMic call region
startmic_match = re.search(r'startMic\\s*\\(', content)
if not startmic_match:
    print("FAIL: no startMic call found")
    sys.exit(1)

# Check that .catch follows startMic
after = content[startmic_match.start():]
has_catch = bool(re.search(r'\\.catch\\s*\\(', after))
has_try = bool(re.search(r'try\\s*\\{[^}]*(?:await\\s+)?startMic', content, re.DOTALL))
if not (has_catch or has_try):
    print("FAIL: no .catch() or try/catch after startMic()")
    sys.exit(1)
print("OK")
"""
    r = subprocess.run(
        ["python3", "-c", script, str(RECORDER)],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"No error handling on startMic: {r.stdout.strip()} {r.stderr.strip()}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_recorder_js_balanced():
    """MinimalAudioRecorder <script> has balanced braces/parens (valid syntax skeleton)."""
    r = subprocess.run(
        ["python3", "-c", _JS_SYNTAX_CHECK, str(RECORDER)],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Recorder script has unbalanced delimiters: {r.stdout.strip()}"
    assert "OK" in r.stdout


# [static] pass_to_pass
def test_player_js_balanced():
    """MinimalAudioPlayer <script> has balanced braces/parens (valid syntax skeleton)."""
    r = subprocess.run(
        ["python3", "-c", _JS_SYNTAX_CHECK, str(PLAYER)],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Player script has unbalanced delimiters: {r.stdout.strip()}"
    assert "OK" in r.stdout


# [static] pass_to_pass
def test_recorder_not_stub():
    """MinimalAudioRecorder.svelte must have substantial implementation."""
    script = _extract_script(RECORDER)
    lines = [l for l in script.split("\n") if l.strip()]
    assert len(lines) >= 20, f"Recorder script too short ({len(lines)} lines)"

    constructs = len(re.findall(
        r"(?:function\s+\w+\s*\(|=>\s*\{|\.\s*(?:then|catch)\s*\(|"
        r"import\s+\{|\bif\s*\(|\$effect\s*\(|\$derived\s*\(|new\s+\w+\s*\()",
        script
    ))
    assert constructs >= 10, f"Recorder has only {constructs} meaningful constructs (need >=10)"


# [static] pass_to_pass
def test_player_not_stub():
    """MinimalAudioPlayer.svelte must have substantial implementation."""
    script = _extract_script(PLAYER)
    lines = [l for l in script.split("\n") if l.strip()]
    assert len(lines) >= 15, f"Player script too short ({len(lines)} lines)"

    constructs = len(re.findall(
        r"(?:function\s+\w+\s*\(|=>\s*\{|\.\s*(?:then|catch)\s*\(|"
        r"import\s+\{|\bif\s*\(|\$effect\s*\(|\$derived\s*\(|new\s+\w+\s*\()",
        script
    ))
    assert constructs >= 8, f"Player has only {constructs} meaningful constructs (need >=8)"
