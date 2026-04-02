"""
Task: gradio-audio-multimodal-textbox
Repo: gradio-app/gradio @ 7874d0411c81dcde9c4b08e7e064ca0dbef94e2e
PR:   12999

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/gradio"
RECORDER = Path(REPO) / "js/audio/shared/MinimalAudioRecorder.svelte"
PLAYER = Path(REPO) / "js/audio/shared/MinimalAudioPlayer.svelte"


def _extract_script(filepath: Path) -> str:
    """Extract <script> content with comments stripped."""
    content = filepath.read_text()
    m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    assert m, f"No <script> tag in {filepath}"
    script = m.group(1)
    script = re.sub(r"//.*?$", "", script, flags=re.MULTILINE)
    script = re.sub(r"/\*.*?\*/", "", script, flags=re.DOTALL)
    return script


def _var_uses_state(script: str, var_name: str) -> bool:
    """Check if a variable declaration uses $state()."""
    pattern = rf"(?:let|var|const)\s+{re.escape(var_name)}\b[^=]*=\s*\$state\s*[<(]"
    return bool(re.search(pattern, script))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_recorder_state_variables_reactive():
    """Recording state vars must use $state() for Svelte 5 reactivity."""
    script = _extract_script(RECORDER)
    required = [
        "record", "seconds", "is_recording", "has_started",
        "mic_devices", "selected_device_id", "show_device_selection",
    ]
    missing = [v for v in required if not _var_uses_state(script, v)]
    assert not missing, f"Recorder vars not using $state(): {missing}"


# [pr_diff] fail_to_pass
def test_player_state_variables_reactive():
    """Playback state vars (playing, duration, currentTime, waveform_ready) must use $state()."""
    script = _extract_script(PLAYER)
    required = ["playing", "duration", "currentTime", "waveform_ready"]
    missing = [v for v in required if not _var_uses_state(script, v)]
    assert not missing, f"Player vars not using $state(): {missing}"


# [pr_diff] fail_to_pass
def test_stop_button_conditional_logic():
    """Stop button must check is_recording: stop if recording, onclear if not."""
    content = RECORDER.read_text()
    content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

    # Look for conditional logic around stop-button that references is_recording
    assert "stop-button" in content, "No stop-button class found in recorder"

    # The onclick handler must branch on is_recording
    has_conditional = bool(re.search(
        r"is_recording.*?\{.*?recording\s*=\s*false.*?\}.*?else.*?\{.*?onclear",
        content, re.DOTALL
    )) or bool(re.search(
        r"is_recording\s*\?.*?recording\s*=\s*false.*?:.*?onclear",
        content, re.DOTALL
    ))
    assert has_conditional, (
        "Stop button must conditionally check is_recording: "
        "set recording=false when recording, call onclear when not"
    )


# [pr_diff] fail_to_pass
def test_startmic_error_handling():
    """startMic() call must have error handling (.catch or try/catch)."""
    script = _extract_script(RECORDER)

    has_dot_catch = bool(re.search(r"startMic\s*\([^)]*\)[\s\S]*?\.catch\s*\(", script))
    has_try_catch = bool(re.search(
        r"try\s*\{[^}]*(?:await\s+)?(?:\w+\.)?startMic.*?\}\s*catch\s*\(",
        script, re.DOTALL
    ))
    assert has_dot_catch or has_try_catch, (
        "startMic() must have .catch() or try/catch error handling"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_recorder_not_stub():
    """MinimalAudioRecorder.svelte must have substantial implementation."""
    script = _extract_script(RECORDER)
    lines = [l for l in script.split("\n") if l.strip()]
    assert len(lines) >= 20, f"Recorder script too short ({len(lines)} lines)"

    # Must have real logic: functions, event handlers, imports
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
