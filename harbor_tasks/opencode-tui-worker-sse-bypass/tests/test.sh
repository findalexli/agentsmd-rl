#!/usr/bin/env bash
set +e

WORKER="packages/opencode/src/cli/cmd/tui/worker.ts"

# ──────────────────────────────────────────────────────────────
# GATE: file must exist and be non-empty
# ──────────────────────────────────────────────────────────────
# [pr_diff] (gate): TypeScript worker file must exist
if [ ! -s "$WORKER" ]; then
  echo "GATE FAILED: worker.ts is missing or empty"
  echo "0.0" > /logs/verifier/reward.txt
  cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
  exit 0
fi

# ──────────────────────────────────────────────────────────────
# All checks run in a single node script for robustness.
# Comment stripping prevents gaming via comment injection.
# Scope-aware analysis prevents keyword placement outside
# the relevant function body.
# ──────────────────────────────────────────────────────────────
RESULTS=$(node -e '
const fs = require("fs");
const src = fs.readFileSync(process.argv[1], "utf8");

// ── Comment stripper (preserves string literals) ──
function stripComments(code) {
  let out = "", i = 0;
  while (i < code.length) {
    if (code[i] === "/" && code[i+1] === "/") {
      // single-line comment: skip to EOL
      while (i < code.length && code[i] !== "\n") i++;
    } else if (code[i] === "/" && code[i+1] === "*") {
      // multi-line comment: skip to */
      i += 2;
      while (i < code.length - 1 && !(code[i] === "*" && code[i+1] === "/")) i++;
      i += 2;
    } else if (code[i] === "\x27" || code[i] === "\x22" || code[i] === "\x60") {
      // string literal: copy verbatim (including escape sequences)
      const q = code[i];
      out += code[i++];
      while (i < code.length && code[i] !== q) {
        if (code[i] === "\\") { out += code[i++]; }
        if (i < code.length) out += code[i++];
      }
      if (i < code.length) out += code[i++];
    } else {
      out += code[i++];
    }
  }
  return out;
}

const stripped = stripComments(src);

// ── Scope extraction: startEventStream body ──
// Find balanced braces for the arrow/function after "const startEventStream"
function extractFunctionBody(code, marker) {
  const idx = code.indexOf(marker);
  if (idx < 0) return "";
  // Find first { after marker
  let braceStart = code.indexOf("{", idx);
  if (braceStart < 0) return "";
  let depth = 0, i = braceStart;
  while (i < code.length) {
    if (code[i] === "{") depth++;
    else if (code[i] === "}") { depth--; if (depth === 0) return code.substring(braceStart, i + 1); }
    // skip string literals inside body
    else if (code[i] === "\x27" || code[i] === "\x22" || code[i] === "\x60") {
      const q = code[i]; i++;
      while (i < code.length && code[i] !== q) { if (code[i] === "\\") i++; i++; }
    }
    i++;
  }
  return code.substring(braceStart);
}

const streamBody = extractFunctionBody(stripped, "startEventStream");

const checks = {};

// ── FAIL-TO-PASS PROXY: Core change checks (applied to comment-stripped, scoped code) ──

// [pr_diff] (0.25): Bus.subscribeAll or Bus.subscribe used WITHIN startEventStream
// The core fix: events consumed from internal bus, not SSE
checks.bus_in_stream = /Bus\s*\.\s*subscribe(All)?\s*\(/.test(streamBody);

// [pr_diff] (0.15): WorkspaceContext.provide called WITHIN startEventStream
// Required so workspace-scoped event filtering works
checks.workspace_ctx = /WorkspaceContext\s*\.\s*provide\s*\(/.test(streamBody);

// [pr_diff] (0.10): Instance.provide called WITHIN startEventStream
// Required so instance-scoped context is available to bus subscriptions
checks.instance_provide = /Instance\s*\.\s*provide\s*\(/.test(streamBody);

// [pr_diff] (0.05): InstanceDisposed event referenced WITHIN startEventStream
// Handles reconnection when instance is disposed
checks.instance_disposed = /InstanceDisposed/.test(streamBody);

// [pr_diff] (0.10): SSE client fully removed from ENTIRE file (comment-stripped)
// createOpencodeClient must not appear in any executable code
checks.sse_removed = !/createOpencodeClient/.test(stripped);

// [pr_diff] (0.05): SSE sdk.event.subscribe pattern removed from startEventStream
// The old event loop used sdk.event.subscribe — must be gone
checks.sdk_subscribe_removed = !/sdk\s*\.\s*event\s*\.\s*subscribe/.test(streamBody);

// ── PASS-TO-PASS: Existing behavior preserved ──

// [pr_diff] (0.05): RPC exports block contains all required methods
const rpcIdx = stripped.indexOf("export const rpc");
const rpcBlock = rpcIdx >= 0 ? stripped.substring(rpcIdx, rpcIdx + 500) : "";
const rpcMethods = ["fetch", "snapshot", "server", "checkUpgrade", "reload", "shutdown"];
checks.rpc_exports = rpcMethods.every(m => rpcBlock.includes(m));

// [pr_diff] (0.05): GlobalBus event forwarding present in executable code
checks.global_bus = /GlobalBus\s*\.\s*on\s*\(/.test(stripped);

// [pr_diff] (0.05): AbortController + signal cleanup pattern present
checks.abort_cleanup = /new\s+AbortController/.test(stripped) &&
  (/signal\s*\.\s*aborted/.test(stripped) || /signal\s*\.\s*addEventListener/.test(stripped));

// ── ANTI-STUB: startEventStream must have substantial implementation ──

// [static] (0.05): startEventStream body has >= 20 non-empty lines (rejects stubs)
const bodyLines = streamBody.split("\n").filter(l => l.trim().length > 0);
checks.not_stub = bodyLines.length >= 20;

// [static] (0.05): startEventStream contains a Promise or async pattern (core logic)
checks.has_async_logic = /new\s+Promise|async\s|await\s|\.then\s*\(|\.catch\s*\(/.test(streamBody);

console.log(JSON.stringify(checks));
' "$WORKER" 2>&1)

# ──────────────────────────────────────────────────────────────
# Parse results and compute score
# ──────────────────────────────────────────────────────────────
if ! echo "$RESULTS" | node -e "JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'))" 2>/dev/null; then
  echo "ERROR: analysis script failed"
  echo "$RESULTS"
  echo "0.0" > /logs/verifier/reward.txt
  cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true
  exit 0
fi

SCORE=0
TOTAL=0

check() {
  local name="$1" weight="$2" desc="$3"
  TOTAL=$(python3 -c "print($TOTAL + $weight)")
  local val
  val=$(echo "$RESULTS" | node -e "
    const r = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    console.log(r['$name'] ? 'true' : 'false');
  " 2>&1)
  if [ "$val" = "true" ]; then
    echo "PASS ($weight): $desc"
    SCORE=$(python3 -c "print($SCORE + $weight)")
  else
    echo "FAIL ($weight): $desc"
  fi
}

echo "=== FAIL-TO-PASS PROXY (comment-stripped, scope-aware) ==="
# [pr_diff] (0.25): Bus subscription in startEventStream body
check bus_in_stream      0.25 "Bus.subscribe/subscribeAll used within startEventStream"
# [pr_diff] (0.15): WorkspaceContext.provide in startEventStream body
check workspace_ctx      0.15 "WorkspaceContext.provide wraps event subscription"
# [pr_diff] (0.10): Instance.provide in startEventStream body
check instance_provide   0.10 "Instance.provide used within startEventStream"
# [pr_diff] (0.05): InstanceDisposed handling in startEventStream
check instance_disposed  0.05 "InstanceDisposed event handled for reconnection"
# [pr_diff] (0.10): SSE client createOpencodeClient removed
check sse_removed        0.10 "createOpencodeClient removed from executable code"
# [pr_diff] (0.05): Old sdk.event.subscribe pattern removed
check sdk_subscribe_removed 0.05 "sdk.event.subscribe SSE pattern removed"

echo ""
echo "=== PASS-TO-PASS ==="
# [pr_diff] (0.05): RPC exports intact
check rpc_exports        0.05 "All RPC methods still exported"
# [pr_diff] (0.05): GlobalBus forwarding intact
check global_bus         0.05 "GlobalBus event forwarding present"
# [pr_diff] (0.05): AbortController/signal cleanup
check abort_cleanup      0.05 "AbortController + signal cleanup pattern intact"

echo ""
echo "=== ANTI-STUB ==="
# [static] (0.05): Minimum code complexity
check not_stub           0.05 "startEventStream has >= 20 non-empty lines"
# [static] (0.05): Async/Promise pattern present
check has_async_logic    0.05 "startEventStream contains async/Promise logic"

echo ""
# ──────────────────────────────────────────────────────────────
# TOTAL
# ──────────────────────────────────────────────────────────────
REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0)")
echo "Score: $SCORE / $TOTAL = $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt
cp /logs/verifier/reward.txt reward.txt 2>/dev/null || true

# Breakdown for reward.json
echo "$RESULTS" | node -e "
  const fs = require('fs');
  const r = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));
  const b = (k) => r[k] ? 1 : 0;
  const f2p = 0.25*b('bus_in_stream') + 0.15*b('workspace_ctx') + 0.10*b('instance_provide')
            + 0.05*b('instance_disposed') + 0.10*b('sse_removed') + 0.05*b('sdk_subscribe_removed');
  const p2p = 0.05*b('rpc_exports') + 0.05*b('global_bus') + 0.05*b('abort_cleanup');
  const anti = 0.05*b('not_stub') + 0.05*b('has_async_logic');
  const total = f2p + p2p + anti;
  const reward = total > 0 ? Math.round(total * 10000) / 10000 : 0;
  const out = {
    reward: reward,
    behavioral: Math.round(f2p * 10000) / 10000,
    regression: Math.round(p2p * 10000) / 10000,
    structural: Math.round(anti * 10000) / 10000,
  };
  fs.writeFileSync('/logs/verifier/reward.json', JSON.stringify(out));
" 2>/dev/null
cp /logs/verifier/reward.json reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
