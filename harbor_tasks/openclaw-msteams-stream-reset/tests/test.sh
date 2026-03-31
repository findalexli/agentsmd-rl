#!/usr/bin/env bash
set +e

TARGET="/workspace/openclaw/extensions/msteams/src/reply-stream-controller.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

for key in behavioral_f2p behavioral2_f2p regression config_boundary; do
    declare RESULTS_$key=0
done

if [ ! -f "$TARGET" ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi

# =============================================================================
# FAIL-TO-PASS 1 (35%): streamReceivedTokens resets after suppression
# Tests the core bug: second text segment should use fallback delivery
# =============================================================================
node --input-type=module << 'NODEOF' && RESULTS_behavioral_f2p=1 || true
import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { execSync } from 'child_process';

const targetPath = '/workspace/openclaw/extensions/msteams/src/reply-stream-controller.ts';

// Create a test harness that mocks the dependencies
const testHarness = `
import type { ReplyPayload } from "../runtime-api.js";

// Mock stream class
class MockTeamsHttpStream {
  private content = "";
  private finalized = false;

  sendInformativeUpdate(text: string) { return Promise.resolve(); }
  update(text: string) { this.content += text; }
  finalize() {
    this.finalized = true;
    return Promise.resolve();
  }
  get hasContent() { return this.content.length > 0; }
  get isFinalized() { return this.finalized; }
}

// Load the actual implementation
${readFileSync(targetPath, 'utf8').replace(/import .* from ['"]\.\.\/.*['"];?\n/g, '').replace(/import .* from ['"]\.\.\/\.\.\/.*['"];?\n/g, '').replace(/import .* from ['"]\.\/.+['"];?\n/g, '')}

// Test the fix
async function test() {
  const controller = createTeamsReplyStreamController({
    conversationType: "personal",
    context: { sendActivity: () => Promise.resolve() } as any,
    feedbackLoopEnabled: false,
    log: { debug: console.log },
  });

  // Simulate tool-call interruption scenario:
  // 1. First text segment arrives
  controller.onPartialReply({ text: "First part" });

  // 2. preparePayload is called (this should suppress and trigger finalize)
  const firstPayload = { text: "First part" };
  const result1 = controller.preparePayload(firstPayload);

  // 3. Second text segment arrives (after tool calls)
  controller.onPartialReply({ text: "After tool" });

  // 4. preparePayload for second segment should NOT suppress (fallback delivery)
  const secondPayload = { text: "After tool" };
  const result2 = controller.preparePayload(secondPayload);

  // Verify: First segment suppressed (result is undefined), second uses fallback
  if (result1 !== undefined) {
    console.log("F2P FAIL: First segment should be suppressed when stream has content");
    process.exit(1);
  }

  if (result2 === undefined) {
    console.log("F2P FAIL: Second segment should use fallback delivery (bug not fixed)");
    process.exit(1);
  }

  if (result2.text !== "After tool") {
    console.log("F2P FAIL: Second segment payload corrupted");
    process.exit(1);
  }

  console.log("F2P PASS: streamReceivedTokens reset enables fallback for subsequent segments");
}

test().catch(e => { console.error(e); process.exit(1); });
`;

mkdirSync('/tmp/test-f2p', { recursive: true });
writeFileSync('/tmp/test-f2p/test.ts', testHarness);

try {
  execSync('cd /workspace/openclaw && npx tsx /tmp/test-f2p/test.ts 2>&1', {
    encoding: 'utf8',
    timeout: 30000,
    stdio: ['pipe', 'pipe', 'pipe']
  });
  process.exit(0);
} catch (e) {
  console.log("F2P FAIL: " + (e.stdout || e.message));
  process.exit(1);
}
NODEOF
echo "TEST behavioral_f2p: $([ $RESULTS_behavioral_f2p -eq 1 ] && echo PASS || echo FAIL)"

# =============================================================================
# FAIL-TO-PASS 2 (30%): isFinalized guard prevents re-suppression
# =============================================================================
node --input-type=module << 'NODEOF' && RESULTS_behavioral2_f2p=1 || true
import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { execSync } from 'child_process';

const targetPath = '/workspace/openclaw/extensions/msteams/src/reply-stream-controller.ts';

// Check that isFinalized is actually used as a guard condition
const source = readFileSync(targetPath, 'utf8');

// Look for isFinalized check in preparePayload
const preparePayloadMatch = source.match(/preparePayload[^{]*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}/s);
if (!preparePayloadMatch) {
  console.log("F2P2 FAIL: preparePayload method not found");
  process.exit(1);
}

const methodBody = preparePayloadMatch[1];

// Check for isFinalized guard in the early return condition
if (!methodBody.match(/stream\.isFinalized|isFinalized/)) {
  console.log("F2P2 FAIL: isFinalized not used in preparePayload");
  process.exit(1);
}

// Check that finalize() method exists and awaits pendingFinalize
const finalizeMatch = source.match(/finalize\s*\([^)]*\)[^{]*\{([^}]*)\}/s);
if (!finalizeMatch) {
  console.log("F2P2 FAIL: finalize method not found");
  process.exit(1);
}

