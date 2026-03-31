#!/usr/bin/env bash
set +e

REPO="/repo"
TARGET="$REPO/src/bun.js/bindings/JSGlobalObject.zig"
TOTAL=0
REWARD_FILE="/logs/verifier/reward.txt"
REWARD_JSON="/logs/verifier/reward.json"
ANALYSIS_FILE="/tmp/analysis.json"

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

write_results() {
  echo "$TOTAL" > "$REWARD_FILE"
  echo "{\"reward\":$TOTAL,\"behavioral\":$behavioral,\"regression\":$regression,\"config\":$config}" > "$REWARD_JSON"
  echo ""
  echo "=== SCORE: $TOTAL ==="
  echo "  behavioral: $behavioral"
  echo "  regression: $regression"
  echo "  config:     $config"
}

# ── GATE: Target file exists and is non-empty ──
# [pr_diff] (0): File must exist
if [ ! -s "$TARGET" ]; then
  echo "GATE FAIL: $TARGET missing or empty"
  echo "0.0" > "$REWARD_FILE"
  echo '{"reward":0,"behavioral":0,"regression":0,"config":0}' > "$REWARD_JSON"
  exit 0
fi

# ── Consolidated Zig source analysis ──
# Strips BOTH comments AND string literals to prevent gaming via injection.
# Uses brace-counting for catch blocks, verifies call-before-return ordering.
python3 << 'PYEOF' > "$ANALYSIS_FILE"
import re, sys, json

TARGET = "/repo/src/bun.js/bindings/JSGlobalObject.zig"

with open(TARGET) as f:
    raw = f.read()

def strip_zig_comments_and_strings(code):
    """Remove // line comments AND string literals to prevent gaming via injection."""
    # Strip line comments
    code = re.sub(r'//[^\n]*', '', code)
    # Strip double-quoted string literals (handles escaped quotes)
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
    return code

clean = strip_zig_comments_and_strings(raw)

def find_fn_region(code, fn_name, size=3000):
    """Find a pub fn and return its region, bounded by the next pub fn or size chars."""
    marker = f'pub fn {fn_name}'
    idx = code.find(marker)
    if idx < 0:
        return None
    next_fn = code.find('pub fn ', idx + len(marker))
    end = idx + size
    if next_fn > 0:
        end = min(end, next_fn)
    return code[idx:end]

def extract_catch_bodies(region):
    """Extract catch block bodies using brace counting (handles nested {})."""
    if region is None:
        return []
    bodies = []
    for m in re.finditer(r'catch\s*(?:\|[^|]*\|)?\s*\{', region):
        start = m.end()
        depth = 1
        i = start
        while i < len(region) and depth > 0:
            if region[i] == '{':
                depth += 1
            elif region[i] == '}':
                depth -= 1
            i += 1
        if depth == 0:
            bodies.append(region[start:i-1])
    return bodies

def catch_has_clear_before_return(region):
    """Check if any catch block calls clearExceptionExceptTermination() BEFORE a return.

    Verifies:
    1. The call is a real method call (preceded by dot, has parens)
    2. The call appears before the return statement in the catch body
    """
    for body in extract_catch_bodies(region):
        # Check for actual method call: .clearExceptionExceptTermination()
        # Must be a dot-accessed method call, not a bare string
        clear_match = re.search(r'\.\s*clearExceptionExceptTermination\s*\(\s*\)', body)
        return_match = re.search(r'\breturn\b', body)
        if clear_match and return_match and clear_match.start() < return_match.start():
            return True
    return False

def catch_returns_typed_error(region, type_method):
    """Check if a catch block with clear also returns the specific error type.

    e.g. for createTypeErrorInstance, the return should use toTypeErrorInstance not toErrorInstance.
    """
    for body in extract_catch_bodies(region):
        clear_match = re.search(r'\.\s*clearExceptionExceptTermination\s*\(\s*\)', body)
        return_match = re.search(r'\breturn\b', body)
        if clear_match and return_match and clear_match.start() < return_match.start():
            # Check if the return statement (and code after it) references the typed method
            return_onwards = body[return_match.start():]
            if re.search(r'\.' + type_method + r'\s*\(', return_onwards):
                return True
    return False

def catch_still_has_generic_error(region):
    """Check if a catch block ONLY returns generic toErrorInstance (not the typed variant).

    This catches the original bug where TypeError/SyntaxError/RangeError functions
    incorrectly returned generic Error instances.
    """
    for body in extract_catch_bodies(region):
        return_match = re.search(r'\breturn\b', body)
        if return_match:
            return_onwards = body[return_match.start():]
            if '.toErrorInstance(' in return_onwards:
                return True
    return False

