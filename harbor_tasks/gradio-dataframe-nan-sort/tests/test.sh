#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/js/dataframe/shared/utils/utils.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_null]=0.35
WEIGHTS[behavioral_undef]=0.25
WEIGHTS[regression]=0.20
WEIGHTS[antistub]=0.20

for key in behavioral_null behavioral_undef regression antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: File exists ----------
if [ ! -f "$TARGET" ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- BEHAVIORAL: Extract and test the function ----------
# We extract the function body and test it behaviorally by executing it
# This is the most reliable way to test without GPU/service dependencies

# Create a test harness that extracts and wraps the function
node --input-type=module << 'NODECODE'
import { readFileSync } from "fs";

const source = readFileSync("/workspace/gradio/js/dataframe/shared/utils/utils.ts", "utf8");

// Extract just the cast_value_to_type function
const funcMatch = source.match(/export\s+function\s+cast_value_to_type\s*\([^)]*\)[^{]*\{([\s\S]*?)^\}/m);
if (!funcMatch) {
    console.log("EXTRACT_FAIL");
    process.exit(1);
}

const funcBody = funcMatch[1];

// Create testable function
const testFn = new Function("v", "t", funcBody);

// Test 1: null preservation (the core bug)
const nullResult = testFn(null, "number");
if (nullResult !== null) {
    console.log(`NULL_FAIL: expected null, got ${JSON.stringify(nullResult)}`);
    process.exit(1);
}

// Test 2: undefined preservation
const undefResult = testFn(undefined, "number");
if (undefResult !== undefined) {
    console.log(`UNDEF_FAIL: expected undefined, got ${JSON.stringify(undefResult)}`);
    process.exit(1);
}

// Test 3: All types preserve null/undefined
const types = ["number", "bool", "date", "str", "markdown", "html", "image"];
for (const t of types) {
    if (testFn(null, t) !== null) {
        console.log(`NULL_TYPE_FAIL: type ${t}`);
        process.exit(1);
    }
    if (testFn(undefined, t) !== undefined) {
        console.log(`UNDEF_TYPE_FAIL: type ${t}`);
        process.exit(1);
    }
}

// Test 4: Regression - normal values still work
if (testFn("42", "number") !== 42) {
    console.log(`REGRESSION_NUMBER_FAIL: ${JSON.stringify(testFn("42", "number"))}`);
    process.exit(1);
}
if (testFn(3.14, "number") !== 3.14) {
    console.log(`REGRESSION_FLOAT_FAIL`);
    process.exit(1);
}
if (testFn("true", "bool") !== true) {
    console.log(`REGRESSION_BOOL_TRUE_FAIL`);
    process.exit(1);
}
if (testFn("false", "bool") !== false) {
    console.log(`REGRESSION_BOOL_FALSE_FAIL`);
    process.exit(1);
}
if (testFn("hello", "str") !== "hello") {
    console.log(`REGRESSION_STR_FAIL`);
    process.exit(1);
}

console.log("ALL_PASS");
process.exit(0);
NODECODE

TEST_EXIT=$?
if [ $TEST_EXIT -eq 0 ]; then
    # All behavioral tests passed
    RESULTS[behavioral_null]=1
    RESULTS[behavioral_undef]=1
    RESULTS[regression]=1
    echo "TEST behavioral: PASS (null, undef, regression)"
else
    # Need to determine which specific tests failed
    # Re-run individual checks for scoring granularity

    # Check just null
    node --input-type=module << 'NODECODE'
import { readFileSync } from "fs";
const source = readFileSync("/workspace/gradio/js/dataframe/shared/utils/utils.ts", "utf8");
const funcMatch = source.match(/export\s+function\s+cast_value_to_type\s*\([^)]*\)[^{]*\{([\s\S]*?)^\}/m);
if (!funcMatch) { console.log("EXTRACT_FAIL"); process.exit(1); }
const testFn = new Function("v", "t", funcMatch[1]);
const r = testFn(null, "number");
console.log(r === null ? "NULL_PASS" : `NULL_FAIL:${JSON.stringify(r)}`);
process.exit(r === null ? 0 : 1);
NODECODE
    [ $? -eq 0 ] && RESULTS[behavioral_null]=1

    # Check undef
    node --input-type=module << 'NODECODE'
import { readFileSync } from "fs";
const source = readFileSync("/workspace/gradio/js/dataframe/shared/utils/utils.ts", "utf8");
const funcMatch = source.match(/export\s+function\s+cast_value_to_type\s*\([^)]*\)[^{]*\{([\s\S]*?)^\}/m);
if (!funcMatch) { console.log("EXTRACT_FAIL"); process.exit(1); }
const testFn = new Function("v", "t", funcMatch[1]);
const types = ["number", "bool", "date", "str"];
let allPass = true;
for (const t of types) {
    if (testFn(null, t) !== null) allPass = false;
    if (testFn(undefined, t) !== undefined) allPass = false;
}
console.log(allPass ? "UNDEF_PASS" : "UNDEF_FAIL");
process.exit(allPass ? 0 : 1);
NODECODE
    [ $? -eq 0 ] && RESULTS[behavioral_undef]=1

    # Check regression
    node --input-type=module << 'NODECODE'
import { readFileSync } from "fs";
const source = readFileSync("/workspace/gradio/js/dataframe/shared/utils/utils.ts", "utf8");
const funcMatch = source.match(/export\s+function\s+cast_value_to_type\s*\([^)]*\)[^{]*\{([\s\S]*?)^\}/m);
if (!funcMatch) { console.log("EXTRACT_FAIL"); process.exit(1); }
const testFn = new Function("v", "t", funcMatch[1]);
let pass = true;
if (testFn("42", "number") !== 42) pass = false;
if (testFn("true", "bool") !== true) pass = false;
if (testFn("false", "bool") !== false) pass = false;
if (testFn("hello", "str") !== "hello") pass = false;
console.log(pass ? "REGRESSION_PASS" : "REGRESSION_FAIL");
process.exit(pass ? 0 : 1);
NODECODE
    [ $? -eq 0 ] && RESULTS[regression]=1
fi

# ---------- Anti-stub check (20%) ----------
# Gate: must pass at least one behavioral test to be eligible for antistub
if [ ${RESULTS[behavioral_null]} -eq 1 ] || [ ${RESULTS[behavioral_undef]} -eq 1 ]; then
    LINE_COUNT=$(wc -l < "$TARGET")
    HAS_EXPORT=$(grep -c "export function cast_value_to_type" "$TARGET" || echo 0)
    HAS_LOGIC=$(grep -cE "(Number|Boolean|String|Date|isNaN)" "$TARGET" || echo 0)

    if [ "$LINE_COUNT" -gt 15 ] && [ "$HAS_EXPORT" -ge 1 ] && [ "$HAS_LOGIC" -ge 2 ]; then
        RESULTS[antistub]=1
        echo "TEST antistub: PASS"
    else
        echo "TEST antistub: FAIL"
    fi
else
    echo "TEST antistub: SKIP (behavioral tests failed)"
    RESULTS[antistub]=0
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_null': ${WEIGHTS[behavioral_null]}, 'behavioral_undef': ${WEIGHTS[behavioral_undef]}, 'regression': ${WEIGHTS[regression]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_null': ${RESULTS[behavioral_null]}, 'behavioral_undef': ${RESULTS[behavioral_undef]}, 'regression': ${RESULTS[regression]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_null  (${WEIGHTS[behavioral_null]}): ${RESULTS[behavioral_null]}"
echo "  behavioral_undef (${WEIGHTS[behavioral_undef]}): ${RESULTS[behavioral_undef]}"
echo "  regression       (${WEIGHTS[regression]}): ${RESULTS[regression]}"
echo "  antistub         (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
