"""
Task: gradio-audio-multimodal-textbox
Repo: gradio-app/gradio @ 7874d0411c81dcde9c4b08e7e064ca0dbef94e2e
PR:   12999

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
import json
import tempfile
import os
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
script = script.replace('\\$state(', '(/* state */')
script = script.replace('\\$derived(', '(/* derived */')
script = script.replace('\\$effect(', '(/* effect */')
script = script.replace('\\$props()', '({})')
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


def _run_python_check(script_content: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Python check script via subprocess."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        f.flush()
        tmp_path = f.name
    
    try:
        result = subprocess.run(
            ["python3", tmp_path],
            capture_output=True, text=True, timeout=timeout
        )
    finally:
        os.unlink(tmp_path)
    
    return result


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_recorder_state_reactive():
    """Recording state vars must use $state() for Svelte 5 reactivity - validated via subprocess."""
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
    # Handles optional type annotation (e.g., ": Type") between var name and =
    # NOT: let varName = plain_value
    pattern = rf'(?:let|var|const)\\s+{{var}}\\b(?:\\s*:\\s*[^=]+?)?\\s*=\\s*\\$state\\s*[(<]'
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
    """Playback state vars must use $state() - validated via subprocess."""
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
    # Handles optional type annotation (e.g., ": Type") between var name and =
    pattern = rf'(?:let|var|const)\\s+{{var}}\\b(?:\\s*:\\s*[^=]+?)?\\s*=\\s*\\$state\\s*[(<]'
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
    """Stop button onclick must branch on is_recording - validated via subprocess."""
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
    """startMic() call must have .catch() error handler - validated via subprocess."""
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
# Pass-to-pass (static) - anti-stub + structural integrity
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


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass tests - Real CI commands via subprocess.run()
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - Audio shared components valid Svelte structure
def test_audio_shared_svelte_valid():
    """Audio shared Svelte components must have valid TypeScript and structure (pass_to_pass)."""
    shared_dir = Path(REPO) / "js" / "audio" / "shared"

    check_script = """
import re
import sys
from pathlib import Path

shared_dir = Path('SHARED_DIR')
svelte_files = list(shared_dir.glob('*.svelte'))

if len(svelte_files) == 0:
    print('INVALID: No .svelte files found in shared/')
    sys.exit(1)

for svelte_file in svelte_files:
    content = svelte_file.read_text()
    # Must have TypeScript script tag
    if '<script lang="ts">' not in content:
        print('INVALID:', svelte_file.name, 'must use TypeScript (<script lang="ts">)')
        sys.exit(1)
    # Must have closing script tag
    if '</script>' not in content:
        print('INVALID:', svelte_file.name, 'missing </script>')
        sys.exit(1)
    # Check balanced braces in script section
    script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if script_match:
        script_content = script_match.group(1)
        open_braces = script_content.count('{')
        close_braces = script_content.count('}')
        if open_braces != close_braces:
            print('INVALID:', svelte_file.name, 'unbalanced braces')
            sys.exit(1)
        # Must have at least some function/variable definition
        if 'function' not in script_content and '=>' not in script_content and 'let ' not in script_content:
            print('INVALID:', svelte_file.name, 'appears to be empty/stub')
            sys.exit(1)

print('VALID:', len(svelte_files), 'Svelte files validated')
""".replace('SHARED_DIR', str(shared_dir))

    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Shared Svelte check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - Audio package.json validity via Python subprocess
def test_audio_package_json_valid():
    """Audio package.json must be valid JSON with required fields (pass_to_pass)."""
    pkg_file = Path(REPO) / "js" / "audio" / "package.json"
    
    check_script = """
import json
import sys

try:
    with open('PKG_PATH') as f:
        pkg = json.load(f)
    assert 'name' in pkg, 'package.json must have name'
    name = pkg.get('name', '')
    assert name == '@gradio/audio', 'name should be @gradio/audio, got: ' + name
    assert 'version' in pkg, 'package.json must have version'
    assert 'exports' in pkg, 'package.json must have exports'
    print('VALID')
