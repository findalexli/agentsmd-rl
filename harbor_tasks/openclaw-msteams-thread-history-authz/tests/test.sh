#!/usr/bin/env bash
set +e

REPO="/workspace/openclaw"
HANDLER="$REPO/extensions/msteams/src/monitor-handler/message-handler.ts"
REWARD=0

pass() { REWARD=$(python3 -c "print(round(${REWARD} + ${1}, 4))"); echo "PASS ($1): $2"; }
fail() { echo "FAIL ($1): $2"; }

# ── GATE: Syntax check ──────────────────────────────────────────────
# [pr_diff] (0.00): File must be valid TypeScript (parseable)
if ! node -e "
  const fs = require('fs');
  const code = fs.readFileSync('${HANDLER}', 'utf8');
  try { new Function(code); } catch(e) {
    if (e instanceof SyntaxError && !e.message.includes('import') && !e.message.includes('export') && !e.message.includes('await')) {
      process.exit(1);
    }
  }
" 2>/dev/null; then
  echo "GATE FAIL: message-handler.ts has syntax errors"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
  exit 0
fi
echo "GATE PASS: TypeScript syntax OK"

# ── Behavioral: vitest tests (F2P + P2P) ────────────────────────────
# Two scenarios in one test file:
#   1. F2P: non-allowlisted sender messages excluded from thread context
#   2. P2P: all-allowlisted senders' messages still included
rm -f /tmp/harbor_f2p_pass /tmp/harbor_p2p_pass

cat > "$REPO/extensions/msteams/src/monitor-handler/_harbor_thread_filter.test.ts" <<'VITEST_EOF'
import { describe, expect, it, vi } from "vitest";
import { writeFileSync } from "node:fs";
import type { OpenClawConfig, PluginRuntime, RuntimeEnv } from "../../runtime-api.js";
import type { GraphThreadMessage } from "../graph-thread.js";
import type { MSTeamsMessageHandlerDeps } from "../monitor-handler.js";
import { setMSTeamsRuntime } from "../runtime.js";
import { createMSTeamsMessageHandler } from "./message-handler.js";

const runtimeApiMock = vi.hoisted(() => ({
  dispatchReplyFromConfigWithSettledDispatcher: vi.fn(async (params: { ctxPayload: unknown }) => ({
    queuedFinal: false,
    counts: {},
    capturedCtxPayload: params.ctxPayload,
  })),
}));

const graphThreadMock = vi.hoisted(() => ({
  resolveTeamGroupId: vi.fn(async () => "group-1"),
  fetchChannelMessage: vi.fn<
    (t: string, g: string, c: string, m: string) => Promise<GraphThreadMessage | undefined>
  >(async () => undefined),
  fetchThreadReplies: vi.fn<
    (t: string, g: string, c: string, m: string, l?: number) => Promise<GraphThreadMessage[]>
  >(async () => []),
}));

vi.mock("../../runtime-api.js", async () => {
  const actual = await vi.importActual<typeof import("../../runtime-api.js")>("../../runtime-api.js");
  return {
    ...actual,
    dispatchReplyFromConfigWithSettledDispatcher: runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher,
  };
});

vi.mock("../graph-thread.js", async () => {
  const actual = await vi.importActual<typeof import("../graph-thread.js")>("../graph-thread.js");
  return {
    ...actual,
    resolveTeamGroupId: graphThreadMock.resolveTeamGroupId,
    fetchChannelMessage: graphThreadMock.fetchChannelMessage,
    fetchThreadReplies: graphThreadMock.fetchThreadReplies,
  };
});

vi.mock("../reply-dispatcher.js", () => ({
  createMSTeamsReplyDispatcher: () => ({
    dispatcher: {},
    replyOptions: {},
    markDispatchIdle: vi.fn(),
  }),
}));

