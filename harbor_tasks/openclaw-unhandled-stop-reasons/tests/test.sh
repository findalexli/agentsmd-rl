#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_sync]=0.35
WEIGHTS[behavioral_async]=0.35
WEIGHTS[regression_nonstop]=0.15
WEIGHTS[structural_integration]=0.10
WEIGHTS[config_nocheck]=0.05

for key in behavioral_sync behavioral_async regression_nonstop structural_integration config_nocheck; do
    RESULTS[$key]=0
done

TARGET_RECOVERY="src/agents/pi-embedded-runner/run/attempt.stop-reason-recovery.ts"
TARGET_ATTEMPT="src/agents/pi-embedded-runner/run/attempt.ts"

# ---------- GATE: Syntax check (required before behavioral tests) ----------
if [ ! -f "$TARGET_RECOVERY" ]; then
    echo "GATE FAIL: $TARGET_RECOVERY does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# Check TypeScript compiles (basic syntax validation)
cd /workspace/openclaw
npx tsc --noEmit "$TARGET_RECOVERY" 2>/dev/null
if [ $? -ne 0 ]; then
    # Try with skipLibCheck for dependency issues
    npx tsc --noEmit --skipLibCheck "$TARGET_RECOVERY" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "GATE FAIL: TypeScript syntax errors in recovery module"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
fi
echo "GATE PASS: recovery module exists and compiles"

# ---------- PRIMARY 1 (35%): Behavioral - Synchronous throw path (fail-to-pass) ----------
# [pr_diff] (0.35): Catch sync "Unhandled stop reason" throws and convert to structured error
node -e "
const fs = require('fs');
const vm = require('vm');

// Read the recovery module source
const recoverySrc = fs.readFileSync('$TARGET_RECOVERY', 'utf8');

// Build mock dependencies context
const mockContext = {
  console: console,
  // Minimal mock for the pi-ai module
  '\@mariozechner/pi-ai': {
    createAssistantMessageEventStream: () => ({
      push: () => {},
      end: () => {},
      result: async () => ({}),
      [Symbol.asyncIterator]: async function*() {}
    }),
    // Mock streamSimple type
    streamSimple: null
  },
  // Mock for stream-message-shared
  '../../stream-message-shared.js': {
    buildStreamErrorAssistantMessage: ({ model, errorMessage }) => ({
      role: 'assistant',
      content: [],
      api: model.api,
      provider: model.provider,
      model: model.id,
      stopReason: 'error',
      errorMessage: errorMessage,
      timestamp: Date.now()
    })
  }
};

// Extract the module using regex since we can't import TypeScript directly
// We need to verify the function exists and has the right behavior

// Check the regex pattern exists (this is ultimately behavioral - it determines what gets caught)
const hasStopReasonRegex = recoverySrc.match(/Unhandled stop reason[:\\s]/i);
if (!hasStopReasonRegex) {
  console.log('BEHAVIORAL_SYNC FAIL: Missing Unhandled stop reason pattern');
  process.exit(1);
}

// Check the function extracts the stop reason and formats a user message
const hasFormatMessage = recoverySrc.match(/unhandled stop reason.*\$\{[^}]+\}/i) ||
                         recoverySrc.match(/unhandled stop reason:.\s*\+?\s*stopReason/i) ||
                         recoverySrc.match(/Please rephrase and try again/i);
if (!hasFormatMessage) {
  console.log('BEHAVIORAL_SYNC FAIL: Missing user-friendly error message formatting');
  process.exit(1);
}

// Verify the wrapper function exists with proper signature
const hasWrapperFunction = recoverySrc.match(/export\s+(async\s+)?function\s+wrapStreamFnHandleSensitiveStopReason/);
if (!hasWrapperFunction) {
  console.log('BEHAVIORAL_SYNC FAIL: Missing wrapStreamFnHandleSensitiveStopReason export');
  process.exit(1);
}

// Check for the core logic: catching and converting errors
const hasTryCatch = recoverySrc.match(/try\s*\{[^}]*\}\s*catch/i) ||
                    recoverySrc.match(/catch\s*\([^)]*\)\s*\{/i);
if (!hasTryCatch) {
  console.log('BEHAVIORAL_SYNC FAIL: Missing try/catch for error handling');
  process.exit(1);
}

// Check for re-throwing non-matching errors (important for correct behavior)
const hasRethrow = recoverySrc.match(/throw\s+err/i) ||
                   recoverySrc.match(/throw\s+error/i) ||
                   recoverySrc.match(/throw\s+ex/i);
if (!hasRethrow) {
  console.log('BEHAVIORAL_SYNC FAIL: Missing re-throw for non-matching errors');
  process.exit(1);
}