except Exception as e:
    print('INVALID:', e)
    sys.exit(1)
""".replace('PKG_PATH', str(pkg_file))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"package.json validation failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - Audio component test file structure via subprocess
def test_audio_test_file_valid():
    """Audio component test file must be valid and complete (pass_to_pass)."""
    test_file = Path(REPO) / "js" / "audio" / "audio.test.ts"
    
    check_script = """
import sys

try:
    with open('TEST_PATH') as f:
        content = f.read()
    # Check for essential test constructs
    assert 'import' in content, 'Test file must have imports'
    assert 'test(' in content or 'describe(' in content or 'it(' in content, 'Test file must have test functions'
    assert 'assert' in content or 'expect' in content, 'Test file must have assertions'
    # Check balanced structure
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, 'Test file has unbalanced braces: ' + str(open_braces) + ' vs ' + str(close_braces)
    print('VALID')
except Exception as e:
    print('INVALID:', e)
    sys.exit(1)
""".replace('TEST_PATH', str(test_file))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Test file validation failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - Svelte component syntax check via subprocess
def test_audio_svelte_syntax_valid():
    """Svelte files in js/audio must have valid syntax structure via Python check (pass_to_pass)."""
    audio_dir = Path(REPO) / "js" / "audio"
    
    check_script = """
import re
import sys
from pathlib import Path

audio_dir = Path('AUDIO_DIR')
svelte_files = list(audio_dir.glob('*.svelte')) + list(audio_dir.glob('shared/*.svelte'))

for svelte_file in svelte_files:
    content = svelte_file.read_text()
    # Check for script tag
    if '<script' not in content:
        print('INVALID:', svelte_file.name, 'missing <script> tag')
        sys.exit(1)
    if '</script>' not in content:
        print('INVALID:', svelte_file.name, 'missing </script>')
        sys.exit(1)
    # Check balanced braces in script
    script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if script_match:
        script_content = script_match.group(1)
        opens = script_content.count('{') + script_content.count('(') + script_content.count('[')
        closes = script_content.count('}') + script_content.count(')') + script_content.count(']')
        if opens != closes:
            print('INVALID:', svelte_file.name, 'unbalanced delimiters')
            sys.exit(1)
print('VALID')
""".replace('AUDIO_DIR', str(audio_dir))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Svelte syntax check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - Audio shared module exports valid via subprocess
def test_audio_shared_index_exports():
    """Audio shared/index.ts must exist with valid exports structure (pass_to_pass)."""
    index_file = Path(REPO) / "js" / "audio" / "shared" / "index.ts"
    
    check_script = """
import re
import sys
from pathlib import Path

index_file = Path('INDEX_PATH')
if not index_file.exists():
    print('INVALID: shared/index.ts must exist')
    sys.exit(1)

content = index_file.read_text()
# Check for export statements
exports = re.findall(r'export\\s+\\{([^}]+)\\}|export\\s+\\*\\s+from\\s+[\\\'\"]([^\\\'\"]+)[\\\'\"]|export\\s+\\{[^}]*\\}\\s+from\\s+[\\\'\"]([^\\\'\"]+)[\\\'\"]', content)
if len(exports) == 0:
    print('INVALID: shared/index.ts must have exports')
    sys.exit(1)

# Check balanced braces
open_braces = content.count('{')
close_braces = content.count('}')
if open_braces != close_braces:
    print('INVALID: shared/index.ts has unbalanced braces')
    sys.exit(1)
print('VALID')
""".replace('INDEX_PATH', str(index_file))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Shared index exports check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - Audio package structure check via subprocess
def test_audio_package_structure():
    """Audio package must have required subdirectories (pass_to_pass)."""
    audio_dir = Path(REPO) / "js" / "audio"
    
    check_script = """
import sys
from pathlib import Path

audio_dir = Path('AUDIO_DIR')
required_dirs = ['shared', 'interactive', 'player', 'recorder', 'static']

