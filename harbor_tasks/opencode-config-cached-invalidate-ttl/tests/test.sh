#!/usr/bin/env bash
set +e

FILE="/repo/packages/opencode/src/config/config.ts"

###############################################################################
# GATE: File exists and is non-trivial TypeScript
###############################################################################
# [pr_diff] (gate): File must exist with Config namespace
if ! python3 -c "
import sys
try:
    with open('$FILE') as f:
        content = f.read()
    if len(content.strip().split('\n')) < 500:
        print('GATE FAIL: file appears gutted'); sys.exit(1)
    if 'namespace Config' not in content:
        print('GATE FAIL: Config namespace missing'); sys.exit(1)
    print('GATE PASS')
except Exception as e:
    print(f'GATE FAIL: {e}'); sys.exit(1)
"; then
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
  exit 0
fi

B1=0; B2=0; B3=0; B4=0
R1=0; R2=0; R3=0
C1=0; C2=0
S1=0

###############################################################################
# Helper: strip JS/TS comments from source code
# Used by checks to prevent comment-injection gaming
###############################################################################
STRIP_COMMENTS='
import re
def strip_comments(src):
    # Remove single-line comments (but not :// in URLs)
    src = re.sub(r"(?<![:\"\x27\\])//[^\n]*", "", src)
    # Remove multi-line comments
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src
'

###############################################################################
# BEHAVIORAL: Fail-to-pass tests (0.65 total)
###############################################################################

# [pr_diff] (0.30): Cache uses Effect.cachedInvalidateWithTTL with destructured
#   const binding — the core fix replacing mutable let + Effect.cached
B1=0
if python3 << 'PYEOF'
import re, sys

with open("/repo/packages/opencode/src/config/config.ts") as f:
    src = f.read()

# Strip comments to prevent gaming via // cachedInvalidateWithTTL
exec("""
import re as _re
def strip_comments(s):
    s = _re.sub(r"(?<![:\\\"\\x27\\\\])//[^\\n]*", "", s)
    s = _re.sub(r"/\\*.*?\\*/", "", s, flags=_re.DOTALL)
    return s
""")
code = strip_comments(src)

# (a) cachedInvalidateWithTTL must appear in actual code, not just comments
if 'cachedInvalidateWithTTL' not in code:
    print('FAIL: cachedInvalidateWithTTL not found in code (comment-stripped)')
    sys.exit(1)

# (b) Must be in a yield* expression with array destructuring
#     Accept: const [x, y] = yield* Effect.cachedInvalidateWithTTL(...)
#     Accept: const [x, y] = yield* pipe(Effect.cachedInvalidateWithTTL(...))
if not re.search(r'const\s+\[\s*\w+\s*,\s*\w+\s*\]\s*=\s*yield\*', code):
    print('FAIL: no const [a, b] = yield* destructuring found')
    sys.exit(1)

# (c) No mutable let cachedGlobal
if re.search(r'\blet\s+cachedGlobal\b', code):
    print('FAIL: let cachedGlobal still exists')
    sys.exit(1)

print('PASS: cache uses cachedInvalidateWithTTL with const destructuring')
PYEOF
then B1=1; fi

# [pr_diff] (0.15): invalidate() no longer recreates cache — uses invalidation
#   handle instead of reassigning via Effect.cached
B2=0
if python3 << 'PYEOF'
import re, sys

with open("/repo/packages/opencode/src/config/config.ts") as f:
    src = f.read()

# Strip comments
code = re.sub(r"(?<![:\"\x27\\])//[^\n]*", "", src)
code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)

# Find the invalidate function body (may have various indentation levels)
m = re.search(r'const\s+invalidate\s*=.*?function\*\s*\(.*?\)\s*\{(.*?)\n\s{4,8}\}\)', code, re.DOTALL)
if not m:
    m = re.search(r'invalidate\b.*?function\*.*?\{(.*?)\n\s{4,8}\}\)', code, re.DOTALL)