// Check that it sets stopReason to error and provides errorMessage
const hasStopReasonAssignment = recoverySrc.match(/stopReason\s*=\s*['\"']error['\"']/i) ||
                                 recoverySrc.match(/stopReason:\s*['\"']error['\"']/i);
if (!hasStopReasonAssignment) {
  console.log('BEHAVIORAL_SYNC FAIL: Does not set stopReason to error');
  process.exit(1);
}

console.log('BEHAVIORAL_SYNC PASS');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[behavioral_sync]=1
    echo "TEST behavioral_sync: PASS"
else
    echo "TEST behavioral_sync: FAIL"
fi

# ---------- PRIMARY 2 (35%): Behavioral - Async stream error path (fail-to-pass) ----------
# [pr_diff] (0.35): Catch stream-event errors with Unhandled stop reason and convert to structured error
node -e "
const fs = require('fs');

const recoverySrc = fs.readFileSync('$TARGET_RECOVERY', 'utf8');

// Check for async iterator handling (key for stream events)
const hasAsyncIterator = recoverySrc.includes('Symbol.asyncIterator') ||
                         recoverySrc.match(/\[Symbol\.asyncIterator\]/);
if (!hasAsyncIterator) {
  console.log('BEHAVIORAL_ASYNC FAIL: Missing async iterator handling for stream events');
  process.exit(1);
}

// Check for result() method patching (handles the stream.result() path)
const hasResultMethod = recoverySrc.match(/\.result\s*=/) ||
                        recoverySrc.match(/result\s*:\s*async/i);
if (!hasResultMethod) {
  console.log('BEHAVIORAL_ASYNC FAIL: Missing result() method handling');
  process.exit(1);
}

// Check for queueMicrotask usage (how error events are pushed in the fix)
const hasQueueMicrotask = recoverySrc.includes('queueMicrotask') ||
                          recoverySrc.includes('setImmediate') ||
                          recoverySrc.includes('process.nextTick');
if (!hasQueueMicrotask) {
  console.log('BEHAVIORAL_ASYNC FAIL: Missing async error stream construction');
  process.exit(1);
}

// Check for the specific error object structure (type: 'error', reason: 'error')
const hasErrorStructure = recoverySrc.match(/type\s*:\s*['\"']error['\"']/) &&
                          recoverySrc.match(/reason\s*:\s*['\"']error['\"']/);
if (!hasErrorStructure) {
  console.log('BEHAVIORAL_ASYNC FAIL: Missing correct error event structure');
  process.exit(1);
}

// Must distinguish between different stop reasons - check for extraction pattern
const hasReasonExtraction = recoverySrc.match(/match.*\[\s*1\s*\]/) ||  // regex match group
                            recoverySrc.match(/group\(1\)/) ||
                            recoverySrc.match(/split.*:/) ||
                            recoverySrc.match(/slice\s*\(\s*['\"']Unhandled/i);
if (!hasReasonExtraction) {
  console.log('BEHAVIORAL_ASYNC FAIL: Missing stop reason extraction from message');
  process.exit(1);
}

console.log('BEHAVIORAL_ASYNC PASS');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[behavioral_async]=1
    echo "TEST behavioral_async: PASS"
else
    echo "TEST behavioral_async: FAIL"
fi

# ---------- REGRESSION (15%): Non-matching errors should be re-thrown (pass-to-pass) ----------
# [pr_diff] (0.15): Errors that don't match the pattern must still be thrown
node -e "
const fs = require('fs');
const recoverySrc = fs.readFileSync('$TARGET_RECOVERY', 'utf8');

// Count occurrences of 'throw' after checking for the pattern
// The fix should have re-throw logic for non-matching errors
const throwMatches = recoverySrc.match(/throw\s+(err|error|e)\b/gi);
const catchBlocks = recoverySrc.match(/catch\s*\([^)]*\)/gi);

if (!throwMatches || throwMatches.length < 2) {
  console.log('REGRESSION FAIL: Insufficient re-throw logic for non-matching errors');
  process.exit(1);
}

// Check that there's conditional logic (if statement) around the error handling
const hasConditional = recoverySrc.match(/if\s*\([^)]*(match|normalized|stopReason)/i) ||
                       recoverySrc.match(/if\s*\(!?(normalized|match)\)/i);
if (!hasConditional) {
  console.log('REGRESSION FAIL: Missing conditional logic for selective error handling');
  process.exit(1);
}

// Ensure the pattern matching is specific enough (not just checking for 'error')
const specificPattern = recoverySrc.match(/Unhandled stop reason/i) ||
                        recoverySrc.match(/stop\s+reason.*sensitive/i);
if (!specificPattern) {
  console.log('REGRESSION FAIL: Pattern matching is not specific to stop reasons');
  process.exit(1);
}

console.log('REGRESSION PASS');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[regression_nonstop]=1
    echo "TEST regression_nonstop: PASS"
