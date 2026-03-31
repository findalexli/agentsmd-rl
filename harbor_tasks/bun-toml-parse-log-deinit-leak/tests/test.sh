#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/bun

FILE="src/bun.js/api/TOMLObject.zig"

##############################################################################
# GATE: File exists and is non-empty
##############################################################################
# [pr_diff] (gate): TOMLObject.zig must exist
if [ ! -s "$FILE" ]; then
    echo "GATE FAILED: $FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# HELPER: Strip Zig comments from source so keyword-in-comment won't game
##############################################################################
STRIPPED=$(python3 -c "
import re, sys
text = open('$FILE').read()
# Remove // line comments
text = re.sub(r'//[^\n]*', '', text)
# Remove /* block comments */ (non-greedy)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
sys.stdout.write(text)
")

# Extract the parse function body from comment-stripped source
PARSE_FN=$(python3 -c "
import re, sys
text = '''$STRIPPED'''  # won't work with quotes in source
" 2>/dev/null || true)

# More robust extraction via file
PARSE_BODY=$(python3 << 'PYEOF'
import re, sys

with open("/workspace/bun/src/bun.js/api/TOMLObject.zig") as f:
    raw = f.read()

# Strip comments
text = re.sub(r'//[^\n]*', '', raw)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

# Extract parse function: find 'pub fn parse' then match braces
start = text.find('pub fn parse')
if start == -1:
    print('__NO_PARSE_FN__')
    sys.exit(0)

# Count braces to find the function end
depth = 0
body_start = text.find('{', start)
if body_start == -1:
    print('__NO_PARSE_FN__')
    sys.exit(0)

i = body_start
while i < len(text):
    if text[i] == '{':
        depth += 1
    elif text[i] == '}':
        depth -= 1
        if depth == 0:
            print(text[start:i+1])
            sys.exit(0)
    i += 1

print('__NO_PARSE_FN__')
PYEOF
)

if [ "$PARSE_BODY" = "__NO_PARSE_FN__" ]; then
    echo "GATE FAILED: pub fn parse not found in $FILE"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL: Fail-to-pass checks (0.65 total)
# WHY STRUCTURAL: Zig code requires the full bun build system (Zig compiler,
# JavaScriptCore, cmake) — cannot be compiled or called in test container.
# All checks operate on comment-stripped source to prevent gaming.
##############################################################################

# [pr_diff] (0.30): Log.init must be paired with a deferred log.deinit()
# On buggy code, Log.init exists but defer log.deinit() is missing, causing
# the logger's internal ArrayList to leak on every call.
# Accepts: defer log.deinit(), defer { log.deinit(); }, errdefer log.deinit()
add_total 0.30
DEINIT_CHECK=$(python3 << 'PYEOF'
import re

body = r"""
PARSE_BODY_PLACEHOLDER
"""

with open("/workspace/bun/src/bun.js/api/TOMLObject.zig") as f:
    raw = f.read()
text = re.sub(r'//[^\n]*', '', raw)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

start = text.find('pub fn parse')
if start == -1:
    print('FAIL')
    exit()

depth = 0
body_start = text.find('{', start)
i = body_start
while i < len(text):
    if text[i] == '{':
        depth += 1
    elif text[i] == '}':
        depth -= 1
        if depth == 0:
            body = text[start:i+1]
            break
    i += 1
else:
    print('FAIL')
    exit()

has_init = bool(re.search(r'Log\.init\s*\(', body))
# Accept various defer patterns for deinit
has_deinit = bool(re.search(r'(defer|errdefer)\s+(\{?\s*)?log\.deinit\s*\(\s*\)', body))
# Verify init comes before deinit (proper ordering)
if has_init and has_deinit:
    init_pos = re.search(r'Log\.init\s*\(', body).start()
    deinit_pos = re.search(r'(defer|errdefer)\s+(\{?\s*)?log\.deinit\s*\(\s*\)', body).start()
    if deinit_pos > init_pos:
        print('PASS')
    else:
        print('FAIL')
else:
    print('FAIL')
PYEOF
)
if [ "$DEINIT_CHECK" = "PASS" ]; then
    add_score 0.30
    echo "PASS [0.30]: Log.init is paired with deferred log.deinit()"
else
    echo "FAIL [0.30]: Log.init missing deferred log.deinit() — memory leak persists"
fi

# [pr_diff] (0.20): Argument access must not use deprecated arguments_old API.
# The buggy code uses callframe.arguments_old(1).slice() which is a legacy
# pattern. All peer parsers use callframe.argument(0).
add_total 0.20
ARG_CHECK=$(python3 << 'PYEOF'
import re

with open("/workspace/bun/src/bun.js/api/TOMLObject.zig") as f:
    raw = f.read()
text = re.sub(r'//[^\n]*', '', raw)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

start = text.find('pub fn parse')
if start == -1:
    print('FAIL')
    exit()

depth = 0
body_start = text.find('{', start)
i = body_start
while i < len(text):
    if text[i] == '{':
        depth += 1
    elif text[i] == '}':
        depth -= 1
        if depth == 0:
            body = text[start:i+1]
            break
    i += 1
else:
    print('FAIL')
    exit()

# Must NOT contain arguments_old in actual code (comments stripped)
has_old = 'arguments_old' in body
if has_old:
    print('FAIL')
else:
    print('PASS')
PYEOF
)
if [ "$ARG_CHECK" = "PASS" ]; then
    add_score 0.20
    echo "PASS [0.20]: argument access modernized (no arguments_old)"
else
    echo "FAIL [0.20]: still uses deprecated arguments_old pattern"
fi

# [pr_diff] (0.15): Input validation for empty/null/undefined is preserved.
# The parse function must still validate input and throw an appropriate error.
# Checks comment-stripped code only.
add_total 0.15
VALIDATE_CHECK=$(python3 << 'PYEOF'
import re

with open("/workspace/bun/src/bun.js/api/TOMLObject.zig") as f:
    raw = f.read()
text = re.sub(r'//[^\n]*', '', raw)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

start = text.find('pub fn parse')
if start == -1:
    print('FAIL')
    exit()

depth = 0
body_start = text.find('{', start)
i = body_start
while i < len(text):
    if text[i] == '{':
        depth += 1
    elif text[i] == '}':
        depth -= 1
        if depth == 0:
            body = text[start:i+1]
            break
    i += 1
else:
    print('FAIL')
    exit()

# Must check for empty/undefined/null input (actual code, not comments)
has_empty_check = 'isEmptyOrUndefinedOrNull' in body
# Must have the throwInvalidArguments call with a string-to-parse message
has_throw = bool(re.search(r'throwInvalidArguments\s*\(', body))
has_msg = 'Expected a string to parse' in body
if has_empty_check and has_throw and has_msg:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$VALIDATE_CHECK" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: input validation for empty/null/undefined preserved"
else
    echo "FAIL [0.15]: input validation missing or error message changed"
fi

##############################################################################
# REGRESSION: Pass-to-pass checks (0.15 total)
##############################################################################

# [pr_diff] (0.05): TOML parse call chain must remain intact.
# The function must still call TOML.parse with source and log parameters.
add_total 0.05
PARSE_CHAIN=$(python3 << 'PYEOF'
import re

with open("/workspace/bun/src/bun.js/api/TOMLObject.zig") as f:
    raw = f.read()
text = re.sub(r'//[^\n]*', '', raw)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

start = text.find('pub fn parse')
if start == -1:
    print('FAIL')
    exit()

depth = 0
body_start = text.find('{', start)
i = body_start
while i < len(text):
    if text[i] == '{':
        depth += 1
    elif text[i] == '}':
        depth -= 1
        if depth == 0:
            body = text[start:i+1]
            break
    i += 1
else:
    print('FAIL')
    exit()

has_toml_parse = bool(re.search(r'TOML\.parse\s*\(', body))
has_to_slice = bool(re.search(r'\.toSlice\s*\(', body))
if has_toml_parse and has_to_slice:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$PARSE_CHAIN" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: TOML parse call chain intact"
else
    echo "FAIL [0.05]: TOML parse call chain broken"
fi

# [pr_diff] (0.05): Peer parsers must not be modified (JSONC, JSON5, YAML).
add_total 0.05
PEER_CHECK=$(python3 << 'PYEOF'
import subprocess
result = subprocess.run(['git', 'diff', 'HEAD', '--name-only'],
                       capture_output=True, text=True, cwd='/workspace/bun')
changed = result.stdout.strip().split('\n') if result.stdout.strip() else []
peers = ['JSONCObject.zig', 'JSON5Object.zig', 'YAMLObject.zig']
modified_peers = [f for f in changed if any(p in f for p in peers)]
if not modified_peers:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$PEER_CHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: peer parsers (JSONC, JSON5, YAML) not modified"
else
    echo "FAIL [0.05]: peer parsers were unexpectedly modified"
fi

# [pr_diff] (0.05): Only TOMLObject.zig should be substantially changed.
# Allow minor changes to other files but the core fix must be in TOMLObject.zig.
add_total 0.05
SCOPE_CHECK=$(python3 << 'PYEOF'
import subprocess
result = subprocess.run(['git', 'diff', 'HEAD', '--numstat'],
                       capture_output=True, text=True, cwd='/workspace/bun')
lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
large_changes = []
for line in lines:
    parts = line.split('\t')
    if len(parts) == 3:
        added, removed, fname = parts
        try:
            total = int(added) + int(removed)
            if total > 20 and 'TOMLObject.zig' not in fname:
                large_changes.append(fname)
        except ValueError:
            pass
if not large_changes:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$SCOPE_CHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: changes scoped to TOMLObject.zig"
else
    echo "FAIL [0.05]: large changes outside TOMLObject.zig"
fi

##############################################################################
# ANTI-STUB (0.10): File must retain original structure
##############################################################################

# [pr_diff] (0.10): TOMLObject.zig must not be stubbed out — check structural
# similarity to original (imports, struct, multiple functions, line count).
add_total 0.10
STUB_CHECK=$(python3 << 'PYEOF'
import re

with open("/workspace/bun/src/bun.js/api/TOMLObject.zig") as f:
    raw = f.read()

# Strip comments for structural analysis
text = re.sub(r'//[^\n]*', '', raw)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

score = 0
reasons = []

# Must have reasonable line count (original is ~60-80 lines)
line_count = len(raw.strip().splitlines())
if line_count >= 40:
    score += 1
    reasons.append(f'lines={line_count}>=40')
else:
    reasons.append(f'lines={line_count}<40')

# Must have module-level @import statements (not just in a function)
imports = re.findall(r'@import\s*\(', text)
if len(imports) >= 3:
    score += 1
    reasons.append(f'imports={len(imports)}>=3')
else:
    reasons.append(f'imports={len(imports)}<3')

# Must have the TOMLObject struct or equivalent pub const
has_struct = bool(re.search(r'(pub\s+const\s+TOMLObject|const\s+Self)', text))
if has_struct:
    score += 1
    reasons.append('has_struct')
else:
    reasons.append('no_struct')

# Must have at least 2 pub fn definitions (parse + at least one other)
pub_fns = re.findall(r'pub\s+fn\s+\w+', text)
if len(pub_fns) >= 2:
    score += 1
    reasons.append(f'pub_fns={len(pub_fns)}>=2')
else:
    reasons.append(f'pub_fns={len(pub_fns)}<2')

# Must have allocator usage (core to the module)
has_alloc = 'default_allocator' in text or 'allocator' in text
if has_alloc:
    score += 1
    reasons.append('has_allocator')
else:
    reasons.append('no_allocator')

if score >= 4:
    print('PASS')
else:
    print(f'FAIL ({score}/5: {", ".join(reasons)})')
PYEOF
)
if echo "$STUB_CHECK" | grep -q "^PASS"; then
    add_score 0.10
    echo "PASS [0.10]: file retains original structure (not stubbed)"
else
    echo "FAIL [0.10]: file appears stubbed — $STUB_CHECK"
fi

##############################################################################
# CONFIG-DERIVED (0.10): Rules from agent config files
##############################################################################

# [agent_config] (0.05): "Never use @import() inline inside of functions" — src/CLAUDE.md:11
add_total 0.05
IMPORT_CHECK=$(python3 << 'PYEOF'
import re

with open("/workspace/bun/src/bun.js/api/TOMLObject.zig") as f:
    raw = f.read()
text = re.sub(r'//[^\n]*', '', raw)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

# Find all function bodies and check for @import inside them
# Functions start with 'pub fn' or 'fn' and have brace-delimited bodies
violations = False
for m in re.finditer(r'(?:pub\s+)?fn\s+\w+', text):
    start = m.start()
    brace = text.find('{', start)
    if brace == -1:
        continue
    depth = 0
    i = brace
    while i < len(text):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                fn_body = text[brace:i+1]
                if '@import(' in fn_body:
                    violations = True
                break
        i += 1

if not violations:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$IMPORT_CHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: no inline @import in functions"
else
    echo "FAIL [0.05]: found inline @import in function (violates src/CLAUDE.md:11)"
fi

# [agent_config] (0.05): "Always use bun.* APIs instead of std.*" — src/CLAUDE.md:16
add_total 0.05
STD_CHECK=$(python3 << 'PYEOF'
import re

with open("/workspace/bun/src/bun.js/api/TOMLObject.zig") as f:
    raw = f.read()
text = re.sub(r'//[^\n]*', '', raw)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

violations = re.findall(r'std\.(fs|posix|os)\.\w+', text)
if not violations:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$STD_CHECK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: uses bun.* APIs, no std.fs/posix/os violations"
else
    echo "FAIL [0.05]: uses std.* where bun.* should be used (violates src/CLAUDE.md:16)"
fi

##############################################################################
# FINAL SCORE
##############################################################################
REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "Total: $SCORE / $TOTAL = $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# Build component scores
python3 << PYEOF > /logs/verifier/reward.json
import json
score = $SCORE
reward = $REWARD
# Behavioral = first 0.65 of checks
behavioral = min(score, 0.65)
# Regression = next 0.15
regression = max(min(score - 0.65, 0.15), 0.0)
# Config = next 0.10
config_s = max(min(score - 0.80, 0.10), 0.0)
print(json.dumps({"reward": reward, "behavioral": round(behavioral, 4),
                   "regression": round(regression, 4), "config": round(config_s, 4),
                   "style_rubric": 0.0}))
PYEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