results = {}

# ── Check createErrorInstance ──
r1 = find_fn_region(clean, 'createErrorInstance')
results['error_fn_exists'] = r1 is not None
results['error_clear_ordered'] = catch_has_clear_before_return(r1)

# ── Check createTypeErrorInstance ──
r2 = find_fn_region(clean, 'createTypeErrorInstance')
results['type_error_fn_exists'] = r2 is not None
results['type_error_clear_ordered'] = catch_has_clear_before_return(r2)
results['type_error_typed_return'] = catch_returns_typed_error(r2, 'toTypeErrorInstance')
results['type_error_generic_bug'] = catch_still_has_generic_error(r2)

# ── Check createSyntaxErrorInstance ──
r3 = find_fn_region(clean, 'createSyntaxErrorInstance')
results['syntax_error_fn_exists'] = r3 is not None
results['syntax_error_clear_ordered'] = catch_has_clear_before_return(r3)
results['syntax_error_typed_return'] = catch_returns_typed_error(r3, 'toSyntaxErrorInstance')
results['syntax_error_generic_bug'] = catch_still_has_generic_error(r3)

# ── Check createRangeErrorInstance ──
r4 = find_fn_region(clean, 'createRangeErrorInstance')
results['range_error_fn_exists'] = r4 is not None
results['range_error_clear_ordered'] = catch_has_clear_before_return(r4)
results['range_error_typed_return'] = catch_returns_typed_error(r4, 'toRangeErrorInstance')
results['range_error_generic_bug'] = catch_still_has_generic_error(r4)

# ── createDOMExceptionInstance should NOT have the clear call ──
r_dom = find_fn_region(clean, 'createDOMExceptionInstance')
if r_dom is None:
    results['dom_exception_clean'] = True
else:
    results['dom_exception_clean'] = not bool(
        re.search(r'\.\s*clearExceptionExceptTermination\s*\(\s*\)', r_dom)
    )

# ── File integrity ──
results['line_count'] = len(raw.splitlines())

# ── Count actual clear calls across the 4 target functions only ──
clear_count = 0
for region in [r1, r2, r3, r4]:
    if region:
        clear_count += len(re.findall(r'\.\s*clearExceptionExceptTermination\s*\(\s*\)', region))
results['target_clear_count'] = clear_count

print(json.dumps(results))
PYEOF

if [ ! -s "$ANALYSIS_FILE" ]; then
  echo "GATE FAIL: Analysis script produced no output"
  echo "0.0" > "$REWARD_FILE"
  echo '{"reward":0,"behavioral":0,"regression":0,"config":0}' > "$REWARD_JSON"
  exit 0
fi

get_val() {
  python3 -c "import json; d=json.load(open('$ANALYSIS_FILE')); print(d.get('$1', False))"
}

# ── GATE: All 4 target functions must exist ──
# [pr_diff] (0): Functions must not be removed
ALL_FNS_EXIST=true
for fn in error_fn_exists type_error_fn_exists syntax_error_fn_exists range_error_fn_exists; do
  if [ "$(get_val $fn)" != "True" ]; then
    ALL_FNS_EXIST=false
    echo "GATE FAIL: Required function missing ($fn)"
  fi
done
if [ "$ALL_FNS_EXIST" = "false" ]; then
  echo "0.0" > "$REWARD_FILE"
  echo '{"reward":0,"behavioral":0,"regression":0,"config":0}' > "$REWARD_JSON"
  exit 0
fi

GATE_PASSED=true

# ── Check 1 (0.25): createErrorInstance catch clears pending exception before return ──
# [pr_diff] (0.25): catch in createErrorInstance must call .clearExceptionExceptTermination() BEFORE return
if [ "$(get_val error_clear_ordered)" = "True" ]; then
  echo "PASS: createErrorInstance catch clears pending exception before return"
  add_score 0.25 behavioral
else
  echo "FAIL: createErrorInstance catch does not clear pending exception before return"
  GATE_PASSED=false
fi

# ── Check 2 (0.25): createTypeErrorInstance catch clears + returns TypeError ──
# [pr_diff] (0.25): catch must clear exception before return AND return a TypeErrorInstance
TYPE_CLEAR=$(get_val type_error_clear_ordered)
TYPE_RET=$(get_val type_error_typed_return)
TYPE_BUG=$(get_val type_error_generic_bug)
if [ "$TYPE_CLEAR" = "True" ] && [ "$TYPE_RET" = "True" ] && [ "$TYPE_BUG" != "True" ]; then
  echo "PASS: createTypeErrorInstance catch clears exception and returns TypeError"
  add_score 0.25 behavioral
