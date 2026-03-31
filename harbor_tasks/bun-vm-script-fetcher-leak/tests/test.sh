#!/usr/bin/env bash
set +e  # Don't exit on individual check failure

HEADER="src/bun.js/bindings/NodeVMScriptFetcher.h"
TOTAL=0.0
add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

BEHAVIORAL=0.0
REGRESSION=0.0
CONFIG=0.0
b_add() { BEHAVIORAL=$(python3 -c "print(round($BEHAVIORAL + $1, 4))"); add "$1"; }
r_add() { REGRESSION=$(python3 -c "print(round($REGRESSION + $1, 4))"); add "$1"; }
c_add() { CONFIG=$(python3 -c "print(round($CONFIG + $1, 4))"); add "$1"; }

# Helper: strip C++ comments for robust pattern matching (anti-gaming)
strip_cpp_comments() {
    python3 -c "
import re, sys
code = open(sys.argv[1]).read()
code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
code = re.sub(r'//[^\n]*', '', code)
print(code)
" "$1"
}

########################################
# GATE: Header file exists and is non-empty
########################################
# [pr_diff] (gate): NodeVMScriptFetcher.h must exist
if [ ! -s "$HEADER" ]; then
  echo "GATE FAILED: $HEADER missing or empty"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
  exit 0
fi

STRIPPED=$(strip_cpp_comments "$HEADER")

########################################
# GATE: Class definition must be intact
########################################
# [pr_diff] (gate): Class definition must be present (checked on comment-stripped source)
if ! echo "$STRIPPED" | grep -q 'class NodeVMScriptFetcher'; then
  echo "GATE FAILED: NodeVMScriptFetcher class definition missing"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
  exit 0
fi

########################################
# BEHAVIORAL: Core fix — Strong reference must be removed
########################################

# [pr_diff] (0.30): m_owner must NOT use Strong reference (breaks the GC cycle)
# WHY structural: C++ header in compiled Zig/CMake runtime, cannot execute
# This is the primary check — the root cause is the Strong handle acting as a GC root.
# Checked on comment-stripped source to prevent gaming via comment injection.
if ! echo "$STRIPPED" | grep -qP 'Strong<[^>]*>\s+m_owner'; then
  echo "PASS: m_owner does not use Strong reference (GC cycle breakable)"
  b_add 0.30
else
  echo "FAIL: m_owner still uses Strong reference — GC cycle not broken"
fi

# [pr_diff] (0.20): m_owner must use Weak reference to allow GC collection
# WHY structural: C++ compiled runtime, cannot execute
# Accept any Weak<T> type parameter (JSCell, Unknown, etc.) — the key is Weak not Strong.
if echo "$STRIPPED" | grep -qP 'Weak<[^>]*>\s+m_owner'; then
  echo "PASS: m_owner uses Weak reference"
  b_add 0.20
else
  echo "FAIL: m_owner should use Weak reference for GC-safe back-reference"
fi

# [pr_diff] (0.10): owner() getter must handle cleared/null weak ref safely
# WHY structural: C++ method, cannot call without compiling bun
# Accept jsUndefined(), jsNull(), or JSValue() as valid safe fallbacks
if echo "$STRIPPED" | grep -qP 'owner\s*\(' && \
   echo "$STRIPPED" | grep -qP 'jsUndefined|jsNull|JSValue\s*\(\s*\)'; then
  echo "PASS: owner() has safe fallback for cleared weak ref"
  b_add 0.10
else
  echo "FAIL: owner() must return a safe value when weak ref is cleared"
fi

# [pr_diff] (0.05): owner setter must guard against non-cell values
# WHY structural: C++ method, cannot call without compiling bun
# Accept isCell(), isObject(), or asCell() as valid guard patterns
if echo "$STRIPPED" | grep -qP 'isCell|isObject|asCell'; then
  echo "PASS: Owner setter has cell/object guard"
  b_add 0.05
else
  echo "FAIL: Owner setter should guard against non-cell values"
fi

# [pr_diff] (0.05): Must include Weak-related header
# WHY structural: C++ include requirement for Weak type
# Accept Weak.h OR WeakInlines.h (WeakInlines.h transitively includes Weak.h)
if echo "$STRIPPED" | grep -qP '#include\s+<JavaScriptCore/Weak(Inlines)?\.h>'; then
  echo "PASS: Weak header included"
  b_add 0.05
else
  echo "FAIL: Missing Weak.h or WeakInlines.h include"
fi

