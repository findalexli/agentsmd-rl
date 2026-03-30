#!/usr/bin/env bash
set +e

TARGET="/workspace/openclaw/extensions/discord/src/monitor/provider.lifecycle.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.40
WEIGHTS[regression]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.10
WEIGHTS[config_boundary]=0.05

for key in behavioral regression structural antistub config_boundary; do
    RESULTS[$key]=0
done

if [ ! -f "$TARGET" ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi

# ---------- PRIMARY 1 (40%): reconnect-exhausted no longer gated by lifecycleStopping ----------
python3 << 'PYEOF'
import sys, re
with open("/workspace/openclaw/extensions/discord/src/monitor/provider.lifecycle.ts") as f:
    src = f.read()

# The bug: reconnect-exhausted only suppressed when lifecycleStopping is true
# Pattern: lifecycleStopping && event.type === "reconnect-exhausted"
buggy = re.search(r'lifecycleStopping\s*&&\s*event\.type\s*===?\s*["\']reconnect-exhausted["\']', src)
if buggy:
    print("BEHAVIORAL FAIL: reconnect-exhausted still gated by lifecycleStopping")
    sys.exit(1)

# The fix should have event.type === "reconnect-exhausted" without lifecycleStopping gate
if 'reconnect-exhausted' not in src:
    print("BEHAVIORAL FAIL: reconnect-exhausted handling removed entirely")
    sys.exit(1)

print("BEHAVIORAL PASS: reconnect-exhausted not gated by lifecycleStopping")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): regression - disallowed-intents still handled ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/extensions/discord/src/monitor/provider.lifecycle.ts") as f:
    src = f.read()
if "disallowed-intents" not in src:
    print("REGRESSION FAIL: disallowed-intents handling removed"); sys.exit(1)
if "runDiscordGatewayLifecycle" not in src:
    print("REGRESSION FAIL: main function removed"); sys.exit(1)
print("REGRESSION PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[regression]=1 && echo "TEST regression: PASS" || echo "TEST regression: FAIL"

# ---------- SUPPLEMENTARY (20%): structural ----------
python3 << 'PYEOF'
import sys, re
with open("/workspace/openclaw/extensions/discord/src/monitor/provider.lifecycle.ts") as f:
    src = f.read()
# Should have: event.type === "reconnect-exhausted" as a standalone condition
pattern = re.search(r'event\.type\s*===?\s*["\']reconnect-exhausted["\']', src)
if not pattern:
    print("STRUCTURAL FAIL: reconnect-exhausted check not found"); sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (15%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/extensions/discord/src/monitor/provider.lifecycle.ts") as f:
    src = f.read()
ok = all(["export" in src, "runDiscordGatewayLifecycle" in src, len(src.splitlines()) > 30])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"


# ---------- Config-derived test (0.05): "Extension code must import from plugin-sdk/*" ----------
# Source: CLAUDE.md line 16 @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find extensions/discord/src -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
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
w={'behavioral':${WEIGHTS[behavioral],'config_boundary':${WEIGHTS[config_boundary]}},'regression':${WEIGHTS[regression]},'structural':${WEIGHTS[structural]},'antistub':${WEIGHTS[antistub]}}
r={'behavioral':${RESULTS[behavioral],'config_boundary':${RESULTS[config_boundary]}},'regression':${RESULTS[regression]},'structural':${RESULTS[structural]},'antistub':${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