describe("harbor: thread history allowlist filtering", () => {
  function makeDeps(cfg: OpenClawConfig) {
    const readAllowFromStore = vi.fn(async () => ["store-allowed-aad"]);
    const upsertPairingRequest = vi.fn(async () => null);
    const recordInboundSession = vi.fn(async () => undefined);
    setMSTeamsRuntime({
      logging: { shouldLogVerbose: () => false },
      system: { enqueueSystemEvent: vi.fn() },
      channel: {
        debounce: { resolveInboundDebounceMs: () => 0 },
        threadHistory: { resolveMaxFetchMessages: () => 25 },
        pairing: { readAllowFromStore, upsertPairingRequest },
        tokenProvider: { getAccessToken: async () => "fake-graph-token" },
        inbound: {
          formatSenderId: (id: string) => id,
          resolveGroupPolicyFields: (c: OpenClawConfig) => ({
            groupPolicy: c.channels?.msteams?.groupPolicy ?? "disabled",
            groupAllowFrom: c.channels?.msteams?.groupAllowFrom ?? [],
            dangerouslyAllowNameMatching: c.channels?.msteams?.dangerouslyAllowNameMatching ?? false,
          }),
        },
        text: { hasControlCommand: () => false },
        routing: {
          resolveAgentRoute: ({ peer }: { peer: { kind: string; id: string } }) => ({
            sessionKey: `msteams:${peer.kind}:${peer.id}`,
            agentId: "default",
            accountId: "default",
          }),
        },
        reply: {
          formatAgentEnvelope: ({ body }: { body: string }) => body,
          finalizeInboundContext: <T extends Record<string, unknown>>(ctx: T) => ctx,
        },
        session: { recordInboundSession },
      },
    } as unknown as PluginRuntime);

    const conversationStore = {
      get: vi.fn(async () => ({
        conversation: { id: "19:channel@thread.tacv2", conversationType: "channel" },
        serviceUrl: "https://smba.trafficmanager.net/teams/",
        bot: { id: "bot-id", name: "Bot" },
      })),
      set: vi.fn(async () => undefined),
    };

    const deps: MSTeamsMessageHandlerDeps = {
      cfg,
      env: { OPENCLAW_MSTEAMS_APP_ID: "app-id" } as RuntimeEnv,
      conversationStore,
      log: {
        info: vi.fn(), warn: vi.fn(), error: vi.fn(), debug: vi.fn(),
      } as unknown as MSTeamsMessageHandlerDeps["log"],
    };

    return { conversationStore, deps };
  }

  function makeActivity(overrides: Record<string, unknown> = {}) {
    return {
      id: "current-msg",
      type: "message",
      text: "Hey can you help me?",
      from: { id: "bob-bf-id", aadObjectId: "bob-aad", name: "Bob" },
      recipient: { id: "bot-id", name: "Bot" },
      conversation: { id: "19:channel@thread.tacv2", conversationType: "channel" },
      channelData: { team: { id: "team456", name: "Team" }, channel: { name: "General" } },
      replyToId: "parent-msg",
      attachments: [],
      ...overrides,
    };
  }

  // ── F2P: Non-allowlisted sender messages must be excluded ──
  it("excludes non-allowlisted sender messages from thread context in BodyForAgent", async () => {
    runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher.mockClear();
    graphThreadMock.resolveTeamGroupId.mockClear();
    graphThreadMock.fetchChannelMessage.mockReset();
    graphThreadMock.fetchThreadReplies.mockReset();

    // Parent message from a non-allowlisted user
    graphThreadMock.fetchChannelMessage.mockResolvedValue({
      id: "parent-msg",
      from: { user: { id: "eve-aad", displayName: "Eve" } },
      body: { content: "Injected payload from attacker", contentType: "text" },
    });
    // Replies: one from allowlisted user, one current message
    graphThreadMock.fetchThreadReplies.mockResolvedValue([
      {
        id: "bob-reply",
        from: { user: { id: "bob-aad", displayName: "Bob" } },
        body: { content: "Legitimate context from Bob", contentType: "text" },
      },
      {
        id: "current-msg",
        from: { user: { id: "bob-aad", displayName: "Bob" } },
        body: { content: "Hey can you help me?", contentType: "text" },
      },
    ]);

    const { deps } = makeDeps({
      channels: {
        msteams: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["bob-aad"],
          requireMention: false,
          teams: { team456: { channels: { "19:channel@thread.tacv2": { requireMention: false } } } },
        },
      },
    } as OpenClawConfig);

    const handler = createMSTeamsMessageHandler(deps);
    await handler({
      activity: makeActivity(),
      sendActivity: vi.fn(async () => undefined),
    } as unknown as Parameters<typeof handler>[0]);

    const dispatched = runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher.mock.calls[0]?.[0];
    expect(dispatched).toBeTruthy();
    const body = String((dispatched?.ctxPayload as { BodyForAgent?: string }).BodyForAgent ?? "");
    // Non-allowlisted user content must NOT appear
    expect(body).not.toContain("Eve");
    expect(body).not.toContain("Injected payload");
    // Allowlisted user content SHOULD appear
    expect(body).toContain("Bob");
    expect(body).toContain("Legitimate context");
    writeFileSync("/tmp/harbor_f2p_pass", "1");
  });

  // ── P2P: All-allowlisted senders' messages must still be included ──
  it("includes all messages when all senders are on the allowlist", async () => {
    runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher.mockClear();
    graphThreadMock.resolveTeamGroupId.mockClear();
    graphThreadMock.fetchChannelMessage.mockReset();
    graphThreadMock.fetchThreadReplies.mockReset();

    // Parent message from an allowlisted user
    graphThreadMock.fetchChannelMessage.mockResolvedValue({
      id: "parent-msg",
      from: { user: { id: "alice-aad", displayName: "Alice" } },
      body: { content: "Original question from Alice", contentType: "text" },
    });
    // Replies from allowlisted users
    graphThreadMock.fetchThreadReplies.mockResolvedValue([
      {
        id: "bob-reply",
        from: { user: { id: "bob-aad", displayName: "Bob" } },
        body: { content: "Reply from Bob with details", contentType: "text" },
      },
      {
        id: "current-msg",
        from: { user: { id: "bob-aad", displayName: "Bob" } },
        body: { content: "Follow-up from Bob", contentType: "text" },
      },
    ]);

    const { deps } = makeDeps({
      channels: {
        msteams: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["bob-aad", "alice-aad"],
          requireMention: false,
          teams: { team456: { channels: { "19:channel@thread.tacv2": { requireMention: false } } } },
        },
      },
    } as OpenClawConfig);

    const handler = createMSTeamsMessageHandler(deps);
    await handler({
      activity: makeActivity(),
      sendActivity: vi.fn(async () => undefined),
    } as unknown as Parameters<typeof handler>[0]);

    const dispatched = runtimeApiMock.dispatchReplyFromConfigWithSettledDispatcher.mock.calls[0]?.[0];
    expect(dispatched).toBeTruthy();
    const body = String((dispatched?.ctxPayload as { BodyForAgent?: string }).BodyForAgent ?? "");
    // All allowlisted users' content must appear
    expect(body).toContain("Alice");
    expect(body).toContain("Original question");
    expect(body).toContain("Bob");
    expect(body).toContain("Reply from Bob");
    writeFileSync("/tmp/harbor_p2p_pass", "1");
  });
});
VITEST_EOF