########################################
# BEHAVIORAL: Regression test for the leak
########################################

# [pr_diff] (0.10): Regression test file must exist and cover the leak scenario
TESTFILE=""
for f in test/js/node/vm/vm-script-fetcher-leak.test.ts \
         test/js/node/vm/vm-leak.test.ts \
         test/js/node/vm/*.test.ts \
         test/regression/**/*.test.ts; do
  if [ -f "$f" ] && grep -q 'vm' "$f" 2>/dev/null && \
     grep -qP 'heap|leak|gc|GC|Script' "$f" 2>/dev/null; then
    TESTFILE="$f"
    break
  fi
done

# Also check for any new test file referencing the leak
if [ -z "$TESTFILE" ]; then
  TESTFILE=$(find test/ -name '*.test.ts' -newer "$HEADER" 2>/dev/null | head -1 || true)
fi

if [ -n "$TESTFILE" ] && [ -f "$TESTFILE" ]; then
  HAS_SCRIPT=false; HAS_COMPILE=false; HAS_MODULE=false
  grep -qP 'vm\.Script|new\s+Script|Script\(' "$TESTFILE" 2>/dev/null && HAS_SCRIPT=true
  grep -qP 'compileFunction|compile_function' "$TESTFILE" 2>/dev/null && HAS_COMPILE=true
  grep -qP 'SourceTextModule|source.*[Mm]odule' "$TESTFILE" 2>/dev/null && HAS_MODULE=true

  if $HAS_SCRIPT && $HAS_COMPILE && $HAS_MODULE; then
    echo "PASS: Regression test covers all three APIs ($TESTFILE)"
    b_add 0.10
  elif $HAS_SCRIPT; then
    echo "PARTIAL: Regression test covers vm.Script only ($TESTFILE)"
    b_add 0.05
  else
    echo "FAIL: Regression test doesn't cover the leak scenario"
  fi
else
  echo "FAIL: No regression test file found for the memory leak"
fi

########################################
# REGRESSION: Existing class structure preserved
########################################

# [repo_tests] (0.05): Must still extend ScriptFetcher
if echo "$STRIPPED" | grep -qP 'class NodeVMScriptFetcher[^{]*public[^{]*ScriptFetcher'; then
  echo "PASS: Class inheritance preserved"
  r_add 0.05
else
  echo "FAIL: Must still extend JSC::ScriptFetcher"
fi

# [repo_tests] (0.05): dynamicImportCallback() must still exist
if echo "$STRIPPED" | grep -q 'dynamicImportCallback'; then
  echo "PASS: dynamicImportCallback preserved"
  r_add 0.05
else
  echo "FAIL: dynamicImportCallback method missing"
fi

# [repo_tests] (0.05): m_owner field must still exist (not simply deleted)
if echo "$STRIPPED" | grep -q 'm_owner'; then
  echo "PASS: m_owner field preserved (not stubbed out by deletion)"
  r_add 0.05
else
  echo "FAIL: m_owner removed entirely — owner() must still work"
fi

########################################
# CONFIG: Agent config checks
########################################

# [agent_config] (0.025): Test uses describe blocks — test/CLAUDE.md:~line 42 @ 594f421f
if [ -n "$TESTFILE" ] && [ -f "$TESTFILE" ] && grep -q 'describe(' "$TESTFILE"; then
  echo "PASS: Test uses describe blocks per test/CLAUDE.md"
  c_add 0.025
else
  echo "FAIL: Test should use describe blocks (test/CLAUDE.md convention)"
fi

# [agent_config] (0.025): Test imports from bun:test — test/CLAUDE.md:~line 10 @ 594f421f
if [ -n "$TESTFILE" ] && [ -f "$TESTFILE" ] && grep -qP "from ['\"]bun:test['\"]" "$TESTFILE"; then
  echo "PASS: Test imports from bun:test"
  c_add 0.025
else
  echo "FAIL: Test should import from bun:test (test/CLAUDE.md convention)"
fi

########################################
# Compute final reward
########################################

echo ""
echo "=== SCORE BREAKDOWN ==="
echo "Behavioral:  $BEHAVIORAL"
echo "Regression:  $REGRESSION"
echo "Config:      $CONFIG"
echo "Total:       $TOTAL"

echo "$TOTAL" > /logs/verifier/reward.txt
python3 -c "
import json
print(json.dumps({
    'reward': $TOTAL,
    'behavioral': $BEHAVIORAL,
    'regression': $REGRESSION,
    'config': $CONFIG,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
