#!/usr/bin/env bash
set +e

REPO="/workspace/bun"
TARGET="$REPO/src/shell/braces.zig"
REWARD=0
TOTAL=100
DETAILS=""

log() {
    local weight="$1" pass="$2" desc="$3"
    if [ "$pass" = "1" ]; then
        DETAILS="${DETAILS}PASS ($weight): $desc\n"
        REWARD=$((REWARD + weight))
    else
        DETAILS="${DETAILS}FAIL ($weight): $desc\n"
    fi
}

# =============================================================================
# GATE: braces.zig must exist and be structurally intact
# WHY structural: Zig source requires full Bun build toolchain to compile+run
# =============================================================================

# [pr_diff] GATE: braces.zig exists and contains core Parser struct
if ! python3 -c "
content = open('$TARGET').read()
assert 'pub const Parser = struct' in content
assert 'fn flattenTokens(' in content
assert 'fn advance(' in content
assert 'fn prev(' in content
assert 'fn peek(' in content
" 2>/dev/null; then
    echo "GATE FAIL: braces.zig missing or core Parser struct broken"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASS: braces.zig core structure intact"

GATE_PASS=1

# =============================================================================
# FAIL-TO-PASS 1 (0.35): flattenTokens guards against empty token list
# WHY structural: compiled Zig — cannot call without full Bun rebuild
# The bug: flattenTokens accesses self.tokens.items[0] without checking length.
# Any correct fix must ensure an empty-length guard BEFORE the first items[N] access
# AND that the guard actually prevents execution of the dangerous access.
# Accepts: if(len==0)return, if(len<1)return, wrapping body in if(len>0){...}, etc.
# =============================================================================

# [pr_diff] (0.35): flattenTokens has effective empty-token guard BEFORE first array access
PASS_FLATTEN=0
if python3 -c "
import re, sys

content = open('$TARGET').read()

# Extract flattenTokens body using brace-depth counting
start = content.find('fn flattenTokens(')
if start == -1:
    sys.exit(1)

brace_start = content.index('{', start)
depth = 1
i = brace_start + 1
while i < len(content) and depth > 0:
    if content[i] == '{': depth += 1
    elif content[i] == '}': depth -= 1
    i += 1
func_body = content[brace_start+1:i-1]

lines = func_body.split('\n')
guard_line = None
guard_effective = False
access_line = None

for idx, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('//'):
        continue

    # Detect length/emptiness guard patterns
    is_len_check = bool(re.search(r'\.len\s*(==\s*0|<\s*1|>\s*0|!=\s*0|>=\s*1)', stripped))
    is_tokens_len = bool(re.search(r'tokens.*len', stripped) and ('return' in stripped or 'if' in stripped))

    if guard_line is None and (is_len_check or is_tokens_len):
        guard_line = idx
        # Verify the guard is effective: must return, continue, break, or open a block
        # Pattern 1: 'if (len == 0) return' on same line
        if 'return' in stripped and re.search(r'(==\s*0|<\s*1)', stripped):
            guard_effective = True
        # Pattern 2: 'if (len > 0)' or 'if (len >= 1)' or 'if (len != 0)' wrapping body
        elif re.search(r'if\s*\(.*\.len\s*(>\s*0|>=\s*1|!=\s*0)', stripped):
            guard_effective = True
        # Pattern 3: early return with 0-length check on nearby lines
        elif re.search(r'(==\s*0|<\s*1)', stripped):
            # Check next few non-comment lines for return
            for j in range(idx+1, min(idx+4, len(lines))):
                nxt = lines[j].strip()
                if nxt.startswith('//'):
                    continue
                if 'return' in nxt:
                    guard_effective = True
                    break
                if nxt and not nxt.startswith('//'):
                    break

    # Detect items[N] access (the dangerous pattern)
    if access_line is None and re.search(r'items\[', stripped) and not stripped.startswith('//'):
        access_line = idx

# Guard must exist, be effective, and come before access
if guard_line is None:
    sys.exit(1)
if not guard_effective:
    sys.exit(1)
if access_line is not None and guard_line > access_line:
    sys.exit(1)
" 2>/dev/null; then
    PASS_FLATTEN=1
fi
log 35 "$PASS_FLATTEN" "[pr_diff] flattenTokens has effective empty-token guard BEFORE first array access"

# =============================================================================
# FAIL-TO-PASS 2 (0.30): advance()/prev() handles current==0 safely
# The bug: advance() calls prev() which does current-1, underflowing when current==0.
# Valid fixes include:
#   (a) Guard in advance() before calling prev()
#   (b) Make prev() itself use saturating subtraction (current -| 1)
#   (c) Use @max(current, 1) - 1 in prev()
#   (d) Inline safe access in advance() instead of calling prev()
# This check accepts ALL of these approaches.
# =============================================================================

