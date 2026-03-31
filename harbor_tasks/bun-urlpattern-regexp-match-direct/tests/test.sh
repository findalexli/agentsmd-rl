#!/usr/bin/env bash
set +e

REPO="/workspace/bun"
SCORE=0
DETAILS=""

add_result() {
    local weight="$1" pass="$2" desc="$3"
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}PASS ($weight): $desc\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $desc\n"
    fi
}

# Helper: strip C/C++ comments from source for robust checking
strip_comments() {
    python3 -c "
import re, sys
src = open(sys.argv[1]).read()
# Remove // line comments
src = re.sub(r'//[^\n]*', '', src)
# Remove /* */ block comments
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)
print(src)
" "$1"
}

COMP_CPP="$REPO/src/bun.js/bindings/webcore/URLPatternComponent.cpp"
COMP_H="$REPO/src/bun.js/bindings/webcore/URLPatternComponent.h"
PAT_CPP="$REPO/src/bun.js/bindings/webcore/URLPattern.cpp"
CONSTR_CPP="$REPO/src/bun.js/bindings/webcore/URLPatternConstructorStringParser.cpp"

# =============================================================================
# GATE: Files exist and are not truncated
# WHY structural: C++ requires full Bun build toolchain (cmake/zig/clang);
# cannot compile or call URLPattern functions without rebuilding Bun
# =============================================================================

# [pr_diff] GATE: Key source files must exist and have balanced braces
if python3 -c "
import sys
for f in ['$COMP_CPP', '$COMP_H', '$PAT_CPP']:
    content = open(f).read()
    if abs(content.count('{') - content.count('}')) > 3:
        print(f'Unbalanced braces in {f}')
        sys.exit(1)
    if len(content) < 500:
        print(f'File too short: {f}')
        sys.exit(1)
"; then
    echo "GATE PASS: Source files structurally intact"
else
    echo "GATE FAIL: Source file structural problems"
    echo "0.0" > "/logs/verifier/reward.txt"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > "/logs/verifier/reward.json"
    exit 0
fi

# =============================================================================
# FAIL-TO-PASS 1 (0.30): Core bug fix — RegExpObject allocation removed from
# component matching, replaced with direct RegExp::match using ovector
# WHY structural: C++ compiled binary, cannot call without full build
# =============================================================================

# [pr_diff] (0.30): The old exec-via-RegExpObject pattern is replaced with
# direct regex matching that reads capture offsets from the ovector buffer.
# Checks: (a) RegExpObject::create gone from component code (the bug source),
# (b) direct match call exists, (c) ovector offsets are read with arithmetic,
# (d) the new method returns optional (no intermediate JSValue needed).
PASS_CORE=0
if python3 -c "
import re, sys

# Strip comments to prevent injection
src_raw = open('$COMP_CPP').read()
src = re.sub(r'//[^\n]*', '', src_raw)
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)

header_raw = open('$COMP_H').read()
header = re.sub(r'//[^\n]*', '', header_raw)
header = re.sub(r'/\*.*?\*/', '', header, flags=re.DOTALL)

# (a) RegExpObject::create must be gone — this is THE bug
if 'RegExpObject::create' in src:
    print('FAIL: RegExpObject::create still present')
    sys.exit(1)

# (b) Some form of direct regex match must exist: match(, matchInline(, etc.
# Accept any method call on a RegExp pointer that does matching
if not re.search(r'(?:regExp|m_regularExpression|regularExpression)\s*(?:\(\))?\s*->\s*match\w*\s*\(', src):
    # Also accept: RegExp:: static methods
    if not re.search(r'RegExp\s*::\s*match\w*\s*\(', src):
        print('FAIL: No direct RegExp match call found')
        sys.exit(1)

# (c) Ovector offset arithmetic: accessing ovector[i*2] or ovector[2*i] etc.
# This is the key correctness detail — reading capture group start/end from ovector
if not re.search(r'ovector\w*\s*\[.*?[*].*?2|ovector\w*\s*\[.*?2.*?[*]', src):
    # Also accept: ovectorSpan access with index arithmetic
    if not re.search(r'(?:ovector|ovectorSpan)\w*\s*\[', src):
        print('FAIL: No ovector index access found')
        sys.exit(1)