const finalizeBody = finalizeMatch[1];
if (!finalizeBody.includes('pendingFinalize') && !finalizeBody.includes('finalize()')) {
  console.log("F2P2 FAIL: finalize doesn't handle pending state");
  process.exit(1);
}

// Now test behavioral correctness
const testHarness = `
// Mock stream with isFinalized
class MockStream {
  private content = "";
  private ended = false;
  update(text: string) { this.content += text; }
  finalize() { this.ended = true; return Promise.resolve(); }
  get hasContent() { return this.content.length > 0; }
  get isFinalized() { return this.ended; }
}

${readFileSync(targetPath, 'utf8').replace(/import .* from ['"]\.\.\/.*['"];?\n/g, '').replace(/import .* from ['"]\.\.\/\.\.\/.*['"];?\n/g, '').replace(/import .* from ['"]\.\/.+['"];?\n/g, '')}

async function test() {
  const stream = new MockStream();
  let pendingFinalize: Promise<void> | undefined;

  // Simulate the fixed scenario
  stream.update("content");

  // First call: should suppress and trigger finalize
  if (stream.hasContent && !stream.isFinalized) {
    pendingFinalize = stream.finalize();
  }

  // After finalize, isFinalized should be true
  if (!stream.isFinalized) {
    console.log("F2P2 FAIL: isFinalized not tracking finalization state");
    process.exit(1);
  }

  // Second call with isFinalized=true should NOT suppress
  if (stream.isFinalized) {
    console.log("F2P2 PASS: isFinalized guard prevents re-suppression");
  }
}

test();
`;

mkdirSync('/tmp/test-f2p2', { recursive: true });
writeFileSync('/tmp/test-f2p2/test.ts', testHarness);

try {
  execSync('cd /workspace/openclaw && npx tsx /tmp/test-f2p2/test.ts 2>&1', {
    encoding: 'utf8',
    timeout: 30000
  });
  console.log("F2P2 PASS: isFinalized guard verified");
  process.exit(0);
} catch (e) {
  console.log("F2P2 FAIL: " + (e.stdout || e.message));
  process.exit(1);
}
NODEOF
echo "TEST behavioral2_f2p: $([ $RESULTS_behavioral2_f2p -eq 1 ] && echo PASS || echo FAIL)"

# =============================================================================
# REGRESSION (20%): Existing single-segment streaming still works
# =============================================================================
node --input-type=module << 'NODEOF' && RESULTS_regression=1 || true
import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { execSync } from 'child_process';

const targetPath = '/workspace/openclaw/extensions/msteams/src/reply-stream-controller.ts';

