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
script = script.replace('\$state(', '(/* state */')
script = script.replace('\$derived(', '(/* derived */')
script = script.replace('\$effect(', '(/* effect */')
script = script.replace('\$props()', '({})')
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
# Repo CI/CD pass-to-pass tests - verifying repo structure and validity
# Discovered from gradio-app/gradio at commit 7874d0411c81dcde9c4b08e7e064ca0dbef94e2e
# ---------------------------------------------------------------------------

# [repo] pass_to_pass - TypeScript syntax check for audio package
def test_audio_ts_syntax_valid():
    """TypeScript files in js/audio must have valid syntax structure (pass_to_pass)."""
    audio_dir = Path(REPO) / "js" / "audio"
    ts_files = list(audio_dir.glob("*.ts")) + list(audio_dir.glob("shared/*.ts"))

    for ts_file in ts_files:
        content = ts_file.read_text()
        # Basic syntax checks
        open_braces = content.count("{")
        close_braces = content.count("}")
        open_parens = content.count("(")
        close_parens = content.count(")")
        open_brackets = content.count("[")
        close_brackets = content.count("]")

        assert open_braces == close_braces, f"{ts_file.name}: Unbalanced braces ({open_braces} vs {close_braces})"
        assert open_parens == close_parens, f"{ts_file.name}: Unbalanced parens ({open_parens} vs {close_parens})"
        assert open_brackets == close_brackets, f"{ts_file.name}: Unbalanced brackets ({open_brackets} vs {close_brackets})"


# [repo] pass_to_pass - Audio component test file structure
def test_audio_test_file_valid():
    """Audio component test file must be valid and complete (pass_to_pass)."""
    test_file = Path(REPO) / "js" / "audio" / "audio.test.ts"
    assert test_file.exists(), "audio.test.ts must exist"

    content = test_file.read_text()
    # Check for essential test constructs
    assert "import" in content, "Test file must have imports"
    assert "test(" in content or "describe(" in content or "it(" in content, "Test file must have test functions"
    assert "assert" in content or "expect" in content, "Test file must have assertions"

    # Check balanced structure
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, f"Test file has unbalanced braces"


# [repo] pass_to_pass - Svelte component structure for audio package
def test_audio_svelte_structure_valid():
    """Svelte files in js/audio must have valid structure (pass_to_pass)."""
    audio_dir = Path(REPO) / "js" / "audio"
    svelte_files = list(audio_dir.glob("*.svelte")) + list(audio_dir.glob("shared/*.svelte"))

    for svelte_file in svelte_files:
        content = svelte_file.read_text()

        # Check for script tag
        assert "<script" in content, f"{svelte_file.name}: Must have <script> tag"

        # Check script tag is closed
        assert "</script>" in content, f"{svelte_file.name}: <script> tag must be closed"

        # Basic brace balance (approximate for Svelte)
        script_match = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
        if script_match:
            script_content = script_match.group(1)
            open_braces = script_content.count("{")
            close_braces = script_content.count("}")
            assert open_braces == close_braces, f"{svelte_file.name}: Unbalanced braces in script"


# [repo] pass_to_pass - Audio package.json validity
def test_audio_package_json_valid():
    """Audio package.json must be valid JSON with required fields (pass_to_pass)."""
    pkg_file = Path(REPO) / "js" / "audio" / "package.json"
    assert pkg_file.exists(), "package.json must exist"

    content = pkg_file.read_text()
    try:
        pkg = json.loads(content)
    except json.JSONDecodeError as e:
        raise AssertionError(f"package.json is invalid JSON: {e}")

    # Check required fields
    assert "name" in pkg, "package.json must have name"
    assert "@gradio/audio" == pkg["name"], f"name should be @gradio/audio, got {pkg.get('name')}"
    assert "version" in pkg, "package.json must have version"


# ---------------------------------------------------------------------------
# Additional CI/CD pass-to-pass tests for gradio-app/gradio
# Based on repo structure analysis at commit 7874d0411c81dcde9c4b08e7e064ca0dbef94e2e
# ---------------------------------------------------------------------------

# [repo] pass_to_pass - Audio shared module exports valid
def test_audio_shared_index_exports():
    """Audio shared/index.ts must export required components (pass_to_pass)."""
    index_file = Path(REPO) / "js" / "audio" / "shared" / "index.ts"
    assert index_file.exists(), "shared/index.ts must exist"

    content = index_file.read_text()

    # Check for export statements
    exports = re.findall(r"export\s+\{([^}]+)\}|export\s+\*\s+from\s+['\"]([^'\"]+)['\"]|export\s+\{[^}]*\}\s+from\s+['\"]([^'\"]+)['\"]", content)
    assert len(exports) > 0, "shared/index.ts must have exports"

    # Check balanced braces
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, "shared/index.ts has unbalanced braces"


# [repo] pass_to_pass - Audio package uses Svelte 5 runes (base commit has $props, $bindable, $derived)
def test_audio_svelte5_runes_base():
    """Audio components must use Svelte 5 runes ($props, $bindable, $derived) (pass_to_pass)."""
    # Check MinimalAudioRecorder has Svelte 5 structure
    recorder_script = _extract_script(RECORDER)

    # At base commit, these should already exist (Svelte 5 migration partially done)
    assert "$props()" in recorder_script, "Recorder must use Svelte 5 $props() for props"
    assert "$bindable()" in recorder_script, "Recorder must use $bindable() for two-way binding"

    # Check MinimalAudioPlayer
    player_script = _extract_script(PLAYER)
    assert "$props()" in player_script, "Player must use Svelte 5 $props() for props"
    assert "$derived(" in player_script, "Player must use $derived() for computed values"


