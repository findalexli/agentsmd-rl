#!/usr/bin/env bash
set +e

TARGET="/workspace/openclaw/extensions/msteams/src/reply-stream-controller.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.40
WEIGHTS[behavioral2]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.10
WEIGHTS[config_boundary]=0.05

for key in behavioral behavioral2 structural antistub config_boundary; do
    RESULTS[$key]=0
done

if [ ! -f "$TARGET" ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi

# ---------- PRIMARY 1 (40%): streamReceivedTokens is reset in preparePayload ----------
python3 << 'PYEOF'
import sys, re
with open("/workspace/openclaw/extensions/msteams/src/reply-stream-controller.ts") as f:
    src = f.read()

# Find preparePayload method body
pp_match = re.search(r'preparePayload\s*\([^)]*\)[^{]*\{', src)
if not pp_match:
    print("BEHAVIORAL FAIL: preparePayload not found"); sys.exit(1)

# Check that streamReceivedTokens is reset to false within preparePayload
# Look for the reset after the suppression
pp_start = pp_match.start()
pp_section = src[pp_start:pp_start+1500]  # reasonable window

if "streamReceivedTokens = false" not in pp_section and "streamReceivedTokens=false" not in pp_section:
    print("BEHAVIORAL FAIL: streamReceivedTokens not reset in preparePayload")
    sys.exit(1)

print("BEHAVIORAL PASS: streamReceivedTokens reset in preparePayload")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): isFinalized guard ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/extensions/msteams/src/reply-stream-controller.ts") as f:
    src = f.read()
if "isFinalized" not in src:
    print("BEHAVIORAL2 FAIL: isFinalized guard not found"); sys.exit(1)
if "finalize" not in src:
    print("BEHAVIORAL2 FAIL: finalize call not found"); sys.exit(1)
print("BEHAVIORAL2 PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral2]=1 && echo "TEST behavioral2: PASS" || echo "TEST behavioral2: FAIL"

# ---------- SUPPLEMENTARY (20%): structural ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/extensions/msteams/src/reply-stream-controller.ts") as f:
    src = f.read()
if "preparePayload" not in src:
    print("STRUCTURAL FAIL"); sys.exit(1)
if "onPartialReply" not in src:
    print("STRUCTURAL FAIL"); sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (15%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/extensions/msteams/src/reply-stream-controller.ts") as f:
    src = f.read()
ok = all(["export" in src, "createTeamsReplyStreamController" in src, len(src.splitlines()) > 30])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"


# ---------- Config-derived test (0.05): "Extension code must import from plugin-sdk/*" ----------
# Source: CLAUDE.md line 16 @ 4752aca926624efdeb62f2f43b606f5090be8903
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find extensions/msteams/src -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
let fail = false;
for (const f of files) {
    const content = fs.readFileSync(f, 'utf8');
    const lines = content.split('\\n');
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (/^import .* from ['\"]\.\.\/\.\.\/\.\.\/src\//.test(line)) {
            console.log('FAIL: ' + f + ':' + (i+1) + ' imports core internals: ' + line.trim());
            fail = true;
        }
    }
}
if (fail) process.exit(1);
console.log('PASS: no cross-boundary imports');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[config_boundary]=1; echo "TEST config_boundary: PASS"; else echo "TEST config_boundary: FAIL"; fi

SCORE=$(python3 -c "
w={'behavioral':${WEIGHTS[behavioral],'config_boundary':${WEIGHTS[config_boundary]}},'behavioral2':${WEIGHTS[behavioral2]},'structural':${WEIGHTS[structural]},'antistub':${WEIGHTS[antistub]}}
r={'behavioral':${RESULTS[behavioral],'config_boundary':${RESULTS[config_boundary]}},'behavioral2':${RESULTS[behavioral2]},'structural':${RESULTS[structural]},'antistub':${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
