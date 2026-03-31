#!/usr/bin/env bash
set +e

REPO="/repo"
TARGET="$REPO/src/bun.js/bindings/BunString.cpp"
TOTAL=0
REWARD_FILE="/logs/verifier/reward.txt"
REWARD_JSON="/logs/verifier/reward.json"

behavioral=0
regression=0
config=0

add_score() {
  local weight="$1"
  local category="$2"
  TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
  case "$category" in
    behavioral) behavioral=$(python3 -c "print(round($behavioral + $weight, 4))") ;;
    regression) regression=$(python3 -c "print(round($regression + $weight, 4))") ;;
    config)     config=$(python3 -c "print(round($config + $weight, 4))") ;;
  esac
}

# ── GATE: Target file exists and is non-empty ──
# [pr_diff] (0): File must exist
if [ ! -s "$TARGET" ]; then
  echo "GATE FAIL: $TARGET missing or empty"
  echo "0.0" > "$REWARD_FILE"
  echo '{"reward":0,"behavioral":0,"regression":0,"config":0}' > "$REWARD_JSON"
  exit 0
fi

# ── Extract the BunString__toJSDOMURL function region (comment-stripped) ──
FUNC_REGION=$(python3 << 'PYEOF'
import re, sys

with open("/repo/src/bun.js/bindings/BunString.cpp") as f:
    content = f.read()

# Strip C/C++ comments
content = re.sub(r'//[^\n]*', '', content)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

# Find BunString__toJSDOMURL function
idx = content.find('BunString__toJSDOMURL')
if idx < 0:
    print('NOTFOUND')
    sys.exit(0)

rest = content[idx:]
func_end = len(rest)
for marker in ['extern "C"', '\nJSC__', '\nBunString__']:
    pos = rest.find(marker, 50)
    if 0 < pos < func_end:
        func_end = pos
func_end = min(func_end, 1500)
print(rest[:func_end])
PYEOF
)

export FUNC_REGION

if [ "$FUNC_REGION" = "NOTFOUND" ]; then
  echo "GATE FAIL: BunString__toJSDOMURL function not found"
  echo "0.0" > "$REWARD_FILE"
  echo '{"reward":0,"behavioral":0,"regression":0,"config":0}' > "$REWARD_JSON"
  exit 0
fi

GATE_PASS=0

# ── Check 1 (0.30): Exception/null guard between toJSNewlyCreated and jsCast ──
# [pr_diff] (0.30): Must handle exception after toJSNewlyCreated before jsCast
# Justification: C++ code requires full Bun build (Zig+CMake+WebKit), cannot execute
CHECK1=$(python3 << 'PYEOF'
import sys, os

region = os.environ.get("FUNC_REGION", "")

jsn = region.find('toJSNewlyCreated')
jsc = region.find('jsCast')
if jsn < 0 or jsc < 0:
    print('broken')
    sys.exit(0)
if jsn > jsc:
    print('broken')
    sys.exit(0)

between = region[jsn:jsc]

# Accept exception/null-related guards only — NOT bare 'if ('
# This prevents gaming via 'if (true)' or any unrelated conditional
exception_patterns = [
    'RETURN_IF_EXCEPTION',
    'throwScope',
    'hasPendingException',
    '.isEmpty()',
    '.isNull()',
    '.isUndefinedOrNull()',
    '!jsValue',
    '== JSValue()',
    '!result',
    'isException',
    'Exception',
    'scope.',
    'EXCEPTION',
]

has_guard = False
for pat in exception_patterns:
    if pat in between:
        has_guard = True
        break

# Also accept: null/validity check on the toJSNewlyCreated return value
# e.g., if (!jsValue), if (jsValue.isEmpty()), if (!result)
# These use a variable capturing the result + a check on it
import re
# Pattern: assignment from toJSNewlyCreated, then a conditional on that variable
assign_match = re.search(r'toJSNewlyCreated[^;]*;', between)
if assign_match:
    after_assign = between[assign_match.end():]
    # Check for conditional on the result variable or null/empty check
    if re.search(r'if\s*\(\s*!', after_assign) or re.search(r'if\s*\(.*(?:null|empty|undefined|exception|error)', after_assign, re.IGNORECASE):
        has_guard = True

if has_guard:
    print('ok')
else:
    print('fail')
PYEOF
)

if [ "$CHECK1" = "ok" ]; then
  echo "PASS [0.30]: Exception/null guard between toJSNewlyCreated and jsCast"
  add_score 0.30 behavioral
  GATE_PASS=1
elif [ "$CHECK1" = "broken" ]; then
  echo "FAIL [0.30]: Function structure broken — missing toJSNewlyCreated or jsCast"
else
  echo "FAIL [0.30]: No exception/null guard between toJSNewlyCreated and jsCast"
fi

