#!/usr/bin/env bash
set +e

REPO="/workspace/bun"
SCORE=0
TOTAL=0

pass() { SCORE=$(python3 -c "print($SCORE + $1)"); TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "PASS ($1): $2"; }
fail() { TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "FAIL ($1): $2"; }

VM_FILE="$REPO/src/bun.js/VirtualMachine.zig"
ARGS_FILE="$REPO/src/cli/Arguments.zig"

# ── GATE: Files exist and are not empty ──────────────────────────────
if [ ! -s "$VM_FILE" ]; then
    echo "GATE FAIL: VirtualMachine.zig missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
if [ ! -s "$ARGS_FILE" ]; then
    echo "GATE FAIL: Arguments.zig missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ── Helper: extract function body using balanced braces ──────────────
# WHY structural: Zig code requires full bun build toolchain — cannot compile or call
EXTRACT_FN='
import sys, re

def extract_zig_fn(source, fn_name):
    """Extract a Zig function body using balanced brace counting."""
    pattern = re.compile(r"\bfn\s+" + re.escape(fn_name) + r"\b")
    m = pattern.search(source)
    if not m:
        return None
    # Find the opening brace
    start = m.start()
    brace_start = source.find("{", m.end())
    if brace_start < 0:
        return None
    depth = 0
    i = brace_start
    while i < len(source):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[start:i+1]
        i += 1
    return None

with open(sys.argv[1]) as f:
    src = f.read()
body = extract_zig_fn(src, sys.argv[2])
if body is None:
    sys.exit(1)
print(body)
'

CONFIGURE_DEBUGGER=$(python3 -c "$EXTRACT_FN" "$VM_FILE" "configureDebugger" 2>/dev/null)
if [ -z "$CONFIGURE_DEBUGGER" ]; then
    echo "GATE FAIL: configureDebugger function not found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ── Fail-to-pass: configureDebugger disables the transpiler cache (0.35) ──
# [pr_diff] (0.35): RuntimeTranspilerCache must be disabled inside configureDebugger
# WHY structural: Zig code requires full build toolchain — cannot call directly
if python3 -c "
import sys
body = '''$CONFIGURE_DEBUGGER'''
# Check that RuntimeTranspilerCache is disabled somewhere in the function
# Accept any of: .is_disabled = true, .disable(), setting the field
if 'RuntimeTranspilerCache' not in body:
    sys.exit(1)
# Must set is_disabled or call a disable method
if 'is_disabled' not in body and 'disable(' not in body:
    sys.exit(1)
# The disable must be an assignment to true or a method call
import re
if not re.search(r'RuntimeTranspilerCache\S*\.\s*is_disabled\s*=\s*true', body) and \
   not re.search(r'RuntimeTranspilerCache\S*\.disable\s*\(', body):
    sys.exit(1)
"; then
    pass 0.35 "configureDebugger disables RuntimeTranspilerCache"
else
    fail 0.35 "configureDebugger does not disable RuntimeTranspilerCache"
fi

# ── Fail-to-pass: cache disable gated on inspector being enabled (0.15) ──
# [pr_diff] (0.15): Cache disable must run when inspector is enabled (any activation method)
# WHY structural: Zig code requires full build toolchain
if python3 -c "
import sys
body = '''$CONFIGURE_DEBUGGER'''
# The function should check isInspectorEnabled() or env.get for BUN_INSPECT
# and the cache disable should be reachable from that path
has_inspector_check = 'isInspectorEnabled()' in body or 'inspector_enabled' in body or 'BUN_INSPECT' in body
has_cache_disable = 'RuntimeTranspilerCache' in body and ('is_disabled' in body or 'disable(' in body)
if not has_inspector_check:
    sys.exit(1)
if not has_cache_disable:
    sys.exit(1)
# Cache disable must appear after the inspector check (reachable from it)
insp_pos = min(p for p in [body.find('isInspectorEnabled()'), body.find('inspector_enabled'), body.find('BUN_INSPECT')] if p >= 0)
cache_pos = body.find('RuntimeTranspilerCache')
if cache_pos < insp_pos:
    sys.exit(1)
"; then
    pass 0.15 "Cache disable is gated on inspector being enabled"
else
    fail 0.15 "Cache disable is not properly gated on inspector check"
fi

# ── Fail-to-pass: cache disable applies to ALL inspector modes (0.15) ──
# [pr_diff] (0.15): Cache disable must apply to all modes including connect
# WHY structural: Zig code requires full build toolchain
if python3 -c "
import sys, re
body = '''$CONFIGURE_DEBUGGER'''
# The cache disable must NOT be exclusively inside a mode != .connect branch.
# Strategy: find the cache disable line and check it's not wrapped in a narrow mode check.
lines = body.split('\n')
cache_line_idx = None
for i, line in enumerate(lines):
    if 'RuntimeTranspilerCache' in line and ('is_disabled' in line or 'disable(' in line):
        cache_line_idx = i
        break
if cache_line_idx is None:
    sys.exit(1)