# [repo] pass_to_pass - Audio package TypeScript imports valid
def test_audio_imports_valid():
    """TypeScript files in audio package must have valid import paths (pass_to_pass)."""
    audio_dir = Path(REPO) / "js" / "audio"
    ts_files = list(audio_dir.glob("*.ts")) + list(audio_dir.glob("shared/*.ts"))

    for ts_file in ts_files:
        content = ts_file.read_text()

        # Find all import statements
        imports = re.findall(r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]", content)

        for imp in imports:
            # Check relative imports exist
            if imp.startswith("./") or imp.startswith("../"):
                # Resolve the import path
                base_dir = ts_file.parent
                if imp.endswith(".ts") or imp.endswith(".js"):
                    resolved = base_dir / imp
                else:
                    # Try with .ts extension
                    resolved = base_dir / (imp + ".ts")
                    if not resolved.exists():
                        # Try as directory with index.ts
                        resolved = base_dir / imp / "index.ts"

                # Only check if it's within the audio package
                if "@gradio/" not in imp and imp.startswith(("./", "../")):
                    # For .svelte imports, check file exists
                    if imp.endswith(".svelte"):
                        svelte_path = base_dir / imp
                        assert svelte_path.exists(), f"{ts_file.name}: Import '{imp}' not found"


# [repo] pass_to_pass - Audio test file imports valid
def test_audio_test_imports_valid():
    """Audio test file must have valid imports from test libraries (pass_to_pass)."""
    test_file = Path(REPO) / "js" / "audio" / "audio.test.ts"
    content = test_file.read_text()

    # Check for vitest imports
    assert "vitest" in content, "Test file must import from vitest"

    # Check for @self/tootils import (test utils)
    assert "@self/tootils" in content, "Test file must import from @self/tootils"

    # Verify mock structure for wavesurfer
    mock_match = re.search(r"vi\.mock\s*\(\s*['\"]wavesurfer\.js['\"]", content)
    assert mock_match, "Test file must mock wavesurfer.js"


# [repo] pass_to_pass - Audio package has required subdirectories
def test_audio_package_structure():
    """Audio package must have required subdirectories (pass_to_pass)."""
    audio_dir = Path(REPO) / "js" / "audio"

    required_dirs = ["shared", "interactive", "player", "recorder", "static"]
    for dir_name in required_dirs:
        dir_path = audio_dir / dir_name
        assert dir_path.exists(), f"Audio package must have {dir_name}/ directory"
        assert dir_path.is_dir(), f"{dir_name} must be a directory"


# [repo] pass_to_pass - TypeScript types file valid
def test_audio_types_valid():
    """Audio types.ts must have valid TypeScript type definitions (pass_to_pass)."""
    types_file = Path(REPO) / "js" / "audio" / "shared" / "types.ts"
    assert types_file.exists(), "types.ts must exist in shared/"

    content = types_file.read_text()

    # Check for type/interface definitions
    has_types = "interface" in content or "type " in content
    assert has_types, "types.ts must define types or interfaces"

    # Check balanced braces
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, "types.ts has unbalanced braces"


# [repo] pass_to_pass - Audio buffer utility function valid
def test_audio_buffer_util_valid():
    """Audio buffer utility (audioBufferToWav.ts) must have valid structure (pass_to_pass)."""
    util_file = Path(REPO) / "js" / "audio" / "shared" / "audioBufferToWav.ts"
    assert util_file.exists(), "audioBufferToWav.ts must exist"

    content = util_file.read_text()

    # Check for function export
    assert "export" in content, "audioBufferToWav.ts must have exports"

    # Check for function definition
    has_function = re.search(r"function\s+\w+\s*\(", content) is not None
    assert has_function, "audioBufferToWav.ts must define a function"

    # Check balanced braces
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, "audioBufferToWav.ts has unbalanced braces"


# [repo] pass_to_pass - Audio package exports are valid
def test_audio_exports_valid():
    """Audio package main exports (index.ts) must be valid (pass_to_pass)."""
    index_file = Path(REPO) / "js" / "audio" / "index.ts"
    assert index_file.exists(), "index.ts must exist"

    content = index_file.read_text()

    # Check for export statement
    assert "export" in content, "index.ts must have exports"

    # Basic syntax check
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, "index.ts has unbalanced braces"


# [repo] pass_to_pass - Audio Index.svelte component structure valid
def test_audio_index_svelte_valid():
    """Audio Index.svelte main component must have valid structure (pass_to_pass)."""
    index_svelte = Path(REPO) / "js" / "audio" / "Index.svelte"
    assert index_svelte.exists(), "Index.svelte must exist"

    content = index_svelte.read_text()

    # Check for script tag with TypeScript
    assert '<script lang="ts">' in content, "Index.svelte must have TypeScript script tag"

    # Check for component imports
    assert "import" in content, "Index.svelte must have imports"

    # Check script tag is closed
    assert "</script>" in content, "Index.svelte script must be closed"


# [repo] pass_to_pass - Audio recorder and player Svelte files exist and are valid
def test_audio_recorder_player_structure():
    """Audio recorder and player Svelte files must exist with valid structure (pass_to_pass)."""
    recorder = Path(REPO) / "js" / "audio" / "recorder" / "AudioRecorder.svelte"
    player = Path(REPO) / "js" / "audio" / "player" / "AudioPlayer.svelte"

    # Check files exist
    assert recorder.exists(), "AudioRecorder.svelte must exist"
    assert player.exists(), "AudioPlayer.svelte must exist"

    # Check basic structure
    for filepath in [recorder, player]:
        content = filepath.read_text()
        assert "<script" in content, f"{filepath.name} must have script tag"
        assert "</script>" in content, f"{filepath.name} script tag must be closed"
