#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/js/dataframe/shared/utils/utils.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_null]=0.30
WEIGHTS[behavioral_undef]=0.20
WEIGHTS[regression]=0.15
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15

for key in behavioral_null behavioral_undef regression structural antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: File exists ----------
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: target file exists"

# ---------- PRIMARY 1 (30%): Behavioral - null values preserved for number type ----------
# Extract and run cast_value_to_type with null input via node
node --input-type=module << 'NODEEOF'
import { readFileSync } from "fs";

const source = readFileSync("/workspace/gradio/js/dataframe/shared/utils/utils.ts", "utf8");

// Extract the cast_value_to_type function body
const funcMatch = source.match(/export\s+function\s+cast_value_to_type\s*\([^)]*\)[^{]*\{([\s\S]*?)^\}/m);
if (!funcMatch) {
    console.log("BEHAVIORAL_NULL FAIL: could not extract cast_value_to_type function");
    process.exit(1);
}

// Build a standalone function from the extracted source
const funcBody = funcMatch[1];
const testFunc = new Function("v", "t", funcBody);

// Test: null with "number" type should return null, not 0
const result = testFunc(null, "number");
if (result === null) {
    console.log("BEHAVIORAL_NULL PASS: cast_value_to_type(null, 'number') returns null");
    process.exit(0);
} else {
    console.log(`BEHAVIORAL_NULL FAIL: cast_value_to_type(null, 'number') returned ${JSON.stringify(result)}, expected null`);
    process.exit(1);
}
NODEEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_null]=1
    echo "TEST behavioral_null: PASS"
else
    echo "TEST behavioral_null: FAIL"
fi

# ---------- PRIMARY 2 (20%): Behavioral - undefined values preserved ----------
node --input-type=module << 'NODEEOF'
import { readFileSync } from "fs";

const source = readFileSync("/workspace/gradio/js/dataframe/shared/utils/utils.ts", "utf8");

const funcMatch = source.match(/export\s+function\s+cast_value_to_type\s*\([^)]*\)[^{]*\{([\s\S]*?)^\}/m);
if (!funcMatch) {
    console.log("BEHAVIORAL_UNDEF FAIL: could not extract function");
    process.exit(1);
}

const funcBody = funcMatch[1];
const testFunc = new Function("v", "t", funcBody);

// Test null/undefined across all types
const types = ["number", "bool", "date", "str"];
let allPass = true;

for (const t of types) {
    const nullResult = testFunc(null, t);
    if (nullResult !== null) {
        console.log(`  FAIL: cast_value_to_type(null, '${t}') returned ${JSON.stringify(nullResult)}`);
        allPass = false;
    }
    const undefResult = testFunc(undefined, t);
    if (undefResult !== undefined) {
        console.log(`  FAIL: cast_value_to_type(undefined, '${t}') returned ${JSON.stringify(undefResult)}`);
        allPass = false;
    }
}

if (allPass) {
    console.log("BEHAVIORAL_UNDEF PASS: null/undefined preserved for all types");
    process.exit(0);
} else {
    console.log("BEHAVIORAL_UNDEF FAIL");
    process.exit(1);
}
NODEEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_undef]=1
    echo "TEST behavioral_undef: PASS"
else
    echo "TEST behavioral_undef: FAIL"
fi

# ---------- PRIMARY 3 (15%): Regression - normal values still cast correctly ----------
node --input-type=module << 'NODEEOF'
import { readFileSync } from "fs";

const source = readFileSync("/workspace/gradio/js/dataframe/shared/utils/utils.ts", "utf8");

const funcMatch = source.match(/export\s+function\s+cast_value_to_type\s*\([^)]*\)[^{]*\{([\s\S]*?)^\}/m);
if (!funcMatch) {
    console.log("REGRESSION FAIL: could not extract function");
    process.exit(1);
}

const funcBody = funcMatch[1];
const testFunc = new Function("v", "t", funcBody);

let allPass = true;

// Number casting
if (testFunc("42", "number") !== 42) { console.log("FAIL: '42' -> number"); allPass = false; }
if (testFunc(3.14, "number") !== 3.14) { console.log("FAIL: 3.14 -> number"); allPass = false; }

// Bool casting
if (testFunc("true", "bool") !== true) { console.log("FAIL: 'true' -> bool"); allPass = false; }
if (testFunc("false", "bool") !== false) { console.log("FAIL: 'false' -> bool"); allPass = false; }

// String stays as-is
if (testFunc("hello", "str") !== "hello") { console.log("FAIL: 'hello' -> str"); allPass = false; }

if (allPass) {
    console.log("REGRESSION PASS: normal values cast correctly");
    process.exit(0);
} else {
    console.log("REGRESSION FAIL");
    process.exit(1);
}
NODEEOF
if [ $? -eq 0 ]; then
    RESULTS[regression]=1
    echo "TEST regression: PASS"
else
    echo "TEST regression: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - null/undefined guard exists ----------
node --input-type=module << 'NODEEOF'
import { readFileSync } from "fs";

const source = readFileSync("/workspace/gradio/js/dataframe/shared/utils/utils.ts", "utf8");

const funcMatch = source.match(/export\s+function\s+cast_value_to_type\s*\([^)]*\)[^{]*\{([\s\S]*?)^\}/m);
if (!funcMatch) {
    console.log("STRUCTURAL FAIL: could not extract function");
    process.exit(1);
}

const funcBody = funcMatch[1];

// Check that there is a null/undefined guard before the type coercion
const hasNullCheck = /null/.test(funcBody) && /undefined/.test(funcBody);
const hasEarlyReturn = /return\s+v/.test(funcBody);

// The null/undefined check should appear before Number() coercion
const nullCheckPos = funcBody.search(/null|undefined/);
const numberCoercionPos = funcBody.search(/Number\s*\(/);

if (hasNullCheck && hasEarlyReturn && nullCheckPos < numberCoercionPos) {
    console.log("STRUCTURAL PASS: null/undefined guard present before type coercion");
    process.exit(0);
} else {
    console.log("STRUCTURAL FAIL: missing proper null/undefined guard before coercion");
    process.exit(1);
}
NODEEOF
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- Anti-stub check (15%) ----------
if [ -f "$TARGET" ]; then
    LINE_COUNT=$(wc -l < "$TARGET")
    HAS_EXPORT=$(grep -c "export function cast_value_to_type" "$TARGET" || true)
    HAS_NUMBER=$(grep -c "Number" "$TARGET" || true)
    if [ "$LINE_COUNT" -gt 20 ] && [ "$HAS_EXPORT" -ge 1 ] && [ "$HAS_NUMBER" -ge 1 ]; then
        RESULTS[antistub]=1
        echo "TEST antistub: PASS"
    else
        echo "TEST antistub: FAIL"
    fi
else
    echo "TEST antistub: FAIL (file missing)"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_null': ${WEIGHTS[behavioral_null]}, 'behavioral_undef': ${WEIGHTS[behavioral_undef]}, 'regression': ${WEIGHTS[regression]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_null': ${RESULTS[behavioral_null]}, 'behavioral_undef': ${RESULTS[behavioral_undef]}, 'regression': ${RESULTS[regression]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_null  (${WEIGHTS[behavioral_null]}): ${RESULTS[behavioral_null]}"
echo "  behavioral_undef (${WEIGHTS[behavioral_undef]}): ${RESULTS[behavioral_undef]}"
echo "  regression       (${WEIGHTS[regression]}): ${RESULTS[regression]}"
echo "  structural       (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub         (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