# Check backwards from cache line for a mode-conditional that would exclude .connect
# Look for patterns like: if (mode != .connect) or switch on mode that excludes connect
# within the nearest enclosing block
preceding = '\n'.join(lines[max(0, cache_line_idx-15):cache_line_idx])
# If there's a mode != .connect check in the preceding lines without a closing brace between,
# and the cache disable is more indented, it's likely gated
mode_exclude_pattern = re.search(r'(mode\s*!=\s*\.connect|mode\s*!=\s*InspectorMode\.connect)', preceding)
if mode_exclude_pattern:
    # Find if there's a closing brace at same/lesser indent between the mode check and cache line
    mode_line = preceding[:mode_exclude_pattern.end()].count('\n')
    cache_line = lines[cache_line_idx]
    cache_indent = len(cache_line) - len(cache_line.lstrip())
    # Check if the mode check's block is still open at the cache line
    brace_depth = 0
    for line in lines[max(0, cache_line_idx-15) + mode_line:cache_line_idx]:
        brace_depth += line.count('{') - line.count('}')
    if brace_depth > 0:
        # Cache disable IS inside the mode != .connect block — fail
        sys.exit(1)
"; then
    pass 0.15 "Cache disable applies to all inspector modes"
else
    fail 0.15 "Cache disable is incorrectly gated on specific mode"
fi

# ── Pass-to-pass: minification disabling preserved in configureDebugger (0.10) ──
# [pr_diff] (0.10): Existing debugger options (minify_identifiers etc.) must be preserved
if grep -q 'minify_identifiers = false' "$VM_FILE" && \
   grep -q 'minify_syntax = false' "$VM_FILE" && \
   grep -q 'minify_whitespace = false' "$VM_FILE" && \
   grep -q 'options.debugger = true' "$VM_FILE"; then
    pass 0.10 "Debugger minification settings preserved"
else
    fail 0.10 "Debugger minification settings missing"
fi

# ── Pass-to-pass: Arguments.zig still handles --inspect flags (0.05) ──
# [pr_diff] (0.05): CLI inspect flag handling must not be broken
if grep -q '\-\-inspect"' "$ARGS_FILE" && \
   grep -q '\-\-inspect-wait"' "$ARGS_FILE" && \
   grep -q '\-\-inspect-brk"' "$ARGS_FILE"; then
    pass 0.05 "Arguments.zig still handles --inspect flags"
else
    fail 0.05 "Arguments.zig --inspect flag handling broken"
fi

# ── Structural: anti-stub — VirtualMachine.zig has meaningful changes (0.05) ──
# [pr_diff] (0.05): Changes must be non-trivial (not just comments or whitespace)
DIFF_LINES=$(cd "$REPO" && git diff HEAD -- src/bun.js/VirtualMachine.zig 2>/dev/null | grep '^[+-]' | grep -v '^[+-][+-][+-]' | grep -v '^[+-]$' | grep -v '^[+-]\s*\/\/' | wc -l)
if [ "$DIFF_LINES" -ge 2 ]; then
    pass 0.05 "Non-trivial changes in VirtualMachine.zig"
else
    fail 0.05 "Changes appear to be stub or trivial"
fi

# ── Config-derived: no @import inside functions (0.05) ──
# [agent_config] (0.05): "Never use @import() inline inside of functions" — src/CLAUDE.md:11 @ 047cedb
if python3 -c "
import sys, subprocess
diff = subprocess.run(
    ['git', 'diff', 'HEAD', '--', 'src/bun.js/VirtualMachine.zig'],
    capture_output=True, text=True, cwd='$REPO'
).stdout
added = [l[1:] for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
for line in added:
    stripped = line.strip()
    if '@import(' in stripped and 'const' not in stripped.split('@import')[0]:
        sys.exit(1)
"; then
    pass 0.05 "No inline @import in added lines"
else
    fail 0.05 "Found inline @import in added function code"
fi

# ── Config-derived: uses bun.* APIs not std.* (0.05) ──
# [agent_config] (0.05): "Always use bun.* APIs instead of std.*" — src/CLAUDE.md:16 @ 047cedb
if python3 -c "
import sys, subprocess
diff = subprocess.run(
    ['git', 'diff', 'HEAD', '--', 'src/bun.js/VirtualMachine.zig', 'src/cli/Arguments.zig'],
    capture_output=True, text=True, cwd='$REPO'
).stdout
added = [l[1:] for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
forbidden = ['std.fs.', 'std.posix.', 'std.os.', 'std.process.']
for line in added:
    for f in forbidden:
        if f in line:
            sys.exit(1)
"; then
    pass 0.05 "No forbidden std.* API usage in added lines"
else
    fail 0.05 "Found forbidden std.* API usage"
fi

# ── Final score ──────────────────────────────────────────────────────
echo ""
echo "Deterministic score: $SCORE / $TOTAL"
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
s = $SCORE
json.dump({
    'reward': s,
    'behavioral': min(s, 0.65),
    'regression': min(max(s - 0.65, 0), 0.15),
    'config': min(max(s - 0.80, 0), 0.10),
    'structural': min(max(s - 0.90, 0), 0.10)
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