# (d) A method returning optional<URLPatternComponentResult> must exist in header
# (replaces the old two-method componentExec+createComponentMatchResult pattern)
if not re.search(r'std::optional\s*<\s*URLPatternComponentResult\s*>', header):
    # Accept equivalent: Optional<URLPatternComponentResult> (WTF style)
    if not re.search(r'Optional\s*<\s*URLPatternComponentResult\s*>', header):
        print('FAIL: No optional-returning component match method in header')
        sys.exit(1)

print('PASS: Core fix verified')
" 2>/dev/null; then
    PASS_CORE=1
fi
add_result 0.30 "$PASS_CORE" "[pr_diff] RegExpObject removed, direct match+ovector used, returns optional"

# =============================================================================
# FAIL-TO-PASS 2 (0.20): matchSpecialSchemeProtocol uses direct matching
# WHY structural: C++ compiled binary
# =============================================================================

# [pr_diff] (0.20): matchSpecialSchemeProtocol must not create RegExpObject.
# It should iterate special schemes and use direct RegExp matching.
PASS_SPECIAL=0
if python3 -c "
import re, sys

src_raw = open('$COMP_CPP').read()
src = re.sub(r'//[^\n]*', '', src_raw)
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)

# Extract matchSpecialSchemeProtocol function body
fn = re.search(r'matchSpecialSchemeProtocol\s*\([^)]*\)\s*(?:const\s*)?\{(.*?)^\}', src, re.DOTALL | re.MULTILINE)
if not fn:
    print('FAIL: matchSpecialSchemeProtocol function not found')
    sys.exit(1)

body = fn.group(1)

# Must NOT have RegExpObject::create or ->exec( — the old pattern
if 'RegExpObject::create' in body or '->exec(' in body:
    print('FAIL: Still uses old RegExpObject exec pattern')
    sys.exit(1)

# Must have some form of direct matching: ->match, ->test, ->matchInline, etc.
if not re.search(r'->\s*(?:match|test|matchInline)\w*\s*\(', body):
    print('FAIL: No direct matching call in matchSpecialSchemeProtocol')
    sys.exit(1)

# Must iterate special schemes (for/range loop, or find_if, or any_of)
if not re.search(r'for\s*\(|find_if|any_of|ranges::', body):
    print('FAIL: No iteration over special schemes')
    sys.exit(1)

# Non-trivial: at least 3 real statements
lines = [l.strip() for l in body.split('\\n') if l.strip() and not l.strip().startswith('//')]
if len(lines) < 3:
    print('FAIL: Function body too trivial')
    sys.exit(1)

print('PASS: matchSpecialSchemeProtocol fixed')
" 2>/dev/null; then
    PASS_SPECIAL=1
fi
add_result 0.20 "$PASS_SPECIAL" "[pr_diff] matchSpecialSchemeProtocol uses direct matching, no RegExpObject"

# =============================================================================
# FAIL-TO-PASS 3 (0.15): URLPattern::match consolidates lock and removes
# per-component componentExec calls
# WHY structural: C++ compiled binary
# =============================================================================

# [pr_diff] (0.15): URLPattern::match must not have 8 separate componentExec
# calls with individual lock acquisitions. The old pattern had 8 blocks of
# componentExec + createComponentMatchResult. The fix consolidates.
PASS_MATCH=0
if python3 -c "
import re, sys

src_raw = open('$PAT_CPP').read()
src = re.sub(r'//[^\n]*', '', src_raw)
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)

# Find URLPattern::match function
fn = re.search(r'URLPattern::match\s*\(.*?\)\s*\{(.*?)(?=\n\w.*?::\w|\Z)', src, re.DOTALL)
if not fn:
    print('FAIL: URLPattern::match not found')
    sys.exit(1)

body = fn.group(1)

# The old pattern: componentExec called per-component (8 times in base code)
exec_calls = len(re.findall(r'componentExec\s*\(', body))
if exec_calls > 2:
    print(f'FAIL: Still has {exec_calls} componentExec calls (old pattern)')
    sys.exit(1)

