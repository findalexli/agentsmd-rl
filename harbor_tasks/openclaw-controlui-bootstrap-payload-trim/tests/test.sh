#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight="$1" pass="$2" tag="$3" desc="$4"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}PASS ($weight) [$tag]: $desc\n"
    else
        DETAILS="${DETAILS}FAIL ($weight) [$tag]: $desc\n"
    fi
}

REPO="/workspace/openclaw"

# ========== GATE: TypeScript files compile / required files exist ==========
# [pr_diff] (0): Modified files must exist

GATE_PASS=1
for f in \
    "$REPO/src/gateway/control-ui-contract.ts" \
    "$REPO/src/gateway/control-ui.ts" \
    "$REPO/ui/src/ui/controllers/control-ui-bootstrap.ts" \
    "$REPO/ui/vite.config.ts"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f does not exist"
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" = "0" ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    echo "GATE FAILED: required files missing"
    exit 0
fi

# ========== Install dependencies ==========
cd "$REPO"
npm install --ignore-scripts --no-audit --no-fund --loglevel=error 2>/dev/null
cd "$REPO/ui"
npm install --ignore-scripts --no-audit --no-fund --loglevel=error 2>/dev/null
cd "$REPO"

# ========== BEHAVIORAL: Fail-to-pass — gateway handler test ==========
# These tests exercise the actual HTTP handler and assert the bootstrap
# payload shape. The repo's test files at the base commit assert the OLD
# behavior, so we patch them to assert the CORRECT behavior first —
# making them genuine fail-to-pass tests.

# Patch gateway test: expect bootstrap payload to NOT have extra fields
cd "$REPO"
python3 - <<'PYEOF'
import re, pathlib

# --- Gateway HTTP test ---
gw = pathlib.Path("src/gateway/control-ui.http.test.ts")
src = gw.read_text()

# Remove assistantAgentId from the parsed type alias
src = re.sub(r'\n\s*assistantAgentId:\s*string;\n', '\n', src)

# Replace positive assertions with negative ones
src = src.replace(
    'expect(parsed.assistantAgentId).toBe("main")',
    'expect(parsed).not.toHaveProperty("assistantAgentId");\n        expect(parsed).not.toHaveProperty("serverVersion")'
)
gw.write_text(src)

# --- UI bootstrap controller test ---
ui = pathlib.Path("ui/src/ui/controllers/control-ui-bootstrap.test.ts")
src = ui.read_text()

# Remove extra fields from mock response
src = re.sub(r'\n\s*assistantAgentId:\s*"main",\n', '\n', src)
src = re.sub(r'\n\s*serverVersion:\s*"2026\.3\.7",\n', '\n', src)

# Replace positive assertions with null checks
src = src.replace(
    'expect(state.assistantAgentId).toBe("main")',
    'expect(state.assistantAgentId).toBeNull()'
)
src = src.replace(
    'expect(state.serverVersion).toBe("2026.3.7")',
    'expect(state.serverVersion).toBeNull()'
)

# Add null assertions after assistantName checks in test blocks that don't have them
# (the "ignores failures" and "normalizes trailing slash" blocks)
lines = src.split('\n')
new_lines = []
i = 0
while i < len(lines):
    new_lines.append(lines[i])
    # After 'expect(state.assistantName).toBe("Assistant")' add null checks if not already present
    if 'expect(state.assistantName).toBe("Assistant")' in lines[i]:
        indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
        # Check if next non-empty line already has the null assertions
        j = i + 1
        while j < len(lines) and lines[j].strip() == '':
            j += 1
        if j < len(lines) and 'assistantAgentId' not in lines[j]:
            new_lines.append(f'{indent}expect(state.assistantAgentId).toBeNull();')
            new_lines.append(f'{indent}expect(state.serverVersion).toBeNull();')
    # After 'expect.objectContaining({ method: "GET" }),' blocks followed by non-null-assertion lines
    if 'normalizes trailing slash' in lines[i] if False else False:
        pass
    i += 1
src = '\n'.join(new_lines)
ui.write_text(src)
PYEOF

# [pr_diff] (0.35): Gateway handler test — bootstrap payload has no extra fields
npx vitest run src/gateway/control-ui.http.test.ts --reporter=verbose --no-color 2>&1 | tee /tmp/gw_test.log
GW_EXIT=${PIPESTATUS[0]}
if [ "$GW_EXIT" = "0" ]; then
    add_result 0.35 1 "pr_diff" "Gateway handler test passes (bootstrap payload trimmed)"
else
    add_result 0.35 0 "pr_diff" "Gateway handler test fails"
fi

# [pr_diff] (0.25): UI bootstrap controller test — state no longer stores removed fields
cd "$REPO/ui"
npx vitest run src/ui/controllers/control-ui-bootstrap.test.ts --reporter=verbose --no-color 2>&1 | tee /tmp/ui_test.log
UI_EXIT=${PIPESTATUS[0]}
if [ "$UI_EXIT" = "0" ]; then
    add_result 0.25 1 "pr_diff" "UI bootstrap test passes (removed fields are null)"
else
    add_result 0.25 0 "pr_diff" "UI bootstrap test fails"
fi

# ========== BEHAVIORAL: Payload shape via inline assertion ==========
# Validates that the ControlUiBootstrapConfig type has exactly the
# expected fields — works regardless of HOW the agent removed the extras.