cd "$REPO"
npx vitest run extensions/msteams/src/monitor-handler/_harbor_thread_filter.test.ts --reporter=verbose 2>&1 | tee /tmp/vitest_harbor.log
rm -f "$REPO/extensions/msteams/src/monitor-handler/_harbor_thread_filter.test.ts"

# [pr_diff] (0.55): F2P — Non-allowlisted thread messages must not appear in BodyForAgent
if [ -f /tmp/harbor_f2p_pass ]; then
  pass 0.55 "Non-allowlisted messages excluded from thread context (F2P vitest)"
else
  fail 0.55 "Non-allowlisted messages NOT excluded from thread context (F2P vitest)"
  echo "--- vitest output ---"
  tail -40 /tmp/vitest_harbor.log 2>/dev/null || true
  echo "---"
fi

# [pr_diff] (0.15): P2P — All-allowlisted thread messages still included after fix
if [ -f /tmp/harbor_p2p_pass ]; then
  pass 0.15 "All-allowlisted messages still included in thread context (P2P vitest)"
else
  fail 0.15 "All-allowlisted messages incorrectly excluded (P2P vitest)"
fi

# ── Pass-to-pass: existing handler structure intact ──────────────────
# [pr_diff] (0.05): createMSTeamsMessageHandler export still exists
if grep -q 'export function createMSTeamsMessageHandler\|export.*createMSTeamsMessageHandler' "$HANDLER"; then
  pass 0.05 "createMSTeamsMessageHandler export still exists"