# [pr_diff] (0.30): Parser handles current==0 safely (no underflow in advance/prev path)
PASS_UNDERFLOW=0
if python3 -c "
import re, sys

content = open('$TARGET').read()

# Strategy: check BOTH advance() and prev() — fix in either is valid.
# The bug is that advance()->prev() does current-1 when current==0.

def extract_fn(name, src):
    start = src.find('fn ' + name + '(')
    if start == -1:
        return None
    brace_start = src.index('{', start)
    depth = 1
    i = brace_start + 1
    while i < len(src) and depth > 0:
        if src[i] == '{': depth += 1
        elif src[i] == '}': depth -= 1
        i += 1
    return src[brace_start+1:i-1]

advance_body = extract_fn('advance', content)
prev_body = extract_fn('prev', content)

if advance_body is None:
    sys.exit(1)
if prev_body is None:
    sys.exit(1)

fixed = False

# === Approach A: advance() itself is safe ===
adv_lines = [l.strip() for l in advance_body.split('\n') if l.strip() and not l.strip().startswith('//')]

# Check if bare unconditional 'return self.prev()' is gone from advance
has_bare_prev = any(re.match(r'^return\s+self\.prev\(\)\s*;?\s*$', l) for l in adv_lines)

if not has_bare_prev:
    # There's some change in advance(). Verify it has a guard mechanism.
    full_adv = advance_body
    adv_has_guard = False
    # Conditional return with prev
    if re.search(r'return\s+if\s*\(', full_adv):
        adv_has_guard = True
    # current > 0 / != 0 / >= 1 check
    if re.search(r'current\s*(>|!=|>=)\s*(0|1)', full_adv):
        adv_has_guard = True
    # current == 0 check
    if re.search(r'current\s*==\s*0', full_adv):
        adv_has_guard = True
    # Saturating subtraction in advance
    if '-|' in full_adv and 'current' in full_adv:
        adv_has_guard = True
    # @max approach in advance
    if '@max' in full_adv and 'current' in full_adv:
        adv_has_guard = True
    # Condition wrapping prev call
    if re.search(r'if\s*\(.*current', full_adv) and 'prev' in full_adv:
        adv_has_guard = True
    if adv_has_guard:
        fixed = True

# === Approach B: prev() itself is safe (saturating sub, @max, etc.) ===
full_prev = prev_body
# Saturating subtraction: current -| 1 (Zig idiom)
if '-|' in full_prev and 'current' in full_prev:
    fixed = True
# @max(self.current, 1) - 1
if '@max' in full_prev and 'current' in full_prev:
    fixed = True
# Explicit guard in prev: if (current == 0) return ...
if re.search(r'current\s*==\s*0', full_prev) and 'return' in full_prev:
    fixed = True
# Conditional: if (current > 0) current - 1 else 0
if re.search(r'if\s*\(.*current\s*(>|!=|>=)\s*(0|1)', full_prev):
    fixed = True

if not fixed:
    sys.exit(1)
" 2>/dev/null; then
    PASS_UNDERFLOW=1
fi
log 30 "$PASS_UNDERFLOW" "[pr_diff] Parser handles current==0 safely (no underflow in advance/prev path)"

# =============================================================================
# PASS-TO-PASS (0.15): Core parser functions still work correctly
# =============================================================================

# [repo_tests] (0.05): prev() still returns token at current-1 for normal case
PASS_PREV=0
if python3 -c "
content = open('$TARGET').read()
start = content.find('fn prev(')
if start == -1: exit(1)
# Extract prev body
brace_start = content.index('{', start)
depth = 1
i = brace_start + 1
while i < len(content) and depth > 0:
    if content[i] == '{': depth += 1
    elif content[i] == '}': depth -= 1
    i += 1
body = content[brace_start+1:i-1]
# Must still reference current - 1 or current -| 1 (normal case token access)
if 'current - 1' in body or 'current -| 1' in body or '@max' in body:
    exit(0)
exit(1)
" 2>/dev/null; then
    PASS_PREV=1
fi
log 5 "$PASS_PREV" "[repo_tests] prev() still returns token at current-1"

# [repo_tests] (0.05): is_at_end() still works (needed for advance to function)
PASS_END=0
if python3 -c "
content = open('$TARGET').read()
start = content.find('fn is_at_end(')
if start == -1: exit(1)
brace_start = content.index('{', start)
depth = 1
i = brace_start + 1
while i < len(content) and depth > 0:
    if content[i] == '{': depth += 1
    elif content[i] == '}': depth -= 1
    i += 1
