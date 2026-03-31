#!/usr/bin/env bash
set +e

SCORE=0.0
TOTAL=0.0

add_score() { SCORE=$(python3 -c "print($SCORE + $1)"); TOTAL=$(python3 -c "print($TOTAL + $1)"); }
add_total() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

cd /workspace/bun
FILE="test/cli/hot/hot.test.ts"

##############################################################################
# GATE: Target file must exist
##############################################################################
# [pr_diff] (gate): test/cli/hot/hot.test.ts must exist and be non-empty
if [ ! -s "$FILE" ]; then
    echo "GATE FAILED: $FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# Helper: strip comments so checks can't be gamed with comment injection.
# Writes stripped code to /tmp/stripped.ts for use by subsequent checks.
##############################################################################
python3 << 'PYEOF'
code = open("/workspace/bun/test/cli/hot/hot.test.ts").read()
lines = code.split('\n')
result = []
in_block = False
for line in lines:
    s = line.strip()
    if in_block:
        if '*/' in s:
            in_block = False
        continue
    if s.startswith('/*') and '*/' not in s:
        in_block = True
        continue
    if s.startswith('/*') and '*/' in s:
        continue
    if s.startswith('//'):
        continue
    result.append(line)
with open("/tmp/stripped.ts", "w") as f:
    f.write('\n'.join(result))
PYEOF