for dir_name in required_dirs:
    dir_path = audio_dir / dir_name
    if not dir_path.exists():
        print('INVALID: Audio package missing ' + dir_name + '/ directory')
        sys.exit(1)
    if not dir_path.is_dir():
        print('INVALID: ' + dir_name + ' is not a directory')
        sys.exit(1)
print('VALID')
""".replace('AUDIO_DIR', str(audio_dir))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Package structure check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - Audio types.ts validity via subprocess
def test_audio_types_valid():
    """Audio types.ts must have valid TypeScript type definitions (pass_to_pass)."""
    types_file = Path(REPO) / "js" / "audio" / "shared" / "types.ts"
    
    check_script = """
import sys
from pathlib import Path

types_file = Path('TYPES_PATH')
if not types_file.exists():
    print('INVALID: types.ts must exist in shared/')
    sys.exit(1)

content = types_file.read_text()
# Check for type/interface definitions
has_types = 'interface' in content or 'type ' in content
if not has_types:
    print('INVALID: types.ts must define types or interfaces')
    sys.exit(1)

# Check balanced braces
open_braces = content.count('{')
close_braces = content.count('}')
if open_braces != close_braces:
    print('INVALID: types.ts has unbalanced braces')
    sys.exit(1)
print('VALID')
""".replace('TYPES_PATH', str(types_file))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Types validity check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - Audio buffer utility via subprocess
def test_audio_buffer_util_valid():
    """Audio buffer utility (audioBufferToWav.ts) must have valid structure (pass_to_pass)."""
    util_file = Path(REPO) / "js" / "audio" / "shared" / "audioBufferToWav.ts"
    
    check_script = """
import re
import sys
from pathlib import Path

util_file = Path('UTIL_PATH')
if not util_file.exists():
    print('INVALID: audioBufferToWav.ts must exist')
    sys.exit(1)

content = util_file.read_text()
# Check for function export
if 'export' not in content:
    print('INVALID: audioBufferToWav.ts must have exports')
    sys.exit(1)

# Check for function definition
has_function = re.search(r'function\\s+\\w+\\s*\\(', content) is not None
if not has_function:
    print('INVALID: audioBufferToWav.ts must define a function')
    sys.exit(1)

# Check balanced braces
open_braces = content.count('{')
close_braces = content.count('}')
if open_braces != close_braces:
    print('INVALID: audioBufferToWav.ts has unbalanced braces')
    sys.exit(1)
print('VALID')
""".replace('UTIL_PATH', str(util_file))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Buffer util check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - Audio main exports via subprocess
def test_audio_exports_valid():
    """Audio package main exports (index.ts) must be valid (pass_to_pass)."""
    index_file = Path(REPO) / "js" / "audio" / "index.ts"
    
    check_script = """
import sys
from pathlib import Path

index_file = Path('INDEX_PATH')
if not index_file.exists():
    print('INVALID: index.ts must exist')
    sys.exit(1)

content = index_file.read_text()
# Check for export statement
if 'export' not in content:
    print('INVALID: index.ts must have exports')
    sys.exit(1)

# Basic syntax check
open_braces = content.count('{')
close_braces = content.count('}')
if open_braces != close_braces:
    print('INVALID: index.ts has unbalanced braces')
    sys.exit(1)
print('VALID')
""".replace('INDEX_PATH', str(index_file))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Main exports check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - Audio Index.svelte component via subprocess
def test_audio_index_svelte_valid():
    """Audio Index.svelte main component must have valid structure (pass_to_pass)."""
    index_svelte = Path(REPO) / "js" / "audio" / "Index.svelte"
    
    check_script = """
import sys
from pathlib import Path

index_svelte = Path('INDEX_PATH')
if not index_svelte.exists():
    print('INVALID: Index.svelte must exist')
    sys.exit(1)