const testHarness = `
class MockStream {
  private content = "";
  private ended = false;
  update(text: string) { this.content += text; }
  finalize() { this.ended = true; return Promise.resolve(); }
  get hasContent() { return this.content.length > 0; }
  get isFinalized() { return this.ended; }
}

${readFileSync(targetPath, 'utf8').replace(/import .* from ['"]\.\.\/.*['"];?\n/g, '').replace(/import .* from ['"]\.\.\/\.\.\/.*['"];?\n/g, '').replace(/import .* from ['"]\.\/.+['"];?\n/g, '')}

async function test() {
  const controller = createTeamsReplyStreamController({
    conversationType: "personal",
    context: { sendActivity: () => Promise.resolve() } as any,
    feedbackLoopEnabled: false,
    log: {},
  });

  // Single segment flow should still work
  await controller.onReplyStart();
  controller.onPartialReply({ text: "Hello single segment" });
  const payload = controller.preparePayload({ text: "Hello single segment" });

  // Should be suppressed (stream has content)
  if (payload !== undefined) {
    console.log("REGRESSION FAIL: Single segment not suppressed correctly");
    process.exit(1);
  }

  await controller.finalize();

  // Non-personal chats (no stream)
  const controller2 = createTeamsReplyStreamController({
    conversationType: "group",
    context: { sendActivity: () => Promise.resolve() } as any,
    feedbackLoopEnabled: false,
    log: {},
  });

  const payload2 = controller2.preparePayload({ text: "Group message" });
  if (payload2 === undefined) {
    console.log("REGRESSION FAIL: Group chat messages incorrectly suppressed");
    process.exit(1);
  }

  // Empty text should pass through
  const controller3 = createTeamsReplyStreamController({
    conversationType: "personal",
    context: { sendActivity: () => Promise.resolve() } as any,
    feedbackLoopEnabled: false,
    log: {},
  });

  const payload3 = controller3.preparePayload({ text: "" });
  if (payload3 === undefined) {
    console.log("REGRESSION FAIL: Empty text incorrectly suppressed");
    process.exit(1);
  }

  console.log("REGRESSION PASS: Existing flows work correctly");
}

test().catch(e => { console.error(e); process.exit(1); });
`;

mkdirSync('/tmp/test-regression', { recursive: true });
writeFileSync('/tmp/test-regression/test.ts', testHarness);

try {
  execSync('cd /workspace/openclaw && npx tsx /tmp/test-regression/test.ts 2>&1', {
    encoding: 'utf8',
    timeout: 30000
  });
  process.exit(0);
} catch (e) {
  console.log("REGRESSION FAIL: " + (e.stdout || e.message));
  process.exit(1);
}
NODEOF
echo "TEST regression: $([ $RESULTS_regression -eq 1 ] && echo PASS || echo FAIL)"

# =============================================================================
# CONFIG-DERIVED (15%): No cross-boundary imports from src/
# [agent_config] CLAUDE.md:16 @ 4752aca926624efdeb62f2f43b606f5090be8903
# =============================================================================
node --input-type=module << 'NODEOF' && RESULTS_config_boundary=1 || true
import { readFileSync } from 'fs';
import { execSync } from 'child_process';

const files = execSync('find /workspace/openclaw/extensions/msteams/src -name "*.ts" -not -name "*.test.ts" -not -name "*.d.ts" 2>/dev/null || true', { encoding: 'utf8' })
  .trim()
  .split('\n')
  .filter(Boolean);

for (const f of files) {
  const content = readFileSync(f, 'utf8');
  const lines = content.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Remove comments before checking
    const codeOnly = line.replace(/\/\/.*$/, '').replace(/\/\*[\s\S]*?\*\//, '');
    if (/^import .* from ['"]\.\.\/\.\.\/\.\.\/src\//.test(codeOnly)) {
      console.log('CONFIG BOUNDARY FAIL: ' + f + ':' + (i + 1) + ' imports core internals');
      process.exit(1);
    }
  }
}
console.log('CONFIG BOUNDARY PASS: No cross-boundary imports');
NODEOF
NODE_EXIT=$?
if [ $NODE_EXIT -eq 0 ]; then RESULTS_config_boundary=1; fi
echo "TEST config_boundary: $([ $RESULTS_config_boundary -eq 1 ] && echo PASS || echo FAIL)"

# =============================================================================
# Calculate score
# =============================================================================
SCORE=$(python3 -c "
weights = {'behavioral_f2p': 0.35, 'behavioral2_f2p': 0.30, 'regression': 0.20, 'config_boundary': 0.15}
results = {'behavioral_f2p': $RESULTS_behavioral_f2p, 'behavioral2_f2p': $RESULTS_behavioral2_f2p, 'regression': $RESULTS_regression, 'config_boundary': $RESULTS_config_boundary}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")

echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