# [pr_diff] (0.15): Contract type has only display-relevant fields
cd "$REPO"
node -e "
const fs = require('fs');
const src = fs.readFileSync('src/gateway/control-ui-contract.ts', 'utf8');

// Parse exported type fields by looking for word: type patterns
// This is intentionally loose — any valid TS type syntax is fine
const hasBasePath = /basePath\s*[:\?]/.test(src);
const hasAssistantName = /assistantName\s*[:\?]/.test(src);
const hasAssistantAvatar = /assistantAvatar\s*[:\?]/.test(src);

// The removed fields should not appear as type members
const hasAgentId = /assistantAgentId\s*[:\?]/.test(src);
const hasServerVersion = /serverVersion\s*[:\?]/.test(src);

const corePresent = hasBasePath && hasAssistantName && hasAssistantAvatar;
const extrasRemoved = !hasAgentId && !hasServerVersion;

if (corePresent && extrasRemoved) {
    process.exit(0);
} else {
    if (!corePresent) console.log('Missing core fields in contract type');
    if (!extrasRemoved) console.log('Extra fields still present in contract type');
    process.exit(1);
}
" 2>&1
if [ $? -eq 0 ]; then
    add_result 0.15 1 "pr_diff" "Contract type has only display-relevant fields"
else
    add_result 0.15 0 "pr_diff" "Contract type still has extra fields or missing core fields"
fi

# ========== PASS-TO-PASS: Core display fields still work ==========

# [pr_diff] (0.10): Handler still references core display fields
P2P_HANDLER=1
cd "$REPO"
node -e "
const fs = require('fs');
const src = fs.readFileSync('src/gateway/control-ui.ts', 'utf8');
const required = ['basePath', 'assistantName', 'assistantAvatar'];
for (const field of required) {
    if (!src.includes(field)) {
        console.log('Missing field: ' + field);
        process.exit(1);
    }
}
" 2>&1
if [ $? -eq 0 ]; then
    add_result 0.10 1 "pr_diff" "Handler still populates core display fields"
else
    add_result 0.10 0 "pr_diff" "Handler missing core display fields"
fi

# ========== STRUCTURAL: Anti-gaming — handler doesn't populate removed fields ==========
# Only worth 0.10 combined; kept as defense-in-depth, not primary signal.

# [pr_diff] (0.05): Handler response object doesn't include assistantAgentId as a property
cd "$REPO"
node -e "
const fs = require('fs');
const src = fs.readFileSync('src/gateway/control-ui.ts', 'utf8');
// Check for assistantAgentId as an object property being assigned
// Matches: assistantAgentId: or assistantAgentId, or 'assistantAgentId' patterns
// in a response-building context. Loose enough to catch any assignment style.
const hasAgentIdProp = /assistantAgentId\s*[,:=]/.test(src);
if (hasAgentIdProp) {
    console.log('Handler still populates assistantAgentId');
    process.exit(1);
}
" 2>&1
if [ $? -eq 0 ]; then
    add_result 0.05 1 "pr_diff" "Handler no longer populates assistantAgentId"
else
    add_result 0.05 0 "pr_diff" "Handler still populates assistantAgentId"
fi

# [pr_diff] (0.05): Handler doesn't resolve server version for bootstrap
node -e "
const fs = require('fs');
const src = fs.readFileSync('src/gateway/control-ui.ts', 'utf8');
const hasVersionResolve = /resolveRuntimeServiceVersion/.test(src);
const hasServerVersionProp = /serverVersion\s*[,:=]/.test(src);
if (hasVersionResolve || hasServerVersionProp) {
    console.log('Handler still resolves or assigns serverVersion');
    process.exit(1);
}
" 2>&1
if [ $? -eq 0 ]; then
    add_result 0.05 1 "pr_diff" "Handler no longer resolves serverVersion"
else
    add_result 0.05 0 "pr_diff" "Handler still resolves serverVersion"
fi

# ========== CONFIG-DERIVED ==========

# [agent_config] (0.05): "Prefer strict typing; avoid any" — CLAUDE.md:144
cd "$REPO"
ANY_FOUND=0
for f in src/gateway/control-ui-contract.ts src/gateway/control-ui.ts ui/src/ui/controllers/control-ui-bootstrap.ts; do
    if git diff HEAD -- "$f" 2>/dev/null | grep -q '^\+.*:\s*any\b'; then
        ANY_FOUND=1
    fi
done
if [ "$ANY_FOUND" = "0" ]; then
    add_result 0.05 1 "agent_config" "No 'any' types introduced — CLAUDE.md:144"
else
    add_result 0.05 0 "agent_config" "New 'any' types found — CLAUDE.md:144"
fi

# ========== Output ==========
echo "========================================="
echo "Test Results"
echo "========================================="
printf "$DETAILS"
echo "========================================="
echo "Score: $SCORE / $TOTAL"
echo "========================================="

# Write reward
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
score = float('$SCORE')
data = {
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.75), 4),
    'regression': round(min(max(score - 0.75, 0), 0.10), 4),
    'structural': round(min(max(score - 0.85, 0), 0.10), 4),
    'config': round(min(max(score - 0.95, 0), 0.05), 4)
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