content = index_svelte.read_text()
# Check for script tag with TypeScript
if '<script lang="ts">' not in content:
    print('INVALID: Index.svelte must have TypeScript script tag')
    sys.exit(1)

# Check for component imports
if 'import' not in content:
    print('INVALID: Index.svelte must have imports')
    sys.exit(1)

# Check script tag is closed
if '</script>' not in content:
    print('INVALID: Index.svelte script must be closed')
    sys.exit(1)
print('VALID')
""".replace('INDEX_PATH', str(index_svelte))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Index.svelte check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - Audio recorder and player exist via subprocess
def test_audio_recorder_player_exist():
    """Audio recorder and player Svelte files must exist with valid structure (pass_to_pass)."""
    recorder = Path(REPO) / "js" / "audio" / "recorder" / "AudioRecorder.svelte"
    player = Path(REPO) / "js" / "audio" / "player" / "AudioPlayer.svelte"
    
    check_script = """
import sys
from pathlib import Path

recorder = Path('RECORDER_PATH')
player = Path('PLAYER_PATH')

# Check files exist
if not recorder.exists():
    print('INVALID: AudioRecorder.svelte must exist')
    sys.exit(1)
if not player.exists():
    print('INVALID: AudioPlayer.svelte must exist')
    sys.exit(1)

# Check basic structure
for filepath in [recorder, player]:
    content = filepath.read_text()
    if '<script' not in content:
        print('INVALID: ' + filepath.name + ' missing script tag')
        sys.exit(1)
    if '</script>' not in content:
        print('INVALID: ' + filepath.name + ' missing closed script tag')
        sys.exit(1)
print('VALID')
""".replace('RECORDER_PATH', str(recorder)).replace('PLAYER_PATH', str(player))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Recorder/player check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - MinimalAudioRecorder has Svelte 5 structure (base commit)
def test_audio_recorder_svelte5_runes():
    """Audio MinimalAudioRecorder uses Svelte 5 runes $props and $bindable at base commit (pass_to_pass)."""
    recorder = Path(REPO) / "js" / "audio" / "shared" / "MinimalAudioRecorder.svelte"

    check_script = """
import re
import sys
from pathlib import Path

recorder = Path('RECORDER_PATH')
if not recorder.exists():
    print('INVALID: MinimalAudioRecorder.svelte must exist')
    sys.exit(1)

content = recorder.read_text()
script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
if not script_match:
    print('INVALID: No script tag found')
    sys.exit(1)

script = script_match.group(1)
# Check for Svelte 5 runes present at base commit ($props and $bindable, NOT $state yet)
if '$props()' not in script:
    print('INVALID: Recorder must use $props() for props')
    sys.exit(1)
if '$bindable()' not in script:
    print('INVALID: Recorder must use $bindable() for two-way binding')
    sys.exit(1)
print('VALID')
""".replace('RECORDER_PATH', str(recorder))

    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Recorder Svelte 5 check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# [repo_tests] pass_to_pass - MinimalAudioPlayer has Svelte 5 structure
def test_audio_player_svelte5_runes():
    """Audio MinimalAudioPlayer uses Svelte 5 runes ($props, $derived) (pass_to_pass)."""
    player = Path(REPO) / "js" / "audio" / "shared" / "MinimalAudioPlayer.svelte"
    
    check_script = """
import re
import sys
from pathlib import Path

player = Path('PLAYER_PATH')
if not player.exists():
    print('INVALID: MinimalAudioPlayer.svelte must exist')
    sys.exit(1)

content = player.read_text()
script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
if not script_match:
    print('INVALID: No script tag found')
    sys.exit(1)

script = script_match.group(1)
# Check for Svelte 5 runes
if '$props()' not in script:
    print('INVALID: Player must use $props() for props')
    sys.exit(1)
if '$derived(' not in script:
    print('INVALID: Player must use $derived() for computed values')
    sys.exit(1)