if not m:
    print('FAIL: cannot find invalidate function')
    sys.exit(1)

body = m.group(1)

# MUST NOT recreate cache with Effect.cached(
if 'Effect.cached(' in body:
    print('FAIL: invalidate still recreates cache with Effect.cached()')
    sys.exit(1)

# MUST NOT reassign cachedGlobal (the mutable pattern)
if re.search(r'cachedGlobal\s*=\s*yield', body):
    print('FAIL: invalidate still reassigns cachedGlobal')
    sys.exit(1)

# MUST have a yield* statement (calling the invalidation handle)
if 'yield*' not in body and 'yield *' not in body:
    print('FAIL: invalidate has no yield statement for invalidation')
    sys.exit(1)

print('PASS: invalidate uses invalidation handle, no cache recreation')
PYEOF
then B2=1; fi

# [pr_diff] (0.10): Error logging added before fallback — errors are no longer
#   silently swallowed by orElseSucceed
B3=0
if python3 << 'PYEOF'
import re, sys

with open("/repo/packages/opencode/src/config/config.ts") as f:
    src = f.read()

# Strip comments
code = re.sub(r"(?<![:\"\x27\\])//[^\n]*", "", src)
code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)

# Error logging must exist in CODE and be near the loadGlobal/orElseSucceed chain
error_kws = ['tapError', 'logError', 'catchAll', 'tap.*error', 'Effect\.log']
found = False
for kw in error_kws:
    for m in re.finditer(kw, code):
        # Check it's near the config loading area (within 500 chars of loadGlobal or orElseSucceed)
        start = max(0, m.start() - 400)
        end = min(len(code), m.end() + 400)
        region = code[start:end]
        if ('orElseSucceed' in region or 'loadGlobal' in region) and '.pipe(' in region:
            found = True
            break
    if found:
        break

if not found:
    print('FAIL: no error logging near loadGlobal pipe chain (comment-stripped)')
    sys.exit(1)

print('PASS: error logging found in loadGlobal pipe chain')
PYEOF
then B3=1; fi

# [pr_diff] (0.10): Duration imported from effect AND used as TTL argument
#   near cachedInvalidateWithTTL call
B4=0
if python3 << 'PYEOF'
import re, sys

with open("/repo/packages/opencode/src/config/config.ts") as f:
    src = f.read()

code = re.sub(r"(?<![:\"\x27\\])//[^\n]*", "", src)
code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)

# Must import Duration from 'effect'
if not re.search(r'import\s*\{[^}]*\bDuration\b[^}]*\}\s*from\s*["\']effect["\']', code):
    print('FAIL: Duration not imported from effect')
    sys.exit(1)

# Duration must be used near cachedInvalidateWithTTL (as the TTL argument)
idx = code.find('cachedInvalidateWithTTL')
if idx < 0:
    print('FAIL: cachedInvalidateWithTTL not found')
    sys.exit(1)

region = code[idx:idx+600]
if not re.search(r'Duration\.\w+', region):
    print('FAIL: Duration.xxx not used as TTL near cachedInvalidateWithTTL')
    sys.exit(1)

print('PASS: Duration imported and used as TTL argument')
PYEOF
then B4=1; fi

###############################################################################
# REGRESSION: Pass-to-pass (0.15 total)
###############################################################################

# [pr_diff] (0.05): getGlobal function still exists and yields cachedGlobal
R1=0
if python3 << 'PYEOF'
import re, sys
with open("/repo/packages/opencode/src/config/config.ts") as f:
    content = f.read()
if re.search(r'const\s+getGlobal\b.*?cachedGlobal', content, re.DOTALL):
    print('PASS'); sys.exit(0)
print('FAIL: getGlobal missing or not using cachedGlobal'); sys.exit(1)
PYEOF
then R1=1; fi

