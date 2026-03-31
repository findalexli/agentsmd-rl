#!/usr/bin/env bash
set +e

PATCH_FILE="/workspace/slime/docker/patch/latest/sglang.patch"
SCORE=0
LOGS="/logs/verifier"
mkdir -p "$LOGS"

log() { echo "$1" | tee -a "$LOGS/details.txt"; }

########################################################################
# GATE: Patch file exists and modifies deepseek_v2.py
# [pr_diff] (0.00): Gate — patch must exist and target the correct file
########################################################################
log "=== GATE: Patch file validity ==="
if [ ! -f "$PATCH_FILE" ]; then
    log "FAIL: $PATCH_FILE does not exist"
    echo "0.0" > "$LOGS/reward.txt"
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"structural":0.0}' > "$LOGS/reward.json"
    exit 0
fi
if ! grep -q 'deepseek_v2.py' "$PATCH_FILE"; then
    log "FAIL: Patch does not modify deepseek_v2.py"
    echo "0.0" > "$LOGS/reward.txt"
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"structural":0.0}' > "$LOGS/reward.json"
    exit 0
fi
log "PASS: Patch file valid"

########################################################################
# Helper: extract the deepseek_v2.py diff section and reconstruct
# the "new" code lines (context + additions, skip removals).
# Returns lines with their original indentation preserved.
########################################################################
DSV2_NEW_CODE=$(python3 <<'PYEOF'
import sys

with open("/workspace/slime/docker/patch/latest/sglang.patch") as f:
    content = f.read()

marker = "python/sglang/srt/models/deepseek_v2.py"
sections = content.split("diff --git ")
dsv2 = ""
for s in sections:
    first_line = s.split("\n")[0]
    if marker in first_line:
        dsv2 = s
        break

if not dsv2:
    sys.exit(1)

# Reconstruct "new" code from all hunks
for line in dsv2.split("\n"):
    if line.startswith("@@") or line.startswith("diff ") or line.startswith("index ") \
       or line.startswith("--- ") or line.startswith("+++ ") or line.startswith("\\"):
        continue
    if line.startswith("-"):
        continue  # removed line — skip
    elif line.startswith("+"):
        print(line[1:])  # added line — strip "+"
    elif line.startswith(" "):
        print(line[1:])  # context line — strip leading space
    # else: skip non-patch lines
PYEOF
)

if [ -z "$DSV2_NEW_CODE" ]; then
    log "FAIL: Could not extract deepseek_v2.py section from patch"
    echo "0.0" > "$LOGS/reward.txt"
    echo '{"reward":0.0}' > "$LOGS/reward.json"
    exit 0
fi

# Also get the ORIGINAL (buggy) patch for fail-to-pass comparison
ORIG_PATCH_CODE=$(cd /workspace/slime && git show HEAD:docker/patch/latest/sglang.patch 2>/dev/null || echo "")

########################################################################
# FAIL-TO-PASS (0.40): skip_topk/next_skip_topk accessible without use_nsa
# [pr_diff] (0.40): Core bug — these attrs must not require use_nsa=True
# This is a GATE: if it fails, total score is 0.
#
# Accepts multiple valid fix strategies:
#   - Move init before "if self.use_nsa:" (gold approach)
#   - Add "else:" branch after use_nsa that sets defaults
#   - Use getattr(self, 'skip_topk', False) in forward_absorb_prepare
#   - Use hasattr check before accessing
#   - Class-level attribute defaults
########################################################################
log ""
log "=== F2P: skip_topk/next_skip_topk unconditional (0.40, gate) ==="

