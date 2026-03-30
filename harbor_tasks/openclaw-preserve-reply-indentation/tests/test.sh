#!/usr/bin/env bash
set +e

TARGET="/workspace/openclaw/src/utils/directive-tags.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.40
WEIGHTS[behavioral2]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.10
WEIGHTS[config_nocheck]=0.05

for key in behavioral behavioral2 structural antistub config_nocheck; do
    RESULTS[$key]=0
done

if [ ! -f "$TARGET" ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi

# ---------- PRIMARY 1 (40%): normalizeDirectiveWhitespace no longer collapses all spaces ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/src/utils/directive-tags.ts") as f: src = f.read()

# The old aggressive pattern: .replace(/[ \t]+/g, " ") which collapses ALL spaces
if '/ +/g' in src or '/[ \\t]+/g, " "' in src or ".replace(/[ \\t]+/g," in src:
    # Check if it's in normalizeDirectiveWhitespace specifically
    import re
    func_match = re.search(r'function normalizeDirectiveWhitespace.*?\n\}', src, re.DOTALL)
    if func_match:
        func_body = func_match.group(0)
        if '/[ \\t]+/g, " "' in func_body or "replace(/[ \\t]+/g," in func_body:
            print("BEHAVIORAL FAIL: aggressive space collapsing still present")
            sys.exit(1)

# Check the old trim pattern is gone
if '.trim()' in src:
    import re
    func_match = re.search(r'function normalizeDirectiveWhitespace.*?\n\}', src, re.DOTALL)
    if func_match and '.trim()' in func_match.group(0):
        print("BEHAVIORAL FAIL: trim() still in normalizeDirectiveWhitespace")
        sys.exit(1)

print("BEHAVIORAL PASS: aggressive whitespace normalization removed")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): word boundary aware replacement ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/src/utils/directive-tags.ts") as f: src = f.read()

# Should have some kind of word-boundary check for tag replacement
if "\\s" not in src and "boundary" not in src.lower():
    # At minimum check that replacement isn't always " "
    import re
    # Old pattern: return stripAudioTag ? " " : match
    if 'return stripAudioTag ? " " : match' in src:
        print("BEHAVIORAL2 FAIL: audio tag replacement still always inserts space")
        sys.exit(1)
    if 'return stripReplyTags ? " " : match' in src:
        print("BEHAVIORAL2 FAIL: reply tag replacement still always inserts space")
        sys.exit(1)

print("BEHAVIORAL2 PASS: boundary-aware replacement")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral2]=1 && echo "TEST behavioral2: PASS" || echo "TEST behavioral2: FAIL"

# ---------- SUPPLEMENTARY (20%): structural ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/src/utils/directive-tags.ts") as f: src = f.read()
if "normalizeDirectiveWhitespace" not in src:
    print("STRUCTURAL FAIL: function removed"); sys.exit(1)
if "parseInlineDirectives" not in src:
    print("STRUCTURAL FAIL: parseInlineDirectives removed"); sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (15%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/openclaw/src/utils/directive-tags.ts") as f: src = f.read()
ok = all(["export" in src, "parseInlineDirectives" in src, len(src.splitlines()) > 50])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"


# ---------- Config-derived test (0.05): "Never add @ts-nocheck" ----------
# Source: CLAUDE.md line 104 @ 0d0d46f5e95f6f003861be33b4b9c6e3b493ea15
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find src/utils -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
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
w={'behavioral':${WEIGHTS[behavioral],'config_nocheck':${WEIGHTS[config_nocheck]}},'behavioral2':${WEIGHTS[behavioral2]},'structural':${WEIGHTS[structural]},'antistub':${WEIGHTS[antistub]}}
r={'behavioral':${RESULTS[behavioral],'config_nocheck':${RESULTS[config_nocheck]}},'behavioral2':${RESULTS[behavioral2]},'structural':${RESULTS[structural]},'antistub':${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