# The old pattern: createComponentMatchResult called per-component
create_calls = len(re.findall(r'createComponentMatchResult\s*\(', body))
if create_calls > 2:
    print(f'FAIL: Still has {create_calls} createComponentMatchResult calls')
    sys.exit(1)

# Must still reference all 8 components (protocol through hash)
components = ['protocol', 'username', 'password', 'hostname', 'pathname', 'port', 'search', 'hash']
found = sum(1 for c in components if re.search(r'm_' + c + r'Component', body))
if found < 7:
    print(f'FAIL: Only {found}/8 components referenced in match')
    sys.exit(1)

# Lock acquisition count should be small (1-2, not 8)
lock_count = len(re.findall(r'JSLockHolder|JSLock\b', body))
if lock_count > 3:
    print(f'FAIL: {lock_count} lock acquisitions (should be consolidated)')
    sys.exit(1)

print('PASS: URLPattern::match consolidated')
" 2>/dev/null; then
    PASS_MATCH=1
fi
add_result 0.15 "$PASS_MATCH" "[pr_diff] URLPattern::match removes per-component exec, consolidates locking"

# =============================================================================
# PASS-TO-PASS (0.10): Core API surface still intact
# =============================================================================

# [repo_tests] (0.10): Key types and methods remain in headers and source
PASS_P2P=0
if python3 -c "
import sys

h = open('$COMP_H').read()
cpp = open('$COMP_CPP').read()
pat = open('$PAT_CPP').read()

checks = [
    ('class URLPatternComponent', h, 'header'),
    ('compile(', h, 'header'),
    ('patternString()', h, 'header'),
    ('matchSpecialSchemeProtocol(', h, 'header'),
    ('m_regularExpression', h, 'header'),
    ('m_groupNameList', h, 'header'),
    ('URLPattern::match', pat, 'URLPattern.cpp'),
    ('specialSchemeList', cpp, 'URLPatternComponent.cpp'),
    ('namespace WebCore', cpp, 'URLPatternComponent.cpp'),
]

for needle, haystack, location in checks:
    if needle not in haystack:
        print(f'MISSING in {location}: {needle}')
        sys.exit(1)

print('PASS: API surface intact')
" 2>/dev/null; then
    PASS_P2P=1
fi
add_result 0.10 "$PASS_P2P" "[repo_tests] Core URLPattern API surface preserved"

# =============================================================================
# ANTI-STUB (0.10): The component matching replacement has real capture logic
# WHY structural: C++ compiled binary
# =============================================================================

# [pr_diff] (0.10): The method that replaced componentExec+createComponentMatchResult
# must have substantial capture-group extraction logic: iteration over subpatterns,
# building group name/value pairs, and substring extraction.
PASS_STUB=0
if python3 -c "
import re, sys

src_raw = open('$COMP_CPP').read()
src = re.sub(r'//[^\n]*', '', src_raw)
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)

# Find any method returning optional<URLPatternComponentResult> or URLPatternComponentResult
fn = re.search(r'(?:optional|Optional)\s*<\s*URLPatternComponentResult\s*>\s+\w+::\w+\s*\([^)]*\)\s*(?:const\s*)?\{(.*?)^\}', src, re.DOTALL | re.MULTILINE)
if not fn:
    # Also accept: method that returns URLPatternComponentResult directly
    fn = re.search(r'URLPatternComponentResult\s+\w+::\w+\s*\([^)]*\)\s*(?:const\s*)?\{(.*?)^\}', src, re.DOTALL | re.MULTILINE)
    if not fn:
        print('FAIL: No component match result method found')
        sys.exit(1)

body = fn.group(1)

# Must have iteration (for/while/range-based)
has_loop = bool(re.search(r'(?:for|while)\s*\(', body))

# Must reference group names (m_groupNameList or groupNameList or similar)
has_groups = bool(re.search(r'(?:groupName|m_groupNameList|NameMatchPair|GroupsRecord)', body))

# Must have substring/offset extraction from the match
has_extraction = bool(re.search(r'substring|subpattern|numSubpattern|start.*end|ovector', body, re.IGNORECASE))