# ── Check 2 (0.25): Guard prevents reaching jsCast on error path ──
# [pr_diff] (0.25): Exception path must not reach jsCast — needs conditional return/branch
# Justification: C++ code requires full Bun build
CHECK2=$(python3 << 'PYEOF'
import sys, re, os

region = os.environ.get("FUNC_REGION", "")

jsn = region.find('toJSNewlyCreated')
jsc = region.find('jsCast')
if jsn < 0 or jsc < 0:
    print('fail')
    sys.exit(0)

between = region[jsn:jsc]

# Must have BOTH a check AND a diversion (return/throw/RETURN_IF_EXCEPTION)
# RETURN_IF_EXCEPTION combines both — it checks and returns
has_diversion = False

if 'RETURN_IF_EXCEPTION' in between:
    has_diversion = True  # Macro handles check+return
elif 'return' in between:
    # 'return' alone is not enough — it must be inside an exception-related conditional
    # to avoid gaming with 'if (true) { return; }'
    # Extract the if-condition text and check it references exception/null/error state
    if_match = re.search(r'if\s*\(([^)]*)\)', between)
    if if_match:
        condition = if_match.group(1).lower()
        exception_terms = ['exception', 'null', 'empty', 'undefined', 'scope',
                           'jsvalue', 'result', 'error', '!', 'throw']
        if any(t in condition for t in exception_terms):
            has_diversion = True

# Also accept: jsCast wrapped in conditional (only reached on success)
jsc_ctx = region[max(0, jsc - 200):jsc + 50]
if re.search(r'(?:else|if\s*\([^)]*(?:jsValue|result|!.*(?:empty|null|exception)))', jsc_ctx, re.IGNORECASE):
    has_diversion = True

if has_diversion:
    print('ok')
else:
    print('fail')
PYEOF
)

if [ "$CHECK2" = "ok" ]; then
  echo "PASS [0.25]: Guard prevents reaching jsCast on error path"
  add_score 0.25 behavioral
else
  echo "FAIL [0.25]: No conditional guard protecting jsCast from error path"
fi

# ── Check 3 (0.10): Valid URL path still reaches jsCast and RELEASE_AND_RETURN ──
# [pr_diff] (0.10): Fix must not break the success path — jsCast and RELEASE_AND_RETURN must remain reachable
# This prevents unconditional-return gaming
CHECK3=$(python3 << 'PYEOF'
import sys, os

region = os.environ.get("FUNC_REGION", "")

jsn = region.find('toJSNewlyCreated')
jsc = region.find('jsCast')
rar = region.find('RELEASE_AND_RETURN')

if jsn < 0 or jsc < 0 or rar < 0:
    print('fail')
    sys.exit(0)

# jsCast must come after toJSNewlyCreated
if jsc <= jsn:
    print('fail')
    sys.exit(0)

# RELEASE_AND_RETURN must come after jsCast
if rar <= jsc:
    print('fail')
    sys.exit(0)

between = region[jsn:jsc]

# Check for unconditional return that would make jsCast unreachable
# An unconditional return = a 'return' at the top level of the between region
# (not inside an if/else block)
lines = between.split('\n')
brace_depth = 0
has_unconditional_return = False
for line in lines:
    stripped = line.strip()
    brace_depth += stripped.count('{') - stripped.count('}')
    # A return at brace_depth 0 or 1 (function body level) that isn't
    # inside a conditional block indicates unconditional return
    # RETURN_IF_EXCEPTION is conditional (macro), so skip it
    if 'RETURN_IF_EXCEPTION' in stripped:
        continue
    if stripped.startswith('return') and brace_depth <= 1:
        # Check if this return is preceded by an if/else on a recent line
        # Simple: if brace_depth is 0, it's unconditional
        if brace_depth <= 0:
            has_unconditional_return = True
            break

if has_unconditional_return:
    print('fail')
else:
    print('ok')
PYEOF
)

if [ "$CHECK3" = "ok" ]; then
  echo "PASS [0.10]: Valid URL path still reaches jsCast and RELEASE_AND_RETURN"
  add_score 0.10 behavioral
else
  echo "FAIL [0.10]: jsCast/RELEASE_AND_RETURN unreachable (unconditional return or removed)"
fi

# ── Check 4 (0.10): Fix region is non-trivial (anti-stub) ──
# [pr_diff] (0.10): The fix must add actual C++ statements, not whitespace or trivial stubs
CHECK4=$(python3 << 'PYEOF'
import sys, os

region = os.environ.get("FUNC_REGION", "")

jsn = region.find('toJSNewlyCreated')
jsc = region.find('jsCast')
if jsn < 0 or jsc < 0:
    print('fail')
    sys.exit(0)

between = region[jsn:jsc]
# Count non-trivial lines (not empty, not just braces/parens)
lines = [l.strip() for l in between.split('\n')
         if l.strip() and l.strip() not in ('{', '}', '(', ')', ');', '};')]
# The original buggy code has ~1 line between. A real fix adds at least 2 meaningful lines.
if len(lines) >= 3:
    print('ok')
else:
    print('fail')
PYEOF
)

