#!/usr/bin/env bash
set +e

RECORDER="/workspace/gradio/js/audio/shared/MinimalAudioRecorder.svelte"
PLAYER="/workspace/gradio/js/audio/shared/MinimalAudioPlayer.svelte"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

WEIGHT_BEHAVIORAL_RECORDER_STATE=0.30
WEIGHT_BEHAVIORAL_PLAYER_STATE=0.20
WEIGHT_BEHAVIORAL_STOP_LOGIC=0.15
WEIGHT_STRUCTURAL_ERROR_HANDLING=0.15
WEIGHT_ANTISTUB=0.20

declare -A RESULTS
RESULTS[behavioral_recorder_state]=0
RESULTS[behavioral_player_state]=0
RESULTS[behavioral_stop_logic]=0
RESULTS[structural_error_handling]=0
RESULTS[antistub]=0

REWARD=0.0

# ---------- GATE: Files exist and are valid Svelte ----------
if [ ! -f "$RECORDER" ] || [ ! -f "$PLAYER" ]; then
    echo "GATE FAIL: target files not found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# Verify files have valid Svelte structure (must have <script> tags)
if ! grep -q '<script' "$RECORDER" 2>/dev/null || ! grep -q '<script' "$PLAYER" 2>/dev/null; then
    echo "GATE FAIL: files missing <script> tags"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

echo "GATE PASS: target files exist and have script tags"

# ---------- PRIMARY 1 (30%): Behavioral - Recorder state variables use $state() ----------
# [pr_diff] (0.30): is_recording, has_started, seconds must use $state()
python3 << 'PYEOF'
import sys
import re

def extract_script_content(filepath):
    """Extract content inside <script> tags, filtering comments."""
    with open(filepath) as f:
        content = f.read()

    # Find script content
    script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        return None, content

    script_content = script_match.group(1)

    # Remove comments (both // and /* */)
    # Remove // comments
    script_no_comments = re.sub(r'//.*?$', '', script_content, flags=re.MULTILINE)
    # Remove /* */ comments
    script_no_comments = re.sub(r'/\*.*?\*/', '', script_no_comments, flags=re.DOTALL)

    return script_no_comments, content

script_content, full_content = extract_script_content("/workspace/gradio/js/audio/shared/MinimalAudioRecorder.svelte")
if script_content is None:
    print("BEHAVIORAL_RECORDER_STATE FAIL: no <script> tag found")
    sys.exit(1)

# The key variables that must use $state() for reactivity in Svelte 5
required_state_vars = ["is_recording", "has_started", "seconds"]
found = 0
details = []

# Pattern to match: let VAR = $state(...)
# Must be actual declaration, not in comments (we stripped those)
for var in required_state_vars:
    # Match let/var/const X = $state(...)
    pattern = rf'(?:let|var|const)\s+{re.escape(var)}\s*=\s*\$state\s*\('
    if re.search(pattern, script_content):
        found += 1
        details.append(f"FOUND: {var} uses $state()")
    else:
        details.append(f"MISSING: {var} does not use $state()")

for d in details:
    print(f"  {d}")

if found >= 3:
    print("BEHAVIORAL_RECORDER_STATE PASS: all critical recorder state variables use $state()")
    sys.exit(0)
else:
    print(f"BEHAVIORAL_RECORDER_STATE FAIL: only {found}/3 state variables converted")
    sys.exit(1)
PYEOF
BEHAVIORAL_RECORDER_STATE_EXIT=$?
if [ $BEHAVIORAL_RECORDER_STATE_EXIT -eq 0 ]; then
    RESULTS[behavioral_recorder_state]=1
    echo "TEST behavioral_recorder_state: PASS"
else
    echo "TEST behavioral_recorder_state: FAIL"
fi

# ---------- PRIMARY 2 (20%): Behavioral - Player state variables use $state() ----------
# [pr_diff] (0.20): playing, duration, currentTime, waveform_ready must use $state()
python3 << 'PYEOF'
import sys
import re

def extract_script_content(filepath):
    """Extract content inside <script> tags, filtering comments."""
    with open(filepath) as f:
        content = f.read()

    script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        return None, content

    script_content = script_match.group(1)

    # Remove comments
    script_no_comments = re.sub(r'//.*?$', '', script_content, flags=re.MULTILINE)
    script_no_comments = re.sub(r'/\*.*?\*/', '', script_no_comments, flags=re.DOTALL)

    return script_no_comments, content

script_content, full_content = extract_script_content("/workspace/gradio/js/audio/shared/MinimalAudioPlayer.svelte")
if script_content is None:
    print("BEHAVIORAL_PLAYER_STATE FAIL: no <script> tag found")
    sys.exit(1)

required_state_vars = ["playing", "duration", "currentTime", "waveform_ready"]
found = 0
details = []

for var in required_state_vars:
    pattern = rf'(?:let|var|const)\s+{re.escape(var)}\s*=\s*\$state\s*\('
    if re.search(pattern, script_content):
        found += 1
        details.append(f"FOUND: {var} uses $state()")
    else:
        details.append(f"MISSING: {var} does not use $state()")