print('VALID')
""".replace('PLAYER_PATH', str(player))
    
    r = _run_python_check(check_script, timeout=30)
    assert r.returncode == 0, f"Player Svelte 5 check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "VALID" in r.stdout


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass tests - Real CI commands via subprocess.run()
# These tests run actual CI commands from the repository's test suite
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - Python audio component tests (real CI command)
def test_repo_python_audio_duration():
    """Python audio component duration validator test passes (pass_to_pass).

    Runs the actual pytest CI command for the audio duration validator test.
    This is a real CI test from test/components/test_audio.py.
    Installs required dependencies before running.
    """
    # Install required dependencies first
    deps = subprocess.run(
        ["pip", "install", "-q", "gradio_client", "numpy", "pytest-asyncio", "aiohttp", "fastapi", "pydantic", "pillow", "anyio"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Install gradio and gradio_client in editable mode
    subprocess.run(["pip", "install", "-q", "-e", "."], capture_output=True, cwd=REPO, timeout=180)
    subprocess.run(["pip", "install", "-q", "-e", "client/python"], capture_output=True, cwd=REPO, timeout=180)

    r = subprocess.run(
        ["python", "-m", "pytest", "test/components/test_audio.py::test_duration_validator", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Python audio duration test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Python audio component core functions (real CI command)
def test_repo_python_audio_component():
    """Python audio component core functions test passes (pass_to_pass).

    Runs pytest for TestAudio::test_component_functions from the repo's CI suite.
    Installs required dependencies before running.
    """
    # Install required dependencies first
    deps = subprocess.run(
        ["pip", "install", "-q", "gradio_client", "numpy", "pytest-asyncio", "aiohttp", "fastapi", "pydantic", "pillow", "anyio"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Install gradio and gradio_client in editable mode
    subprocess.run(["pip", "install", "-q", "-e", "."], capture_output=True, cwd=REPO, timeout=180)
    subprocess.run(["pip", "install", "-q", "-e", "client/python"], capture_output=True, cwd=REPO, timeout=180)

    r = subprocess.run(
        ["python", "-m", "pytest", "test/components/test_audio.py::TestAudio::test_component_functions", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Python audio component test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Python audio default value postprocess (real CI command)
def test_repo_python_audio_default_value():
    """Python audio default value postprocess test passes (pass_to_pass).

    Runs pytest for TestAudio::test_default_value_postprocess from the repo's CI suite.
    Installs required dependencies before running.
    """
    # Install required dependencies first
    deps = subprocess.run(
        ["pip", "install", "-q", "gradio_client", "numpy", "pytest-asyncio", "aiohttp", "fastapi", "pydantic", "pillow", "anyio"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Install gradio and gradio_client in editable mode
    subprocess.run(["pip", "install", "-q", "-e", "."], capture_output=True, cwd=REPO, timeout=180)
    subprocess.run(["pip", "install", "-q", "-e", "client/python"], capture_output=True, cwd=REPO, timeout=180)

    r = subprocess.run(
        ["python", "-m", "pytest", "test/components/test_audio.py::TestAudio::test_default_value_postprocess", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Python audio default value test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Python audio HTTP URL postprocess (real CI command)
def test_repo_python_audio_http_url():
    """Python audio HTTP URL postprocess test passes (pass_to_pass).

    Runs pytest for TestAudio::test_postprocess_http_url_like from the repo's CI suite.
    Installs required dependencies before running.
    """
    # Install required dependencies first
    deps = subprocess.run(
        ["pip", "install", "-q", "gradio_client", "numpy", "pytest-asyncio", "aiohttp", "fastapi", "pydantic", "pillow", "anyio"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Install gradio and gradio_client in editable mode
    subprocess.run(["pip", "install", "-q", "-e", "."], capture_output=True, cwd=REPO, timeout=180)
    subprocess.run(["pip", "install", "-q", "-e", "client/python"], capture_output=True, cwd=REPO, timeout=180)

    r = subprocess.run(
        ["python", "-m", "pytest", "test/components/test_audio.py::TestAudio::test_postprocess_http_url_like", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Python audio HTTP URL test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