F2P_RESULT=$(python3 - "$ORIG_PATCH_CODE" <<'PYEOF'
import sys

# Read the current (agent-modified) patch
with open("/workspace/slime/docker/patch/latest/sglang.patch") as f:
    current_content = f.read()

# Read the original (buggy) patch from stdin-ish (passed as arg)
# We'll also read it from git to confirm the bug exists
orig_content = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else ""

def extract_dsv2_new_lines(patch_content):
    """Extract new-code lines from deepseek_v2.py section of a patch."""
    marker = "python/sglang/srt/models/deepseek_v2.py"
    sections = patch_content.split("diff --git ")
    dsv2 = ""
    for s in sections:
        if marker in s.split("\n")[0]:
            dsv2 = s
            break
    if not dsv2:
        return []
    lines = []
    in_hunk = False
    for line in dsv2.split("\n"):
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("-") and not line.startswith("---"):
            continue
        elif line.startswith("+"):
            lines.append(line[1:])
        elif line.startswith("\\"):
            continue
        elif line.startswith(" "):
            lines.append(line[1:])
        else:
            lines.append(line)
    return lines

def check_skip_topk_unconditional(lines):
    """
    Check if skip_topk/next_skip_topk are accessible without use_nsa.
    Returns (skip_ok, next_ok, method) where method describes the approach.
    """
    skip_ok = False
    next_ok = False
    method = ""

    # Track indentation context
    use_nsa_indent = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())

        # Detect the use_nsa conditional
        if ("if self.use_nsa:" in stripped or "if self.use_nsa " in stripped) \
           and "not" not in stripped.split("use_nsa")[0]:
            use_nsa_indent = indent

        # Strategy 1: Unconditional init (before or at same level as use_nsa)
        if "self.skip_topk" in stripped and "=" in stripped and "==" not in stripped:
            if use_nsa_indent is None:
                skip_ok = True
                method = "init_before_use_nsa"
            elif indent <= use_nsa_indent:
                skip_ok = True
                method = "init_at_same_level"

        if "self.next_skip_topk" in stripped and "=" in stripped and "==" not in stripped:
            if use_nsa_indent is None:
                next_ok = True
            elif indent <= use_nsa_indent:
                next_ok = True

    # Strategy 2: Safe access via getattr/hasattr in forward methods
    for line in lines:
        s = line.strip()
        if "getattr" in s and "skip_topk" in s:
            skip_ok = True
            method = "getattr_safe_access"
        if "getattr" in s and "next_skip_topk" in s:
            next_ok = True
        if "hasattr" in s and "skip_topk" in s:
            skip_ok = True
            method = "hasattr_guard"
        if "hasattr" in s and "next_skip_topk" in s:
            next_ok = True

    # Strategy 3: try/except around attribute access
    in_try = False
    for line in lines:
        s = line.strip()
        if s.startswith("try:"):
            in_try = True
        if in_try and ("skip_topk" in s or "except" in s and "Attribute" in s):
            skip_ok = True
            next_ok = True
            method = "try_except_guard"
            break

    return skip_ok, next_ok, method

# First verify the bug EXISTS in the original patch
if orig_content:
    orig_lines = extract_dsv2_new_lines(orig_content)
    orig_skip, orig_next, _ = check_skip_topk_unconditional(orig_lines)
    if orig_skip and orig_next:
        # Bug doesn't exist in original? This shouldn't happen.
        # Still proceed — maybe the original was already partially fixed
        pass

# Now check the current (agent-modified) patch
current_lines = extract_dsv2_new_lines(current_content)
if not current_lines:
    print("FAIL:no_dsv2_section")
    sys.exit(0)

skip_ok, next_ok, method = check_skip_topk_unconditional(current_lines)

if skip_ok and next_ok:
    print(f"PASS:{method}")
elif not skip_ok:
    print("FAIL:skip_topk_still_conditional")
else:
    print("FAIL:next_skip_topk_still_conditional")
PYEOF
)

if [[ "$F2P_RESULT" == PASS* ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.40)")
    log "PASS: skip_topk/next_skip_topk accessible without use_nsa ($F2P_RESULT)"
else
    log "FAIL (GATE): $F2P_RESULT — core bug not fixed, total score = 0"
    echo "0.0" > "$LOGS/reward.txt"
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"structural":0.0}' > "$LOGS/reward.json"
    exit 0
fi

########################################################################
# PASS-TO-PASS 1 (0.15): Config attributes preserved in the patch
# [pr_diff] (0.15): index_topk_freq, index_topk_pattern, index_skip_topk_offset
# must still be set somewhere in the deepseek_v2.py section
########################################################################
log ""
log "=== P2P 1: Config attributes preserved (0.15) ==="