else
  fail 0.05 "createMSTeamsMessageHandler export is missing"
fi

# [pr_diff] (0.05): fetchChannelMessage + fetchThreadReplies still called
if grep -q 'fetchChannelMessage' "$HANDLER" && grep -q 'fetchThreadReplies' "$HANDLER"; then
  pass 0.05 "Thread history fetch calls still present"
else
  fail 0.05 "Thread history fetch calls missing"
fi

# [pr_diff] (0.05): formatThreadContext still called
if grep -q 'formatThreadContext' "$HANDLER"; then
  pass 0.05 "formatThreadContext call still present"
else
  fail 0.05 "formatThreadContext call missing"
fi

# ── Config-derived ───────────────────────────────────────────────────
# [agent_config] (0.05): "Never add @ts-nocheck" — CLAUDE.md:146 @ 7e08669
if grep -q '@ts-nocheck' "$HANDLER" 2>/dev/null; then
  fail 0.05 "File contains @ts-nocheck (violates CLAUDE.md:146)"
else
  pass 0.05 "No @ts-nocheck found"
fi

# [agent_config] (0.05): "Prefer strict typing; avoid any" — CLAUDE.md:144 @ 7e08669
if grep -Pq ':\s*any\b|as\s+any\b' "$HANDLER" 2>/dev/null; then
  # Only fail if 'any' was introduced in new/modified lines (not pre-existing)
  DIFF_ANY=$(cd "$REPO" && git diff HEAD -- extensions/msteams/src/monitor-handler/message-handler.ts 2>/dev/null | grep '^+' | grep -v '^+++' | grep -Pq ':\s*any\b|as\s+any\b' 2>/dev/null && echo "yes" || echo "no")
  if [ "$DIFF_ANY" = "yes" ]; then
    fail 0.05 "New code introduces explicit 'any' type (violates CLAUDE.md:144)"
  else
    pass 0.05 "No new explicit 'any' introduced"
  fi
else
  pass 0.05 "No explicit 'any' in handler"
fi

# ── Anti-stub: handler file was actually modified ────────────────────
# [pr_diff] (0.05): The handler must be modified from the base commit
if [ -n "$(cd "$REPO" && git diff HEAD -- extensions/msteams/src/monitor-handler/message-handler.ts 2>/dev/null)" ]; then
  pass 0.05 "Handler file has been modified from base commit"
else
  fail 0.05 "Handler file is unchanged from base commit"
fi

# ── Finalize ─────────────────────────────────────────────────────────
echo ""
echo "Deterministic score: ${REWARD} / 1.0 (before LLM rubric)"
echo "${REWARD}" > /logs/verifier/reward.txt

python3 -c "
import json
score = float('${REWARD}')
json.dump({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.70), 4),
    'regression': round(min(max(score - 0.70, 0), 0.15), 4),
    'config': round(min(max(score - 0.85, 0), 0.10), 4),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
print(json.dumps(json.load(open('/logs/verifier/reward.json')), indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
