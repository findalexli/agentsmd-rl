#!/usr/bin/env bash
set +e

RECORDER="/workspace/gradio/js/audio/shared/MinimalAudioRecorder.svelte"
PLAYER="/workspace/gradio/js/audio/shared/MinimalAudioPlayer.svelte"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_recorder_state]=0.30
WEIGHTS[behavioral_player_state]=0.20
WEIGHTS[behavioral_stop_logic]=0.15
WEIGHTS[structural_error_handling]=0.15
WEIGHTS[antistub]=0.20

for key in behavioral_recorder_state behavioral_player_state behavioral_stop_logic structural_error_handling antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: Files exist ----------
if [ ! -f "$RECORDER" ] || [ ! -f "$PLAYER" ]; then
    echo "GATE FAIL: target files not found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: target files exist"

# ---------- PRIMARY 1 (30%): Behavioral - Recorder state variables use $state() ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/audio/shared/MinimalAudioRecorder.svelte") as f:
    content = f.read()

# The key variables that must use $state() for reactivity in Svelte 5
required_state_vars = ["is_recording", "has_started", "seconds"]
found = 0
for var in required_state_vars:
    # Match patterns like: let is_recording = $state(false);
    pattern = rf'let\s+{var}[^=]*=\s*\$state\('
    if re.search(pattern, content):
        found += 1
        print(f"  FOUND: {var} uses $state()")
    else:
        print(f"  MISSING: {var} does not use $state()")

if found >= 3:
    print("BEHAVIORAL_RECORDER_STATE PASS: all critical recorder state variables use $state()")
    sys.exit(0)
elif found >= 2:
    print(f"BEHAVIORAL_RECORDER_STATE PARTIAL: {found}/3 state variables converted")
    sys.exit(0)
else:
    print(f"BEHAVIORAL_RECORDER_STATE FAIL: only {found}/3 state variables converted")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_recorder_state]=1
    echo "TEST behavioral_recorder_state: PASS"
else
    echo "TEST behavioral_recorder_state: FAIL"
fi

# ---------- PRIMARY 2 (20%): Behavioral - Player state variables use $state() ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/audio/shared/MinimalAudioPlayer.svelte") as f:
    content = f.read()

required_state_vars = ["playing", "duration", "currentTime", "waveform_ready"]
found = 0
for var in required_state_vars:
    pattern = rf'let\s+{var}[^=]*=\s*\$state\('
    if re.search(pattern, content):
        found += 1
        print(f"  FOUND: {var} uses $state()")
    else:
        print(f"  MISSING: {var} does not use $state()")

if found >= 3:
    print("BEHAVIORAL_PLAYER_STATE PASS: player state variables use $state()")
    sys.exit(0)
else:
    print(f"BEHAVIORAL_PLAYER_STATE FAIL: only {found}/4 state variables converted")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_player_state]=1
    echo "TEST behavioral_player_state: PASS"
else
    echo "TEST behavioral_player_state: FAIL"
fi

# ---------- PRIMARY 3 (15%): Behavioral - Stop button differentiates recording vs clear ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/audio/shared/MinimalAudioRecorder.svelte") as f:
    content = f.read()

# The fix adds a conditional: if (is_recording) { recording = false } else { onclear?.() }
# Check that the stop button handler checks is_recording state
stop_section = re.search(r'class="stop-button".*?</button>', content, re.DOTALL)
if stop_section:
    stop_code = stop_section.group(0)
    if "is_recording" in stop_code and "onclear" in stop_code:
        print("BEHAVIORAL_STOP_LOGIC PASS: stop button differentiates recording vs clear state")
        sys.exit(0)
    elif "is_recording" in stop_code:
        print("BEHAVIORAL_STOP_LOGIC PARTIAL: checks is_recording but missing onclear")
        sys.exit(0)
    else:
        print("BEHAVIORAL_STOP_LOGIC FAIL: stop button does not check is_recording state")
        sys.exit(1)
else:
    # Try a broader search
    if "is_recording" in content and "onclear" in content and "stop" in content.lower():
        print("BEHAVIORAL_STOP_LOGIC PASS: is_recording and onclear both present in component")
        sys.exit(0)
    print("BEHAVIORAL_STOP_LOGIC FAIL: could not find stop button handler")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_stop_logic]=1
    echo "TEST behavioral_stop_logic: PASS"
else
    echo "TEST behavioral_stop_logic: FAIL"
fi

# ---------- SUPPLEMENTARY (15%): Structural - startMic error handling ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/audio/shared/MinimalAudioRecorder.svelte") as f:
    content = f.read()

# Check that startMic() has a .catch() or try/catch for error handling
if re.search(r'startMic\b.*\.catch\(', content, re.DOTALL):
    print("STRUCTURAL_ERROR_HANDLING PASS: startMic has .catch() error handling")
    sys.exit(0)
elif re.search(r'try\s*\{.*startMic.*\}\s*catch', content, re.DOTALL):
    print("STRUCTURAL_ERROR_HANDLING PASS: startMic has try/catch error handling")
    sys.exit(0)
else:
    print("STRUCTURAL_ERROR_HANDLING FAIL: no error handling for startMic")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural_error_handling]=1
    echo "TEST structural_error_handling: PASS"
else
    echo "TEST structural_error_handling: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
RECORDER_LINES=$(wc -l < "$RECORDER")
PLAYER_LINES=$(wc -l < "$PLAYER")
HAS_WAVEFORM=$(grep -c "WaveSurfer\|waveform" "$RECORDER" 2>/dev/null || echo "0")
HAS_RECORD=$(grep -c "RecordPlugin\|record" "$RECORDER" 2>/dev/null || echo "0")
if [ "$RECORDER_LINES" -gt 50 ] && [ "$PLAYER_LINES" -gt 20 ] && [ "$HAS_WAVEFORM" -ge 1 ] && [ "$HAS_RECORD" -ge 1 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_recorder_state': ${WEIGHTS[behavioral_recorder_state]}, 'behavioral_player_state': ${WEIGHTS[behavioral_player_state]}, 'behavioral_stop_logic': ${WEIGHTS[behavioral_stop_logic]}, 'structural_error_handling': ${WEIGHTS[structural_error_handling]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_recorder_state': ${RESULTS[behavioral_recorder_state]}, 'behavioral_player_state': ${RESULTS[behavioral_player_state]}, 'behavioral_stop_logic': ${RESULTS[behavioral_stop_logic]}, 'structural_error_handling': ${RESULTS[structural_error_handling]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_recorder_state  (${WEIGHTS[behavioral_recorder_state]}): ${RESULTS[behavioral_recorder_state]}"
echo "  behavioral_player_state    (${WEIGHTS[behavioral_player_state]}): ${RESULTS[behavioral_player_state]}"
echo "  behavioral_stop_logic      (${WEIGHTS[behavioral_stop_logic]}): ${RESULTS[behavioral_stop_logic]}"
echo "  structural_error_handling  (${WEIGHTS[structural_error_handling]}): ${RESULTS[structural_error_handling]}"
echo "  antistub                   (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