P2P1_RESULT=$(python3 <<'PYEOF'
with open("/workspace/slime/docker/patch/latest/sglang.patch") as f:
    content = f.read()

marker = "python/sglang/srt/models/deepseek_v2.py"
sections = content.split("diff --git ")
dsv2 = ""
for s in sections:
    if marker in s.split("\n")[0]:
        dsv2 = s
        break

if not dsv2:
    print("FAIL:no_dsv2")
    import sys; sys.exit(0)

# These config attrs must still be present (not deleted by the agent)
required = ["index_topk_freq", "index_topk_pattern", "index_skip_topk_offset"]
missing = [r for r in required if r not in dsv2]

if missing:
    print(f"FAIL:missing_{','.join(missing)}")
else:
    # Verify they appear in added/context lines (not just removed lines)
    new_lines = []
    in_hunk = False
    for line in dsv2.split("\n"):
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("-"):
            continue
        new_lines.append(line)
    new_text = "\n".join(new_lines)
    still_missing = [r for r in required if r not in new_text]
    if still_missing:
        print(f"FAIL:deleted_{','.join(still_missing)}")
    else:
        print("PASS")
PYEOF
)

if [ "$P2P1_RESULT" = "PASS" ]; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    log "PASS: Config attributes preserved"
else
    log "FAIL: $P2P1_RESULT"
fi

########################################################################
# PASS-TO-PASS 2 (0.15): forward_absorb_prepare skip logic preserved
# [pr_diff] (0.15): The method must still conditionally skip the indexer
# and use prev_topk_indices as a fallback
########################################################################
log ""
log "=== P2P 2: forward_absorb_prepare skip logic (0.15) ==="

P2P2_RESULT=$(python3 <<'PYEOF'
with open("/workspace/slime/docker/patch/latest/sglang.patch") as f:
    content = f.read()

marker = "python/sglang/srt/models/deepseek_v2.py"
sections = content.split("diff --git ")
dsv2 = ""
for s in sections:
    if marker in s.split("\n")[0]:
        dsv2 = s
        break

if not dsv2:
    print("FAIL:no_dsv2")
    import sys; sys.exit(0)

# Extract non-removed lines
new_lines = []
in_hunk = False
for line in dsv2.split("\n"):
    if line.startswith("@@"):
        in_hunk = True
        continue
    if not in_hunk:
        continue
    if line.startswith("-"):
        continue
    new_lines.append(line)
new_text = "\n".join(new_lines)

# Check that skip logic elements are present (any valid form)
has_skip_ref = "skip_topk" in new_text
has_prev_topk = "prev_topk_indices" in new_text
# Accept: "if not self.skip_topk:", "if self.skip_topk:", "getattr(...skip_topk...)", etc.
has_conditional = ("if not self.skip_topk" in new_text or
                   "if self.skip_topk" in new_text or
                   "getattr" in new_text and "skip_topk" in new_text or
                   "hasattr" in new_text and "skip_topk" in new_text)

if has_skip_ref and has_prev_topk and has_conditional:
    print("PASS")
elif not has_skip_ref:
    print("FAIL:no_skip_topk_reference")
elif not has_prev_topk:
    print("FAIL:no_prev_topk_indices")
else:
    print("FAIL:no_skip_conditional")
PYEOF
)

if [ "$P2P2_RESULT" = "PASS" ]; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    log "PASS: forward_absorb_prepare skip logic preserved"
else
    log "FAIL: $P2P2_RESULT"
fi

########################################################################
# PASS-TO-PASS 3 (0.15): Return value includes topk_indices for caching
# [pr_diff] (0.15): forward_absorb_prepare must return topk data
########################################################################
log ""
log "=== P2P 3: Return includes topk_indices (0.15) ==="

P2P3_RESULT=$(python3 <<'PYEOF'
with open("/workspace/slime/docker/patch/latest/sglang.patch") as f:
    content = f.read()

marker = "python/sglang/srt/models/deepseek_v2.py"
sections = content.split("diff --git ")
dsv2 = ""
for s in sections:
    if marker in s.split("\n")[0]:
        dsv2 = s
        break

if not dsv2:
    print("FAIL:no_dsv2")
    import sys; sys.exit(0)

# Check non-removed lines for return tuple
new_lines = []
in_hunk = False
for line in dsv2.split("\n"):
    if line.startswith("@@"):
        in_hunk = True
        continue
    if not in_hunk:
        continue
    if line.startswith("-"):
        continue
    new_lines.append(line)
new_text = "\n".join(new_lines)

# Accept any form of returning topk_indices:
# "return output, topk_indices", "return (output, topk_indices)",
# "return output, None", "return result, indices", etc.
# The key: there must be a return that includes topk-related data
has_tuple_return = False
for line in new_lines:
    s = line.strip()
    if s.startswith("return ") and "topk" in s and "," in s:
        has_tuple_return = True
        break
    if s.startswith("return ") and "None" in s and "," in s and "output" in s:
        has_tuple_return = True
        break
    if s.startswith("return (") and "topk" in s:
        has_tuple_return = True
        break

# Also check next_skip_topk is used to control when indices are returned
has_next_skip = "next_skip_topk" in new_text

if has_tuple_return and has_next_skip:
    print("PASS")
elif not has_tuple_return:
    print("FAIL:no_tuple_return_with_topk")
else:
    print("FAIL:no_next_skip_topk_logic")
PYEOF
)