##############################################################################
# [pr_diff] (0.30): BEHAVIORAL — Data-loss bug must be fixed
# The buggy code sets str="" inside the inner loop then does "continue outer",
# discarding remaining unprocessed lines. The fix must:
#   (a) Remove this discard pattern
#   (b) Preserve remaining lines via ANY valid mechanism
##############################################################################
add_total 0.30
DATALOSS=$(python3 << 'PYEOF'
import re

code = open("/tmp/stripped.ts").read()

# (a) The buggy pattern: str="" followed (within ~5 lines) by continue outer
has_buggy = bool(re.search(
    r'str\s*=\s*["\']["\'].*?continue\s+outer',
    code, re.DOTALL
))

# (b) Remaining lines must be preserved. Accept ANY of:
#   - slice/splice on lines array (any index expression)
#   - join remaining lines back into buffer
#   - variable named "remaining" holding leftover lines
#   - re-assigning str from a subset of lines
#   - using break instead of continue (exits inner loop, preserving str)
preserves = bool(re.search(
    r'(?:'
    r'lines?\.\s*slice\s*\(|'       # .slice(
    r'lines?\.\s*splice\s*\(|'      # .splice(
    r'remaining\s*[=,]|'            # remaining = ... or remaining,
    r'\.join\s*\(\s*["\']\\n|'      # .join("\n
    r'str\s*=\s*[^"\';\n]*lines?|'  # str = ...lines...
    r'buf\w*\s*=\s*[^"\';\n]*lines' # buffer = ...lines...
    r')',
    code
))

# Also accept: if the code no longer has "continue outer" at all
# (restructured to not need it), that inherently fixes the data loss
no_continue_outer = 'continue outer' not in code

if (not has_buggy) and (preserves or no_continue_outer):
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$DATALOSS" = "PASS" ]; then
    add_score 0.30
    echo "PASS [0.30]: Data-loss continue-outer pattern fixed, remaining lines preserved"
else
    echo "FAIL [0.30]: Buggy continue-outer still discards remaining lines"
fi

##############################################################################
# [pr_diff] (0.15): BEHAVIORAL — Trailing partial lines must be preserved
# When splitting stderr by newline, the last element may be an incomplete line.
# The fix must save it for the next iteration rather than discarding with str="".
##############################################################################
add_total 0.15
PARTIAL=$(python3 << 'PYEOF'
import re

code = open("/tmp/stripped.ts").read()

# Accept ANY mechanism that preserves the trailing partial line:
#   - .pop() on the split array
#   - accessing last element via [length-1], .at(-1), slice(-1)
#   - any assignment of last element before processing
#   - using split limit or custom splitting that handles partials
saves_last = bool(re.search(
    r'(?:'
    r'lines?\.\s*pop\s*\(\s*\)|'                  # lines.pop()
    r'lines?\s*\[\s*lines?\s*\.\s*length\s*-\s*1|' # lines[lines.length - 1]
    r'lines?\.\s*at\s*\(\s*-\s*1\s*\)|'           # lines.at(-1)
    r'lines?\.\s*slice\s*\(\s*-\s*1\s*\)|'        # lines.slice(-1)
    r'str\s*=\s*lines?\.\s*pop|'                   # str = lines.pop
    r'str\s*=\s*lines?\s*\[\s*lines?\s*\.\s*length' # str = lines[lines.length
    r')',
    code
))

# The old pattern cleared str="" inside the processing loop.
# After comment stripping, check this doesn't exist in the line-processing context.
# (str="" at function top / outside loops is fine)
inner_clear = bool(re.search(
    r'(?:shift|splice|for|while).*?str\s*=\s*["\']["\']',
    code, re.DOTALL
))

# Also accept: if no continue outer exists and code uses a helper function
# that returns remaining buffer (restructured approach)
uses_helper = bool(re.search(r'(?:async\s+)?function\s+\w+.*?stderr', code, re.DOTALL))

if (saves_last or uses_helper) and not inner_clear:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$PARTIAL" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: Trailing partial lines preserved correctly"
else
    echo "FAIL [0.15]: Trailing partial lines may be discarded"
fi

##############################################################################
# [pr_diff] (0.20): BEHAVIORAL — Bundler subprocesses must not use inherit pipes
# stdout:"inherit"/stderr:"inherit" causes pipe buffer backpressure that blocks
# the bundler. Must use "pipe", "ignore", or null instead.
##############################################################################
add_total 0.20
PIPE=$(python3 << 'PYEOF'
import re

code = open("/tmp/stripped.ts").read()

# Find spawn blocks that include bundler-related args (build, --watch)
# and check they don't use inherit for stdout/stderr
# Use a broad search: any spawn/Bun.spawn with build+watch args
spawn_sections = re.findall(
    r'spawn\s*\(\s*\{[\s\S]*?\}\s*\)',
    code
)

found_bundler = False
has_inherit = False
for section in spawn_sections:
    if '--watch' in section or '"watch"' in section:
        found_bundler = True
        if re.search(r'std(?:out|err)\s*:\s*["\']inherit["\']', section):
            has_inherit = True

# Also check via broader pattern if spawn format differs
if not found_bundler:
    bundler_blocks = re.findall(
        r'(?:spawn|Bun\.spawn)\s*\([\s\S]{0,500}?(?:build|--watch)[\s\S]{0,500}?\)',
        code
    )
    for block in bundler_blocks:
        found_bundler = True
        if re.search(r'std(?:out|err)\s*:\s*["\']inherit["\']', block):
            has_inherit = True

if found_bundler and not has_inherit:
    print('PASS')
elif not found_bundler:
    # Bundler spawns may have been restructured; check file-wide
    # that "inherit" is not used with stdout/stderr at all for bundler tests
    bundler_test_code = re.split(r'(?=it\s*\()', code)
    for test_block in bundler_test_code:
        if 'sourcemap loading' in test_block or 'large files' in test_block:
            if re.search(r'std(?:out|err)\s*:\s*["\']inherit["\']', test_block):
                has_inherit = True
                found_bundler = True
    if found_bundler and not has_inherit:
        print('PASS')
    elif not found_bundler:
        print('PASS')  # Restructured without bundler spawns
    else:
        print('FAIL')
else:
    print('FAIL')
PYEOF
)
if [ "$PIPE" = "PASS" ]; then
    add_score 0.20
    echo "PASS [0.20]: Bundler subprocesses do not use inherit pipes"
else
    echo "FAIL [0.20]: Bundler subprocesses still use stdout/stderr inherit"
fi

##############################################################################
# [pr_diff] (0.10): REGRESSION — All three sourcemap tests preserved
# The three tests must still exist (not removed) and verify 50 reload cycles.
##############################################################################
add_total 0.10
REGRESSION=$(python3 << 'PYEOF'
import re

code = open("/tmp/stripped.ts").read()

tests = [
    'should work with sourcemap generation',
    'should work with sourcemap loading',
    'should work with sourcemap loading with large files',
]

all_present = all(t in code for t in tests)

# Each test must still verify 50 reloads (accept toBe(50), toEqual(50), === 50)
reload_checks = len(re.findall(
    r'(?:toBe|toEqual|===)\s*\(\s*50\s*\)',
    code
))

if all_present and reload_checks >= 3:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$REGRESSION" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: All three sourcemap tests preserved with reload assertions"
else
    echo "FAIL [0.10]: Sourcemap tests missing or reload assertions removed"
fi

##############################################################################
# [pr_diff] (0.10): STRUCTURAL — Early bundler exit detection
# Bundler-based tests should detect if the bundler exits early, rather than
# hanging indefinitely waiting on stderr.
# Accept: Promise.race, Promise.any, AbortController, exit event listener,
# or any concurrent monitoring pattern.
##############################################################################
add_total 0.10
EARLYEXIT=$(python3 << 'PYEOF'
import re

code = open("/tmp/stripped.ts").read()

# Accept any form of concurrent exit monitoring
has_exit_detect = bool(re.search(
    r'(?:'
    r'Promise\.\s*(?:race|any|allSettled)\s*\(|'  # Promise.race/any/allSettled
    r'bundler\.\s*exited|'                         # bundler.exited
    r'\.on\s*\(\s*["\'](?:exit|close)["\']|'       # .on('exit'/.on('close'
    r'AbortController|'                             # AbortController
    r'exited\s*\.\s*then\s*\('                     # exited.then(
    r')',
    code
))

if has_exit_detect:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$EARLYEXIT" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: Early bundler exit detection present"
else
    echo "FAIL [0.10]: No early bundler exit detection"
fi

##############################################################################
# [pr_diff] (0.05): ANTI-STUB — File meaningfully modified from base commit
# The fix must involve actual code changes, not just comment additions or
# trivial edits. Check via git diff.
##############################################################################
add_total 0.05
ANTISTUB=$(python3 << 'PYEOF'
import subprocess, re

# Get the diff from the base commit
diff = subprocess.run(
    ['git', 'diff', 'HEAD', '--', 'test/cli/hot/hot.test.ts'],
    capture_output=True, text=True, cwd='/workspace/bun'
).stdout

# Count added and removed non-comment, non-blank lines
added = 0
removed = 0
for line in diff.split('\n'):
    if line.startswith('+') and not line.startswith('+++'):
        content = line[1:].strip()
        if content and not content.startswith('//') and not content.startswith('/*'):
            added += 1
    elif line.startswith('-') and not line.startswith('---'):
        content = line[1:].strip()
        if content and not content.startswith('//') and not content.startswith('/*'):
            removed += 1

# Must have meaningful changes: at least 10 non-comment lines changed
# (the fix touches 3 loop instances, each ~15-20 lines)
code = open("/workspace/bun/test/cli/hot/hot.test.ts").read()
line_count = len(code.splitlines())

if (added + removed) >= 10 and line_count > 300:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$ANTISTUB" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: Anti-stub — meaningful code changes detected"
else
    echo "FAIL [0.05]: Changes appear trivial or file was gutted"
fi

##############################################################################
# [agent_config] (0.10): Buffer.alloc convention
# "Use Buffer.alloc(count, fill).toString() instead of 'A'.repeat(count)"
# — test/CLAUDE.md:147 @ af24e281
# Large repetitive strings (>=100 chars) must use Buffer.alloc, not .repeat()
##############################################################################
add_total 0.10
BUFALLOC=$(python3 << 'PYEOF'
import re

code = open("/tmp/stripped.ts").read()

# Find large .repeat() calls (number >= 100) in non-comment code
large_repeats = re.findall(r'["\'][^"\']*["\']\s*\.\s*repeat\s*\(\s*(\d+)\s*\)', code)
has_large_repeat = any(int(n) >= 100 for n in large_repeats)

# Should use Buffer.alloc or Uint8Array for large string creation
has_buffer = bool(re.search(r'Buffer\.\s*alloc\s*\(', code))
has_uint8 = bool(re.search(r'new\s+Uint8Array\s*\(', code))

if (has_buffer or has_uint8) and not has_large_repeat:
    print('PASS')
else:
    print('FAIL')
PYEOF
)
if [ "$BUFALLOC" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: Uses Buffer.alloc for large repetitive strings per test/CLAUDE.md"
else
    echo "FAIL [0.10]: Still uses .repeat() for large strings"
fi

##############################################################################
# Final score
##############################################################################
REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "Total: $SCORE / $TOTAL = $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# Compute category breakdowns
python3 -c "
score = $SCORE
# Behavioral: data-loss (0.30) + partial (0.15) + pipe (0.20) = 0.65 max
# Regression: tests exist (0.10)
# Structural: early exit (0.10) + anti-stub (0.05) = 0.15 max
# Config: buffer.alloc (0.10)
import json
reward = round(score / $TOTAL, 4) if $TOTAL > 0 else 0.0
print(json.dumps({
    'reward': reward,
    'behavioral': round(min(score, 0.65), 4),
    'regression': round(max(min(score - 0.65, 0.10), 0.0), 4),
    'config': round(max(min(score - 0.85, 0.10), 0.0), 4),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