body = content[brace_start+1:i-1]
if 'current' in body and ('tokens' in body or 'len' in body):
    exit(0)
exit(1)
" 2>/dev/null; then
    PASS_END=1
fi
log 5 "$PASS_END" "[repo_tests] is_at_end() function still intact"

# [repo_tests] (0.05): peek() still works (returns current token)
PASS_PEEK=0
if python3 -c "
content = open('$TARGET').read()
start = content.find('fn peek(')
if start == -1: exit(1)
brace_start = content.index('{', start)
depth = 1
i = brace_start + 1
while i < len(content) and depth > 0:
    if content[i] == '{': depth += 1
    elif content[i] == '}': depth -= 1
    i += 1
body = content[brace_start+1:i-1]
# peek returns the token at current position
if 'current' in body and 'items' in body:
    exit(0)
exit(1)
" 2>/dev/null; then
    PASS_PEEK=1
fi
log 5 "$PASS_PEEK" "[repo_tests] peek() function still intact"

# =============================================================================
# ANTI-STUB (0.10): flattenTokens still has real logic — gated behind F2P
# =============================================================================

# [pr_diff] (0.10): flattenTokens contains core brace-expansion logic (not stubbed out)
# GATED: only awards points if at least one F2P check passed
PASS_STUB=0
if [ "$PASS_FLATTEN" = "1" ] || [ "$PASS_UNDERFLOW" = "1" ]; then
    if python3 -c "
import sys

content = open('$TARGET').read()
start = content.find('fn flattenTokens(')
if start == -1: sys.exit(1)

brace_start = content.index('{', start)
depth = 1
i = brace_start + 1
while i < len(content) and depth > 0:
    if content[i] == '{': depth += 1
    elif content[i] == '}': depth -= 1
    i += 1
body = content[brace_start+1:i-1]

# Must still have core logic indicators
if 'brace_count' not in body: sys.exit(1)
if '.open' not in body: sys.exit(1)
# Must have meaningful iteration (while or for loop)
if 'while' not in body and 'for' not in body: sys.exit(1)
# Must be non-trivial: at least 15 non-blank non-comment lines
real_lines = [l for l in body.split('\n') if l.strip() and not l.strip().startswith('//')]
if len(real_lines) < 15: sys.exit(1)
" 2>/dev/null; then
        PASS_STUB=1
    fi
fi
log 10 "$PASS_STUB" "[pr_diff] flattenTokens still contains core brace-expansion logic (anti-stub, gated)"

# =============================================================================
# CONFIG-DERIVED (0.05): Agent config rules
# =============================================================================

# [agent_config] (0.05): No prohibited std.* APIs in new code — src/CLAUDE.md:16 @ 5b7fe81
# GATED: only awards points if at least one F2P check passed
PASS_CONFIG=0
if [ "$PASS_FLATTEN" = "1" ] || [ "$PASS_UNDERFLOW" = "1" ]; then
    if python3 -c "
import subprocess, sys
result = subprocess.run(['git', 'diff', 'HEAD'], capture_output=True, text=True, cwd='$REPO')
diff = result.stdout
if not diff:
    result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True, cwd='$REPO')
    diff = result.stdout
if not diff:
    # No changes — can't award config points without evidence of work
    sys.exit(1)

added = [l[1:] for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
for line in added:
    for f in ['std.fs', 'std.posix', 'std.os', 'std.process']:
        if f in line:
            sys.exit(1)
" 2>/dev/null; then
        PASS_CONFIG=1
    fi
fi
log 5 "$PASS_CONFIG" "[agent_config] No prohibited std.* APIs in new code — src/CLAUDE.md:16 @ 5b7fe81"

# =============================================================================
# RESULTS
# =============================================================================

echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo "Score: $REWARD / $TOTAL"

FINAL=$(python3 -c "print(f'{min(1.0, max(0.0, $REWARD / $TOTAL)):.4f}')")
echo "$FINAL" > /logs/verifier/reward.txt

BEH=$(python3 -c "print(($PASS_FLATTEN * 35 + $PASS_UNDERFLOW * 30) / 100)")
REG=$(python3 -c "print(($PASS_PREV * 5 + $PASS_END * 5 + $PASS_PEEK * 5) / 100)")
STUB=$(python3 -c "print($PASS_STUB * 10 / 100)")
CFG=$(python3 -c "print($PASS_CONFIG * 5 / 100)")
echo "{\"reward\": $FINAL, \"behavioral\": $BEH, \"regression\": $REG, \"anti_stub\": $STUB, \"config\": $CFG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

echo "Final reward: $FINAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