for d in details:
    print(f"  {d}")

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

# ---------- PRIMARY 3 (15%): Behavioral - Stop button has conditional logic ----------
# [pr_diff] (0.15): Stop button must conditionally call onclear?.() when not recording
python3 << 'PYEOF'
import sys
import re

with open("/workspace/gradio/js/audio/shared/MinimalAudioRecorder.svelte") as f:
    content = f.read()

# Remove comments for reliable parsing
content_no_comments = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)

# Find the stop button and its onclick handler
stop_btn_match = re.search(
    r'class=["\'][^"\']*stop-button[^"\']*["\'].*?onclick=\{(.*?)\}(?:\s|>).*?</button>',
    content_no_comments,
    re.DOTALL | re.IGNORECASE
)

if stop_btn_match:
    onclick_code = stop_btn_match.group(1)
    print(f"  Found onclick handler: {onclick_code[:80]}...")

    # Check for conditional logic in the handler
    # Must check is_recording and conditionally call onclear
    has_is_recording_check = 'is_recording' in onclick_code
    has_onclear_call = 'onclear' in onclick_code

    # Check for if statement or ternary
    has_conditional = bool(re.search(r'\bif\b|\?.*?:', onclick_code))

    if has_is_recording_check and has_onclear_call and has_conditional:
        print("BEHAVIORAL_STOP_LOGIC PASS: stop button has conditional is_recording -> onclear logic")
        sys.exit(0)
    elif has_is_recording_check and has_conditional:
        print("BEHAVIORAL_STOP_LOGIC PARTIAL: has is_recording check but missing onclear call")
        sys.exit(0)
    else:
        print(f"BEHAVIORAL_STOP_LOGIC FAIL: missing conditional logic (is_recording: {has_is_recording_check}, onclear: {has_onclear_call}, conditional: {has_conditional})")
        sys.exit(1)
else:
    # Fallback: search entire file for stop-button class and check logic structure
    if 'stop-button' not in content_no_comments:
        print("BEHAVIORAL_STOP_LOGIC FAIL: no stop-button class found")
        sys.exit(1)

    # Check if there's any conditional logic involving is_recording and onclear together
    # Look for: if (is_recording) { ... } else { ... onclear ... }
    conditional_pattern = r'\bif\s*\(\s*is_recording\s*\).*?\{[^}]*\}\s*else\s*\{[^}]*onclear'
    if re.search(conditional_pattern, content_no_comments, re.DOTALL):
        print("BEHAVIORAL_STOP_LOGIC PASS: found if/else structure with is_recording and onclear")
        sys.exit(0)

    print("BEHAVIORAL_STOP_LOGIC FAIL: stop button found but missing conditional is_recording/onclear logic")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_stop_logic]=1
    echo "TEST behavioral_stop_logic: PASS"
else
    echo "TEST behavioral_stop_logic: FAIL"
fi

# ---------- SUPPLEMENTARY (15%): Structural - startMic error handling ----------
# [pr_diff] (0.15): startMic() must have .catch() or try/catch error handling
python3 << 'PYEOF'
import sys
import re

def extract_script_content(filepath):
    """Extract content inside <script> tags, filtering comments."""
    with open(filepath) as f:
        content = f.read()

    script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        return None

    script_content = script_match.group(1)

    # Remove comments
    script_no_comments = re.sub(r'//.*?$', '', script_content, flags=re.MULTILINE)
    script_no_comments = re.sub(r'/\*.*?\*/', '', script_no_comments, flags=re.DOTALL)

    return script_no_comments

script_content = extract_script_content("/workspace/gradio/js/audio/shared/MinimalAudioRecorder.svelte")
if script_content is None:
    print("STRUCTURAL_ERROR_HANDLING FAIL: no <script> tag found")
    sys.exit(1)

# Check for startMic().catch() pattern
has_dot_catch = bool(re.search(r'startMic\s*\([^)]*\)\s*\.\s*catch\s*\(', script_content))

# Check for try { ... startMic ... } catch pattern
try_catch_pattern = r'try\s*\{[^}]*startMic.*?\}\s*catch\s*\('
has_try_catch = bool(re.search(try_catch_pattern, script_content, re.DOTALL))

# Also check for async/await with try/catch
async_try_pattern = r'try\s*\{[^}]*await\s+startMic.*?\}\s*catch\s*\('
has_async_try_catch = bool(re.search(async_try_pattern, script_content, re.DOTALL))

if has_dot_catch:
    print("STRUCTURAL_ERROR_HANDLING PASS: startMic has .catch() error handling")
    sys.exit(0)
elif has_try_catch or has_async_try_catch:
    print("STRUCTURAL_ERROR_HANDLING PASS: startMic has try/catch error handling")
    sys.exit(0)
else:
    print("STRUCTURAL_ERROR_HANDLING FAIL: no error handling for startMic")
    print("  (Expected: startMic().catch(...) or try { await startMic() } catch (...))")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural_error_handling]=1
    echo "TEST structural_error_handling: PASS"