if [ "$P2P3_RESULT" = "PASS" ]; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    log "PASS: Return value includes topk_indices"
else
    log "FAIL: $P2P3_RESULT"
fi

########################################################################
# STRUCTURAL (0.10): DecoderLayer properly threads topk_indices
# [pr_diff] (0.10): DecoderLayer must pass/unpack topk_indices across layers
########################################################################
log ""
log "=== STRUCTURAL: DecoderLayer threads topk_indices (0.10) ==="

S1_RESULT=$(python3 <<'PYEOF'
with open("/workspace/slime/docker/patch/latest/sglang.patch") as f:
    content = f.read()

marker = "python/sglang/srt/models/deepseek_v2.py"
sections = content.split("diff --git ")
dsv2 = ""
for s in sections:
    if marker in s.split("\n")[0]:
        dsv2 = s
        break

if not dsv2:
    print("FAIL:no_dsv2")
    import sys; sys.exit(0)

new_lines = []
in_hunk = False
for line in dsv2.split("\n"):
    if line.startswith("@@"):
        in_hunk = True
        continue
    if not in_hunk:
        continue
    if line.startswith("-"):
        continue
    new_lines.append(line)
new_text = "\n".join(new_lines)

# DecoderLayer must return topk_indices and model must unpack it
# Accept various tuple forms and variable names
has_layer_return = False
has_unpack = False

for line in new_lines:
    s = line.strip()
    # Return 3-tuple from decoder layer
    if s.startswith("return ") and "hidden_states" in s and "residual" in s and "topk" in s:
        has_layer_return = True
    # Unpack 3-tuple from layer call
    if "topk" in s and "residual" in s and "= layer(" in s:
        has_unpack = True
    if "topk" in s and "residual" in s and "hidden_states" in s and "=" in s:
        has_unpack = True

if has_layer_return and has_unpack:
    print("PASS")
elif not has_layer_return:
    print("FAIL:no_layer_3tuple_return")
else:
    print("FAIL:no_3tuple_unpack")
PYEOF
)

if [ "$S1_RESULT" = "PASS" ]; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    log "PASS: DecoderLayer threads topk_indices"
else
    log "FAIL: $S1_RESULT"
fi

########################################################################
# ANTI-STUB (0.05): Patch diff is non-trivial
# [pr_diff] (0.05): Agent must have made meaningful changes
########################################################################
log ""
log "=== ANTI-STUB: Non-trivial patch changes (0.05) ==="

# Compare current patch against original to count actual changes
CHANGE_COUNT=$(cd /workspace/slime && git diff -- docker/patch/latest/sglang.patch 2>/dev/null | grep -c '^[+-]' || echo "0")
if [ "$CHANGE_COUNT" -gt 3 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    log "PASS: $CHANGE_COUNT changed lines in the patch diff"
else
    log "FAIL: Only $CHANGE_COUNT changed lines — insufficient changes"
fi

########################################################################
# Final score
########################################################################
log ""
log "=== FINAL ==="
log "Score: $SCORE / 1.00"

FINAL=$(python3 -c "print(max(0.0, min(1.0, round($SCORE, 4))))")
echo "$FINAL" > "$LOGS/reward.txt"

# Compute category breakdowns
python3 -c "
import json
reward = round(float('$SCORE'), 4)
data = {
    'reward': reward,
    'behavioral': round(min(0.40, float('$SCORE')), 4),
    'regression': round(max(0.0, min(0.45, float('$SCORE') - 0.40)), 4),
    'structural': round(max(0.0, min(0.15, float('$SCORE') - 0.85)), 4)
}
print(json.dumps(data))
" > "$LOGS/reward.json" 2>/dev/null || true

log "Reward: $FINAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