# [pr_diff] (0.05): invalidate function still dispatches Instance.disposeAll
R2=0
if python3 << 'PYEOF'
import sys
with open("/repo/packages/opencode/src/config/config.ts") as f:
    content = f.read()
if 'Instance.disposeAll' in content:
    print('PASS'); sys.exit(0)
print('FAIL'); sys.exit(1)
PYEOF
then R2=1; fi

# [pr_diff] (0.05): loadGlobal function still exists
R3=0
if python3 << 'PYEOF'
import re, sys
with open("/repo/packages/opencode/src/config/config.ts") as f:
    content = f.read()
if re.search(r'(const|function)\s+loadGlobal\b', content):
    print('PASS'); sys.exit(0)
print('FAIL'); sys.exit(1)
PYEOF
then R3=1; fi

###############################################################################
# CONFIG-DERIVED: Agent config rules (0.10 total)
###############################################################################

# [agent_config] (0.05): "Prefer const over let" — AGENTS.md:62 @ 9f94bdb
C1=0
if python3 << 'PYEOF'
import re, sys
with open("/repo/packages/opencode/src/config/config.ts") as f:
    code = f.read()
code = re.sub(r"(?<![:\"\x27\\])//[^\n]*", "", code)
if re.search(r'\blet\s+cachedGlobal\b', code):
    print('FAIL: let cachedGlobal still present'); sys.exit(1)
print('PASS'); sys.exit(0)
PYEOF
then C1=1; fi

# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:15 @ 9f94bdb
C2=0
if python3 << 'PYEOF'
import re, sys
with open("/repo/packages/opencode/src/config/config.ts") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'cachedGlobal' in line or 'cachedInvalidateWithTTL' in line or 'invalidateGlobal' in line:
        region = lines[max(0,i-5):i+10]
        for l in region:
            stripped = re.sub(r'//.*', '', l)
            if ' as any' in stripped or ': any ' in stripped or ': any;' in stripped or ':any' in stripped:
                print('FAIL: any type near cache code'); sys.exit(1)
print('PASS'); sys.exit(0)
PYEOF
then C2=1; fi

###############################################################################
# STRUCTURAL: Anti-stub (0.10)
###############################################################################

# [pr_diff] (0.10): File not gutted — must retain original structure
S1=0
if python3 << 'PYEOF'
import sys
with open("/repo/packages/opencode/src/config/config.ts") as f:
    content = f.read()
lines = content.strip().split('\n')
if len(lines) < 1000:
    print(f'FAIL: only {len(lines)} lines, likely stubbed'); sys.exit(1)
required = ['loadGlobal', 'getGlobal', 'invalidate', 'loadFile', 'namespace Config']
for req in required:
    if req not in content:
        print(f'FAIL: missing {req}'); sys.exit(1)
print(f'PASS: {len(lines)} lines with all key functions'); sys.exit(0)
PYEOF
then S1=1; fi

###############################################################################
# TOTAL
###############################################################################
REWARD=$(python3 -c "
b1=$B1; b2=$B2; b3=$B3; b4=$B4
r1=$R1; r2=$R2; r3=$R3
c1=$C1; c2=$C2; s1=$S1
total = b1*0.30 + b2*0.15 + b3*0.10 + b4*0.10 + r1*0.05 + r2*0.05 + r3*0.05 + c1*0.05 + c2*0.05 + s1*0.10
print(round(total, 2))
")

echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
b = round($B1*0.30 + $B2*0.15 + $B3*0.10 + $B4*0.10, 4)
r = round($R1*0.05 + $R2*0.05 + $R3*0.05, 4)
c = round($C1*0.05 + $C2*0.05, 4)
data = {'reward': $REWARD, 'behavioral': b, 'regression': r, 'config': c, 'style_rubric': 0.0}
print(json.dumps(data))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
"

echo "Total reward: $REWARD"
source /tests/judge_hook.sh 2>/dev/null || true