elif [ "$TYPE_CLEAR" = "True" ]; then
  echo "PARTIAL: createTypeErrorInstance catch clears exception but wrong return type"
  add_score 0.10 behavioral
else
  echo "FAIL: createTypeErrorInstance catch does not clear pending exception"
  GATE_PASSED=false
fi

# ── Check 3 (0.15): createSyntaxErrorInstance catch clears + returns SyntaxError ──
# [pr_diff] (0.15): catch must clear exception before return AND return a SyntaxErrorInstance
SYNTAX_CLEAR=$(get_val syntax_error_clear_ordered)
SYNTAX_RET=$(get_val syntax_error_typed_return)
SYNTAX_BUG=$(get_val syntax_error_generic_bug)
if [ "$SYNTAX_CLEAR" = "True" ] && [ "$SYNTAX_RET" = "True" ] && [ "$SYNTAX_BUG" != "True" ]; then
  echo "PASS: createSyntaxErrorInstance catch clears exception and returns SyntaxError"
  add_score 0.15 behavioral
elif [ "$SYNTAX_CLEAR" = "True" ]; then
  echo "PARTIAL: createSyntaxErrorInstance catch clears exception but wrong return type"
  add_score 0.07 behavioral
else
  echo "FAIL: createSyntaxErrorInstance catch does not clear pending exception"
fi

# ── Check 4 (0.15): createRangeErrorInstance catch clears + returns RangeError ──
# [pr_diff] (0.15): catch must clear exception before return AND return a RangeErrorInstance
RANGE_CLEAR=$(get_val range_error_clear_ordered)
RANGE_RET=$(get_val range_error_typed_return)
RANGE_BUG=$(get_val range_error_generic_bug)
if [ "$RANGE_CLEAR" = "True" ] && [ "$RANGE_RET" = "True" ] && [ "$RANGE_BUG" != "True" ]; then
  echo "PASS: createRangeErrorInstance catch clears exception and returns RangeError"
  add_score 0.15 behavioral
elif [ "$RANGE_CLEAR" = "True" ]; then
  echo "PARTIAL: createRangeErrorInstance catch clears exception but wrong return type"
  add_score 0.07 behavioral
else
  echo "FAIL: createRangeErrorInstance catch does not clear pending exception"
fi

# ── Check 5 (0.05): Anti-stub — file not gutted ──
# [pr_diff] (0.05): File must retain substantial content
LINE_COUNT=$(get_val line_count)
if [ "$LINE_COUNT" -gt 200 ] 2>/dev/null; then
  echo "PASS: File has $LINE_COUNT lines (not stubbed)"
  add_score 0.05 regression
else
  echo "FAIL: File appears stubbed ($LINE_COUNT lines)"
fi

# ── Check 6 (0.05): createDOMExceptionInstance NOT modified ──
# [pr_diff] (0.05): createDOMExceptionInstance uses try propagation, should NOT gain clearExceptionExceptTermination
DOM_CLEAN=$(get_val dom_exception_clean)
if [ "$DOM_CLEAN" = "True" ]; then
  echo "PASS: createDOMExceptionInstance correctly unchanged"
  add_score 0.05 regression
else
  echo "FAIL: createDOMExceptionInstance incorrectly modified"
fi

# ── Check 7 (0.10): All 4 functions have clear calls (regression count check, gated) ──
# [pr_diff] (0.10): Base has 0 clearExceptionExceptTermination calls in these 4 functions; fix adds 4
if [ "$GATE_PASSED" = "true" ]; then
  TARGET_COUNT=$(get_val target_clear_count)
  if [ "$TARGET_COUNT" -ge 4 ] 2>/dev/null; then
    echo "PASS: All 4 target functions have clearExceptionExceptTermination ($TARGET_COUNT found)"
    add_score 0.10 regression
  elif [ "$TARGET_COUNT" -ge 2 ] 2>/dev/null; then
    echo "PARTIAL: Some target functions fixed ($TARGET_COUNT of 4)"
    add_score 0.05 regression
  else
    echo "FAIL: Too few clearExceptionExceptTermination calls in target functions ($TARGET_COUNT)"
  fi
else
  echo "SKIP: Check 7 gated behind primary behavioral checks"
fi

# ── Write results ──
write_results

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