else
    echo "TEST structural_error_handling: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
# [agent_config] (0.20): Files must have substantial implementation, not stubs
python3 << 'PYEOF'
import sys
import re

def check_substantial_svelte(filepath, min_script_lines=20, min_meaningful_nodes=10):
    """
    Check that a Svelte file has substantial implementation.
    Counts actual AST nodes, not just lines (resistant to comment padding).
    """
    with open(filepath) as f:
        content = f.read()

    # Extract script content
    script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        return False, "no script tag"

    script_content = script_match.group(1)

    # Remove empty lines and comments for line count
    lines = script_content.split('\n')
    non_empty_lines = [l for l in lines if l.strip() and not l.strip().startswith('//')]

    if len(non_empty_lines) < min_script_lines:
        return False, f"only {len(non_empty_lines)} non-empty script lines (min {min_script_lines})"

    # Count meaningful JavaScript constructs (not just declarations)
    meaningful_patterns = [
        (r'\bfunction\s+\w+\s*\(', "function definitions"),
        (r'=>\s*\{', "arrow functions with body"),
        (r'\.\s*(then|catch|finally)\s*\(', "promise chains"),
        (r'\bimport\s+\{[^}]+\}', "named imports"),
        (r'\bif\s*\([^)]+\)', "if statements"),
        (r'\bfor\s*\(|\bwhile\s*\(', "loops"),
        (r'\basync\s+function|\basync\s+\(', "async operations"),
        (r'\.\s*(addEventListener|on\w+)\s*\(', "event handlers"),
        (r'\$effect\s*\(|\$derived\s*\(', "Svelte 5 runes"),
        (r'create\w+\(|new\s+\w+\(', "object instantiation"),
    ]

    total_meaningful = 0
    details = []
    for pattern, desc in meaningful_patterns:
        matches = len(re.findall(pattern, script_content))
        if matches > 0:
            total_meaningful += matches
            details.append(f"{matches}x {desc}")

    if total_meaningful < min_meaningful_nodes:
        return False, f"only {total_meaningful} meaningful constructs (min {min_meaningful_nodes}): {details}"

    return True, f"{len(non_empty_lines)} lines, {total_meaningful} constructs: {details}"

# Check recorder
recorder_ok, recorder_msg = check_substantial_svelte("/workspace/gradio/js/audio/shared/MinimalAudioRecorder.svelte")
print(f"  Recorder: {recorder_msg}")

# Check player
player_ok, player_msg = check_substantial_svelte("/workspace/gradio/js/audio/shared/MinimalAudioPlayer.svelte", min_script_lines=15, min_meaningful_nodes=8)
print(f"  Player: {player_msg}")

if recorder_ok and player_ok:
    print("ANTISTUB PASS: both files have substantial implementation")
    sys.exit(0)
else:
    print("ANTISTUB FAIL: one or both files appear to be stubs")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {
    'behavioral_recorder_state': ${WEIGHT_BEHAVIORAL_RECORDER_STATE},
    'behavioral_player_state': ${WEIGHT_BEHAVIORAL_PLAYER_STATE},
    'behavioral_stop_logic': ${WEIGHT_BEHAVIORAL_STOP_LOGIC},
    'structural_error_handling': ${WEIGHT_STRUCTURAL_ERROR_HANDLING},
    'antistub': ${WEIGHT_ANTISTUB}
}
results = {
    'behavioral_recorder_state': ${RESULTS[behavioral_recorder_state]},
    'behavioral_player_state': ${RESULTS[behavioral_player_state]},
    'behavioral_stop_logic': ${RESULTS[behavioral_stop_logic]},
    'structural_error_handling': ${RESULTS[structural_error_handling]},
    'antistub': ${RESULTS[antistub]}
}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")

# Write detailed breakdown
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_recorder_state  (${WEIGHT_BEHAVIORAL_RECORDER_STATE}): ${RESULTS[behavioral_recorder_state]}"
echo "  behavioral_player_state    (${WEIGHT_BEHAVIORAL_PLAYER_STATE}): ${RESULTS[behavioral_player_state]}"
echo "  behavioral_stop_logic      (${WEIGHT_BEHAVIORAL_STOP_LOGIC}): ${RESULTS[behavioral_stop_logic]}"
echo "  structural_error_handling  (${WEIGHT_STRUCTURAL_ERROR_HANDLING}): ${RESULTS[structural_error_handLING]}"
echo "  antistub                   (${WEIGHT_ANTISTUB}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"

# Write reward.json with breakdown
cat > "${REWARD_FILE%.txt}.json" << EOF
{
  "reward": $SCORE,
  "behavioral_recorder_state": ${RESULTS[behavioral_recorder_state]},
  "behavioral_player_state": ${RESULTS[behavioral_player_state]},
  "behavioral_stop_logic": ${RESULTS[behavioral_stop_logic]},
  "structural_error_handling": ${RESULTS[structural_error_handling]},
  "antistub": ${RESULTS[antistub]}
}
EOF

echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