if [ "$CHECK4" = "ok" ]; then
  echo "PASS [0.10]: Fix region contains non-trivial code"
  add_score 0.10 behavioral
else
  echo "FAIL [0.10]: Fix region appears trivial or empty"
fi

# ── Pass-to-pass: Core function structure preserved (0.10) ──
# [pr_diff] (0.10): jsCast, reportExtraMemoryAllocated, RELEASE_AND_RETURN must remain in function
P2P_OK=$(python3 << 'PYEOF'
import re, sys

with open("/repo/src/bun.js/bindings/BunString.cpp") as f:
    content = f.read()
content = re.sub(r'//[^\n]*', '', content)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

idx = content.find('BunString__toJSDOMURL')
if idx < 0:
    print('fail')
    sys.exit(0)
func_end = content.find('extern "C"', idx + 50)
if func_end < 0:
    func_end = idx + 1500
region = content[idx:func_end]
required = ['jsCast', 'reportExtraMemoryAllocated', 'RELEASE_AND_RETURN']
missing = [r for r in required if r not in region]
if missing:
    print('fail:' + ','.join(missing))
else:
    print('ok')
PYEOF
)

if [ "$P2P_OK" = "ok" ]; then
  echo "PASS [0.10]: Core function structure preserved"
  add_score 0.10 regression
else
  echo "FAIL [0.10]: Function structure damaged — $P2P_OK"
fi

# ── Pass-to-pass: Adjacent URL__fromJS function unchanged (0.05) ──
# [pr_diff] (0.05): Nearby URL__fromJS function must not be broken
URL_FROMJS=$(python3 << 'PYEOF'
import re, sys

with open("/repo/src/bun.js/bindings/BunString.cpp") as f:
    content = f.read()
content = re.sub(r'//[^\n]*', '', content)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

idx = content.find('URL__fromJS')
if idx < 0:
    print('fail')
    sys.exit(0)
region = content[idx:idx + 600]
required = ['RETURN_IF_EXCEPTION', 'isValid']
missing = [r for r in required if r not in region]
if missing:
    print('fail:' + ','.join(missing))
else:
    print('ok')
PYEOF
)

if [ "$URL_FROMJS" = "ok" ]; then
  echo "PASS [0.05]: URL__fromJS function preserved"
  add_score 0.05 regression
else
  echo "FAIL [0.05]: URL__fromJS function damaged — $URL_FROMJS"
fi

# ── Anti-stub: File not gutted (0.05) ──
# [pr_diff] (0.05): File must retain substantial content
LINE_COUNT=$(wc -l < "$TARGET")
if [ "$LINE_COUNT" -gt 400 ]; then
  echo "PASS [0.05]: File has $LINE_COUNT lines (not stubbed)"
  add_score 0.05 regression
else
  echo "FAIL [0.05]: File appears stubbed ($LINE_COUNT lines)"
fi

# ── Config-derived: Uses established JSC exception handling pattern (0.05) ──
# [agent_config] (0.05): Exception handling should follow existing patterns — CLAUDE.md:1 @ 9e93bfa
# BunString.cpp already uses RETURN_IF_EXCEPTION in URL__fromJS; idiomatic JSC uses throwScope
# Gated behind GATE_PASS (Check1 must pass to earn config points)
CONFIG_CHECK=$(python3 << 'PYEOF'
import sys, os

region = os.environ.get("FUNC_REGION", "")

jsn = region.find('toJSNewlyCreated')
if jsn < 0:
    print('fail')
    sys.exit(0)
after_jsn = region[jsn:]

# Check for idiomatic JSC exception handling
idiomatic = ('RETURN_IF_EXCEPTION' in after_jsn or
             'throwScope' in after_jsn or
             'hasPendingException' in after_jsn)
if idiomatic:
    print('ok')
else:
    print('partial')
PYEOF
)

if [ "$GATE_PASS" -eq 1 ]; then
  if [ "$CONFIG_CHECK" = "ok" ]; then
    echo "PASS [0.05]: Fix uses idiomatic JSC exception handling pattern"
    add_score 0.05 config
  elif [ "$CONFIG_CHECK" = "partial" ]; then
    echo "PARTIAL [0.05]: Fix works but doesn't use established JSC exception pattern"
    add_score 0.02 config
  else
    echo "FAIL [0.05]: No exception handling pattern detected"
  fi
else
  echo "SKIP [0.05]: Config check gated behind Check1"
fi

# ── Write results ──
echo "$TOTAL" > "$REWARD_FILE"
echo "{\"reward\":$TOTAL,\"behavioral\":$behavioral,\"regression\":$regression,\"config\":$config}" > "$REWARD_JSON"

echo ""
echo "=== SCORE: $TOTAL ==="
echo "  behavioral: $behavioral"
echo "  regression: $regression"
echo "  config:     $config"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