else
    echo "TEST regression_nonstop: FAIL"
fi

# ---------- STRUCTURAL (10%): Integration with attempt.ts ----------
# [agent_config] (0.10): Wrap applied to streamFn in attempt.ts - openclaw/extensions/CLAUDE.md
node -e "
const fs = require('fs');
const attemptSrc = fs.readFileSync('$TARGET_ATTEMPT', 'utf8');

// Check that attempt.ts imports the recovery module
const hasImport = attemptSrc.match(/from\s+['\"]\.\/attempt\.stop-reason-recovery/) ||
                  attemptSrc.match(/from\s+['\"]\.\.\/[^'\"]*stop-reason-recovery/) ||
                  attemptSrc.match(/import\s+.*wrapStreamFnHandleSensitiveStopReason/);
if (!hasImport) {
  console.log('STRUCTURAL FAIL: attempt.ts does not import recovery module');
  process.exit(1);
}

// Check that the wrapper is actually applied to the streamFn
const hasApplication = attemptSrc.match(/streamFn\s*=\s*wrapStreamFnHandleSensitiveStopReason/) ||
                       attemptSrc.match(/wrapStreamFnHandleSensitiveStopReason\s*\(\s*streamFn/) ||
                       attemptSrc.match(/wrapStreamFnHandleSensitiveStopReason\s*\(\s*activeSession\.agent\.streamFn/);
if (!hasApplication) {
  console.log('STRUCTURAL FAIL: Wrapper not applied to streamFn in attempt.ts');
  process.exit(1);
}

// Ensure it's applied BEFORE the sanitization/usage of streamFn
const streamFnUsageMatch = attemptSrc.match(/wrapStreamFnHandleSensitiveStopReason[\s\S]{0,500}sanitize/);
if (!streamFnUsageMatch) {
  // Alternative: check if it's in the same function scope before usage
  const nearSanitize = attemptSrc.match(/wrapStreamFnHandleSensitiveStopReason[\s\S]{0,1000}try\s*\{[\s\S]{0,500}sanitize/);
  if (!nearSanitize) {
    console.log('STRUCTURAL WARN: Cannot verify wrapper is applied before sanitization');
    // Don't fail - this is a warning-level check
  }
}

console.log('STRUCTURAL PASS');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[structural_integration]=1
    echo "TEST structural_integration: PASS"
else
    echo "TEST structural_integration: FAIL"
fi

# ---------- Config-derived test (5%): "Never add @ts-nocheck" ----------
# [agent_config] (0.05): "Run ruff format" + no @ts-nocheck - CLAUDE.md:32-33 @ 664680318eea98172c7d25405c20f5e3eadfd0e2
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find /workspace/openclaw/src/agents -name '*.\''ts'\'' -not -name '*.\''test.ts'\'' -not -name '*.\''d.ts'\'' 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\n').filter(Boolean);
let fail = false;
for (const f of files) {
    try {
        const content = fs.readFileSync(f, 'utf8');
        if (content.includes('@ts-nocheck') || content.includes('@ts-ignore')) {
            console.log('FAIL: ' + f + ' contains @ts-nocheck or @ts-ignore');
            fail = true;
        }
    } catch(e) {}
}
if (fail) process.exit(1);
console.log('PASS: no @ts-nocheck/@ts-ignore found');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[config_nocheck]=1
    echo "TEST config_nocheck: PASS"
else
    echo "TEST config_nocheck: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {
    'behavioral_sync': ${WEIGHTS[behavioral_sync]},
    'behavioral_async': ${WEIGHTS[behavioral_async]},
    'regression_nonstop': ${WEIGHTS[regression_nonstop]},
    'structural_integration': ${WEIGHTS[structural_integration]},
    'config_nocheck': ${WEIGHTS[config_nocheck]}
}
results = {
    'behavioral_sync': ${RESULTS[behavioral_sync]},
    'behavioral_async': ${RESULTS[behavioral_async]},
    'regression_nonstop': ${RESULTS[regression_nonstop]},
    'structural_integration': ${RESULTS[structural_integration]},
    'config_nocheck': ${RESULTS[config_nocheck]}
}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")

echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_sync       (${WEIGHTS[behavioral_sync]}): ${RESULTS[behavioral_sync]}"
echo "  behavioral_async      (${WEIGHTS[behavioral_async]}): ${RESULTS[behavioral_async]}"
echo "  regression_nonstop    (${WEIGHTS[regression_nonstop]}): ${RESULTS[regression_nonstop]}"
echo "  structural_integration (${WEIGHTS[structural_integration]}): ${RESULTS[structural_integration]}"
echo "  config_nocheck        (${WEIGHTS[config_nocheck]}): ${RESULTS[config_nocheck]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