# Must be substantial (>= 10 real lines)
lines = [l for l in body.strip().split('\\n') if l.strip()]
is_substantial = len(lines) >= 10

score = sum([has_loop, has_groups, has_extraction, is_substantial])
if score < 3:
    print(f'FAIL: Only {score}/4 substance checks passed (loop={has_loop}, groups={has_groups}, extraction={has_extraction}, substantial={is_substantial})')
    sys.exit(1)

print('PASS: Component match method has real capture logic')
" 2>/dev/null; then
    PASS_STUB=1
fi
add_result 0.10 "$PASS_STUB" "[pr_diff] Component match replacement has real capture-group extraction (anti-stub)"

# =============================================================================
# CONFIG-DERIVED (0.05): No RegExpObject.h include in component code
# =============================================================================

# [agent_config] (0.05): RegExpObject.h should not be included — CLAUDE.md:82 @ 2920fac
PASS_CFG=0
if python3 -c "
import re, sys

src_raw = open('$COMP_CPP').read()
src = re.sub(r'//[^\n]*', '', src_raw)
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)

if re.search(r'#include.*RegExpObject\.h', src):
    print('FAIL: Still includes RegExpObject.h')
    sys.exit(1)

print('PASS: RegExpObject.h not included')
" 2>/dev/null; then
    PASS_CFG=1
fi
add_result 0.05 "$PASS_CFG" "[agent_config] No RegExpObject.h include in URLPatternComponent — CLAUDE.md:82 @ 2920fac"

# =============================================================================
# CROSS-FILE COHERENCE (0.10): URLPatternConstructorStringParser updated
# =============================================================================

# [pr_diff] (0.10): matchSpecialSchemeProtocol signature changed from taking
# ScriptExecutionContext& to JSGlobalObject*. The call site in
# URLPatternConstructorStringParser.cpp must be updated to pass globalObject().
PASS_CALLSITE=0
if python3 -c "
import re, sys

src_raw = open('$CONSTR_CPP').read()
src = re.sub(r'//[^\n]*', '', src_raw)
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)

# Find the call to matchSpecialSchemeProtocol
call = re.search(r'matchSpecialSchemeProtocol\s*\(([^)]*)\)', src)
if not call:
    print('FAIL: matchSpecialSchemeProtocol call not found in constructor string parser')
    sys.exit(1)

arg = call.group(1).strip()
# Must pass globalObject (not context directly)
# Accept: context.globalObject(), globalObject, m_globalObject, etc.
if re.search(r'globalObject', arg):
    print('PASS: Passes globalObject')
    sys.exit(0)

# If still passing bare 'context' without .globalObject(), it's the old signature
if arg == 'context' or arg == 'm_context':
    print('FAIL: Still passing context directly (old signature)')
    sys.exit(1)

# Accept other reasonable arguments
print('PASS: Argument updated')
" 2>/dev/null; then
    PASS_CALLSITE=1
fi
add_result 0.10 "$PASS_CALLSITE" "[pr_diff] URLPatternConstructorStringParser updated for new matchSpecialSchemeProtocol signature"

# =============================================================================
# RESULTS
# =============================================================================

echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo "Score: $SCORE / 1.00"

FINAL=$(python3 -c "print(f'{min(1.0, max(0.0, $SCORE)):.4f}')")
echo "$FINAL" > "/logs/verifier/reward.txt"

BEH=$(python3 -c "print(round($PASS_CORE * 0.30 + $PASS_SPECIAL * 0.20 + $PASS_MATCH * 0.15 + $PASS_CALLSITE * 0.10, 4))")
REG=$(python3 -c "print(round($PASS_P2P * 0.10, 4))")
STUB=$(python3 -c "print(round($PASS_STUB * 0.10, 4))")
CFG=$(python3 -c "print(round($PASS_CFG * 0.05, 4))")

echo "{\"reward\": $FINAL, \"behavioral\": $BEH, \"regression\": $REG, \"anti_stub\": $STUB, \"config\": $CFG, \"style_rubric\": 0.0}" > "/logs/verifier/reward.json"

echo "Final reward: $FINAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
