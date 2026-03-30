#!/usr/bin/env bash
set +e

TARGET="/workspace/openclaw/src/plugins/tools.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.40
WEIGHTS[regression]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.10
WEIGHTS[config_nocheck]=0.05

for key in behavioral regression structural antistub config_nocheck; do
    RESULTS[$key]=0
done

if [ ! -f "$TARGET" ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi

# ---------- PRIMARY 1 (40%): getActivePluginRegistry used as fallback ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/src/plugins/tools.ts") as f: src = f.read()
if "getActivePluginRegistry" not in src:
    print("BEHAVIORAL FAIL: getActivePluginRegistry not imported/used"); sys.exit(1)
if "allowGatewaySubagentBinding" not in src:
    print("BEHAVIORAL FAIL: allowGatewaySubagentBinding check not found"); sys.exit(1)
print("BEHAVIORAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): regression ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/src/plugins/tools.ts") as f: src = f.read()
ok = all(["resolvePluginTools" in src, "resolveRuntimePluginRegistry" in src, len(src.splitlines()) > 30])
if not ok: print("REGRESSION FAIL"); sys.exit(1)
print("REGRESSION PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[regression]=1 && echo "TEST regression: PASS" || echo "TEST regression: FAIL"

# ---------- SUPPLEMENTARY (20%): structural ----------
python3 << 'PYEOF'
import sys, re
with open("/workspace/openclaw/src/plugins/tools.ts") as f: src = f.read()
# Should have a helper that checks gateway scope and falls back
if "getActivePluginRegistry()" not in src:
    print("STRUCTURAL FAIL: no getActivePluginRegistry() call"); sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (15%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/src/plugins/tools.ts") as f: src = f.read()
ok = all(["export" in src, "resolvePluginTools" in src, len(src.splitlines()) > 30])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"


# ---------- Config-derived test (0.05): "Never add @ts-nocheck" ----------
# Source: CLAUDE.md line 146 @ 6883f688e8da11481a5d0f91dfab4e4ba6e9f871
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find src/plugins -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
let fail = false;
for (const f of files) {
    try {
        const content = fs.readFileSync(f, 'utf8');
        if (content.includes('@ts-nocheck') || content.includes('@ts-ignore')) {
            console.log('FAIL: ' + f + ' contains @ts-nocheck or @ts-ignore');
            fail = true;
        }
    } catch(e) {}
}
if (fail) process.exit(1);
console.log('PASS: no @ts-nocheck/@ts-ignore found');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[config_nocheck]=1; echo "TEST config_nocheck: PASS"; else echo "TEST config_nocheck: FAIL"; fi

SCORE=$(python3 -c "
w={'behavioral':${WEIGHTS[behavioral],'config_nocheck':${WEIGHTS[config_nocheck]}},'regression':${WEIGHTS[regression]},'structural':${WEIGHTS[structural]},'antistub':${WEIGHTS[antistub]}}
r={'behavioral':${RESULTS[behavioral],'config_nocheck':${RESULTS[config_nocheck]}},'regression':${RESULTS[regression]},'structural':${RESULTS[structural]},'antistub':${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
